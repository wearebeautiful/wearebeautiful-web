import json
import os
from shutil import copyfile, rmtree
import subprocess
from tempfile import mkdtemp
from zipfile import ZipFile

from flask import Flask, render_template, Blueprint, send_file
from werkzeug.exceptions import NotFound
from wearebeautiful.auth import _auth as auth
import config


EDU_KIT_JSON = "docs/education-kits.json"

bp = Blueprint('docs', __name__)

@bp.route('/printing-guide')
@auth.login_required
def printing_guide():
    return render_template("docs/printing-guide.html")

@bp.route('/model-codes')
@auth.login_required
def model_codes():
    return render_template("docs/model-codes.html")

@bp.route('/faq')
@auth.login_required
def faq():
    return render_template("docs/faq.html")


def make_model_kit(kit_version, model_codes, force=False):

    zip_file_name = os.path.join(config.KIT_TMP_DIR, "wearebeautiful-kit-" + kit_version + ".zip")
    print(zip_file_name)
    if force and os.path.exists(zip_file_name):
        try:
            os.unlink(zip_file_name)
        except Exception:
            pass

    if os.path.exists(zip_file_name):
        return zip_file_name

    tmp_dir = mkdtemp()
    zip_files = []
    for model_code in model_codes:
        try:
            id, code, version = model_code.split('-')
        except ValueError:
            raise ValueError("Invalid model code specified in education-kits.json.")
            
        solid_file = os.path.join(config.MODEL_DIR, "%s/%s/%s-solid.stl.gz" % (id, code, model_code))
        if not os.path.exists(solid_file):
            raise KeyError("Model file '%s' does not exist" % solid_file)
        dest_file = os.path.join(tmp_dir, "%s-solid.stl.gz" % model_code)
        copyfile(solid_file, dest_file)
        subprocess.run(['gunzip', dest_file])
        zip_files.append(dest_file[:-3])

    subprocess.run(['zip', '-q', zip_file_name, *zip_files])
    rmtree(tmp_dir)

    print("created", zip_file_name)

    return zip_file_name

def prepare_kits():
    with open(EDU_KIT_JSON, "r") as f:
        edu_kits = json.loads(f.read())

    kits = []
    for i, kit in enumerate(edu_kits):
        zip_file = make_model_kit(kit['version'], kit['models'])
        entry = {}
        entry['filename'] = zip_file
        entry['version'] = kit['version']

        models = []
        for model in kit['models']:
            id, code, version = model.split('-')
            m = {}
            m['model'] = model
            m['screenshot'] = config.IMAGE_BASE_URL + "/model/m/%s/%s/%s-%s-%s-screenshot.jpg" % (id, code, id, code, version)
            models.append(m)

        entry['models'] = models
        kits.append(entry)
            
    return kits


@bp.route('/kit/<version>')
@auth.login_required
def send_model(version):
    filename = "wearebeautiful-kit-%s.zip" % version
    f = os.path.join(config.KIT_TMP_DIR, filename)
    if not os.path.exists(f):
        raise NotFound()

    return send_file(f, attachment_filename=filename, as_attachment=True)


@bp.route('/educational-kits')
@auth.login_required
def educational_kits():
    try:
        kits = prepare_kits()
    except (IOError, KeyError) as err:
        return render_template("docs/educational_kits.html", error=err)

    print(kits)
    return render_template("docs/educational_kits.html", kits=kits)
