import os
import json
from shutil import copyfile, rmtree
import subprocess
from tempfile import mkdtemp
from wearebeautiful.db_model import DBModel
from wearebeautiful.utils import url_for_tagged_screenshot, url_for_screenshot
import config


MODEL_KIT_JSON = "template/exhibit/exhibits.json"


def make_kit_filename(slug):
    return os.path.join(config.KIT_DIR, "wearebeautiful-kit-%s.zip" % slug)


def make_model_kit(kit_data, force=False):

    zip_file_name = make_kit_filename(kit_data['slug'])
    if force and os.path.exists(zip_file_name):
        try:
            os.unlink(zip_file_name)
        except Exception:
            pass

    if os.path.exists(zip_file_name):
        print("  %s (cached)" % zip_file_name)
        return zip_file_name

    print("  %s" % zip_file_name)

    tmp_dir = mkdtemp()
    zip_files = []
    for model in kit_data['models']:
        model_code = model['model']
        try:
            id, code, version = model_code.split('-')
        except ValueError:
            raise ValueError("Invalid model code specified in model-kits.json.")
            
        solid_file = os.path.join(config.MODEL_DIR, "%s/%s/%s-solid.stl.gz" % (id, code, model_code))
        if not os.path.exists(solid_file):
            raise KeyError("Model file '%s' does not exist" % solid_file)
        dest_file = os.path.join(tmp_dir, "%s-solid.stl.gz" % model_code)
        copyfile(solid_file, dest_file)
        subprocess.run(['gunzip', dest_file])
        zip_files.append(dest_file[:-3])

    subprocess.run(['zip', '-q', zip_file_name, *zip_files])
    rmtree(tmp_dir)

    return zip_file_name


def load_kit_list():

    with open(MODEL_KIT_JSON, "r") as f:
        model_kits = json.loads(f.read())

    kits = []
    for i, kit in enumerate(model_kits):
        zip_file = make_kit_filename(kit['slug'])
        entry = kit
        entry['filename'] = zip_file

        models = []
        for model in kit['models']:
            id, code, version = model.split('-')
            m = {}
            m['model'] = model
            m['screenshot'] = url_for_screenshot(id, code, int(version))
            m['tagged_screenshot'] = url_for_tagged_screenshot(id, code, int(version))
            models.append(m)

        entry['models'] = models
        kits.append(entry)
            
    return kits


def prepare_kits(force):

    if not os.path.exists(config.KIT_DIR):
        try:
            os.mkdir(config.KIT_DIR)
        except IOError as err:
            print("Cannot create exhibit kits: ", str(err))
            sys.exit(-1)

    kits = load_kit_list()
    for kit in kits:
        make_model_kit(kit, force)
