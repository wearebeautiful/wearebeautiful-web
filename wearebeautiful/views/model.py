import base64
import json
import gzip
import os
import random
from subprocess import run, CalledProcessError
import tempfile
from zipfile import ZipFile

from PIL import Image
from peewee import *
from operator import itemgetter
from werkzeug.exceptions import BadRequest, NotFound
from flask import Flask, render_template, flash, url_for, current_app, redirect, Blueprint, request, send_file, Response
from hurry.filesize import size, alternative
from wearebeautiful.auth import _auth as auth
from wearebeautiful.db_model import DBModel
import config

FONT_FILE = "admin/font/d-din-exp.ttf"
MAX_NUM_RELATED_MODELS = 3

bp = Blueprint('model', __name__)

@bp.route('/m/<path:filename>')
def send_model(filename):
    if current_app.debug and filename.endswith(".stl"):
        filename = os.path.join(current_app.config['MODEL_DIR'], filename + ".gz")
        if not os.path.exists(filename):
            raise NotFound()

        with gzip.open(filename, 'rb') as f:
            content = f.read()

        response = Response(content, status=200)
        response.headers['Content-Length'] = len(content)
        response.headers['Content-Type'] = 'model/stl'
        return response


    f = os.path.join(current_app.config['MODEL_DIR'], filename)
    if not os.path.exists(f):
        raise NotFound()

    return send_file(f)

@bp.route('/d/<path:filename>')
def download_model(filename):
    if filename.endswith(".stl"):
        filename += ".gz"
    if current_app.debug:
        filename = os.path.join(current_app.config['MODEL_DIR'], filename)
        if not os.path.exists(filename):
            raise NotFound()

        with gzip.open(filename, 'rb') as f:
            content = f.read()

        response = Response(content, status=200)
        response.headers['Content-Length'] = len(content)
        response.headers['Content-Type'] = 'model/stl'
        return response


    filename = os.path.join(current_app.config['MODEL_DIR'], filename)
    try:
        with open(filename, "rb") as f:
            content = f.read()

    except IOError as err:
        raise NotFound("STL file not found.")

    response = Response(content, status=200)
    response.headers['Content-Length'] = len(content)
    response.headers['Content-Type'] = 'model/stl'
    response.headers['Content-Encoding'] = 'gzip'
    return response



@bp.route('/model-diversity')
@auth.login_required
def diversity():
    return render_template("docs/model-diversity.html")


@bp.route('/')
@auth.login_required
def model_root():
    return render_template("error.html")


@bp.route('/statistics')
@auth.login_required
def statistics():
    model_stats = []
    for model in DBModel.select(DBModel.body_part, fn.COUNT(DBModel.id).alias('ct')).group_by(DBModel.body_part):
        if model.body_part == 'anatomical':
            continue

        model_stats.append((model.body_part, model.ct))
    model_stats = sorted(model_stats, key=itemgetter(1), reverse=True)
    total_models = DBModel.select().count()
    total_models -= 1  # remove the anatomical from the count

    with open("static/stats/aggregated_stats.json", "r") as j:
        jsdoc = j.read()

    stats = json.loads(jsdoc)

    ages = []
    for age in stats["ages"]:
        ages.append(( age, stats["ages"][age] ))

    countries = []
    for country in stats["countries"]:
        countries.append(( country, int(stats["countries"][country]) ))
    countries = sorted(countries, key=itemgetter(1), reverse=True)

    ethnicities = []
    for ethnicity in stats["ethnicities"]:
        ethnicities.append(( ethnicity, stats["ethnicities"][ethnicity] ))
    ethnicities = sorted(ethnicities, key=itemgetter(1), reverse=True)

    return render_template("docs/statistics.html", 
        model_stats=model_stats,
        total_models=total_models,
        ages=ages,
        countries=countries,
        ethnicities=ethnicities)


@bp.route('/<model>')
@auth.login_required
def model(model):
    return prepare_model(model, current_app.config["SUBMIT_SCREENSHOTS"])


@bp.route('/<model>/solid')
@auth.login_required
def model_solid(model):
    return prepare_model(model, current_app.config["SUBMIT_SCREENSHOTS"], True)


@bp.route('/<model>/screenshot')
@auth.login_required
def model_screenshot_get(model):
    return prepare_model(model, True)


@bp.route('/<id>-<code>-<int:version>/screenshot', methods = ['POST'])
@auth.login_required
def model_screenshot_post(id, code, version):
    if not config.SUBMIT_SCREENSHOTS:
        raise NotFound()

    fh, tmp_img = tempfile.mkstemp()
    os.close(fh)

    fh, tmp_img2 = tempfile.mkstemp()
    os.close(fh)

    fn = os.path.join(config.MODEL_DIR, id, code, "%s-%s-%d-screenshot.jpg" % (id, code, version))
    tagged = os.path.join(config.MODEL_DIR, id, code, "%s-%s-%d-screenshot-tagged.jpg" % (id, code, version))

    data = base64.b64decode(request.get_data()[23:])
    with open(tmp_img, "wb") as f:
        f.write(data)

    # TODO: Improve error handling here
    try:
        run(['convert',  
            tmp_img,
            "-resize", "800x800",
            fn], check=True)
    except CalledProcessError as err:
        print(err.output)

    if version > 1:
        model_code = "%s-%s-%s" % (id, code, version)
    else:
        model_code = "%s-%s" % (id, code)

    try:
        run(['convert',  
            fn,
            "-gravity", "north",
            "-background", "#F2ECE5",
            "-extent", "%dx%d" % (800, 850),
            tmp_img], check=True)
        run(['convert',  
            tmp_img,
            "-pointsize", "28", 
            "-font", FONT_FILE, 
            "-fill", "black", 
            "-gravity", "southwest",
            "-draw", 'text 10,12 "%s"' % (model_code), 
            tmp_img2], check=True)
        run(['convert',  
            tmp_img2,
            "static/img/watermark.png",
            "-gravity", "southeast",
            "-composite",
            tagged], check=True)
        os.unlink(tmp_img)
        os.unlink(tmp_img2)
    except CalledProcessError as err:
        print(err.output)

    return ""


def get_related_models(model):

    desc = ""
    models = DBModel.select(DBModel.model_id, DBModel.code, DBModel.body_part, DBModel.version) \
                    .where(DBModel.model_id == model.model_id, DBModel.code != model.code).limit(3)
    models = [ m for m in models ]

    if len(models):
        desc = "more models from the same person"
    if len(models) >= MAX_NUM_RELATED_MODELS:
        [ m.parse_data() for m in models ]
        return { "desc" : desc, "models" : models[0:MAX_NUM_RELATED_MODELS] }

    same_part_models = DBModel.select(DBModel.model_id, DBModel.code, DBModel.body_part, DBModel.version) \
                              .where(DBModel.body_part == model.body_part, DBModel.model_id != model.model_id)
    same_part_models = [ m for m in same_part_models ]
    random.shuffle(same_part_models)

    if len(same_part_models):
        if len(models):
            desc += " and "
        models.extend(same_part_models)

    desc += "more %s models" % model.body_part
    [ m.parse_data() for m in models ]
    return { "desc" : desc, "models" : models[0:MAX_NUM_RELATED_MODELS] }


def prepare_model(model, screenshot, solid = False):

    if model.isdigit() and len(model) == 6:
        models = DBModel.select().where(DBModel.model_id == model)
        model_list = [ ]
        for m in models:
            m.parse_data()
            model_list.append(m)

        if not model_list:
            raise NotFound("Model %s does not exist." % model)

        if len(model_list) == 1:
            return redirect(url_for("model.model", model=model_list[0].model_id + '-' + model_list[0].code))
        else:
            model_list = [ m for m in models ]
            return render_template("docs/model-disambig.html", model=model, model_list=model_list)

    try:
        parts = model.split('-')
        if len(parts) == 3:
            id, code, version = parts
        else:
            id, code = parts
            version = 1
    except ValueError as err:
        raise NotFound("Invalid model id/code.")

    model = DBModel.get(DBModel.model_id == id, DBModel.code == code, DBModel.version == version)
    if not model:
        raise NotFound("model %s does not exist." % model)

    model.parse_data()
    id = model.model_id
    code = model.code
    version = model.version
    model_file_med = config.STL_BASE_URL + "/model/m/%s/%s/%s-%s-%d-surface-med.stl" % (id, code, id, code, version)
    model_file_low = config.STL_BASE_URL + "/model/m/%s/%s/%s-%s-%d-surface-low.stl" % (id, code, id, code, version)
    model_file_solid= config.STL_BASE_URL + "/model/m/%s/%s/%s-%s-%d-solid.stl" % (id, code, id, code, version)

    solid_file = "%s-%s-%d-solid.stl" % (id, code, version)
    solid_path = "/%s/%s/%s" % (id, code, solid_file)
    surface_file = "%s-%s-%d-surface.stl" % (id, code, version)
    surface_path = "/%s/%s/%s" % (id, code, surface_file)

    solid_size = os.path.getsize(config.MODEL_DIR + solid_path + ".gz")
    surface_size = os.path.getsize(config.MODEL_DIR + surface_path + ".gz")

    downloads = {
        'solid' : (size(solid_size, system=alternative), config.STL_BASE_URL + "/model/d" + solid_path, solid_file),
        'surface' : (size(surface_size, system=alternative), config.STL_BASE_URL + "/model/d" + surface_path, surface_file)
    }

    return render_template("browse/view.html", 
        model = model, 
        model_file_med=model_file_med, 
        model_file_low=model_file_low, 
        model_file_solid=model_file_solid, 
        screenshot = int(screenshot),
        downloads = downloads,
        solid=(1 if solid else 0),
        related = get_related_models(model))
