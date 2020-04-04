import base64
import os
import random
from werkzeug.exceptions import BadRequest, NotFound
from flask import Flask, render_template, flash, url_for, current_app, redirect, Blueprint, request, send_file
from hurry.filesize import size, alternative
from wearebeautiful.auth import _auth as auth
from wearebeautiful.db_model import DBModel
import config

MAX_NUM_RELATED_MODELS = 3

bp = Blueprint('model', __name__)

@bp.route('/m/<path:filename>')
def send_model(filename):
    return send_file(os.path.join(current_app.config['MODEL_DIR'], filename))


@bp.route('/by-part')
@auth.login_required
def browse_by_part():

    body_parts = DBModel.select(DBModel.body_part).distinct()
    body_parts = [ part.body_part for part in body_parts ]
    body_parts = sorted(body_parts, reverse=True)

    models = DBModel.select().order_by(DBModel.body_part)
    sections = {}
    for model in models:
        model.parse_data()
        if not model.body_part in sections:
            sections[model.body_part] = { 'name' : model.body_part, 'models' : [] }
        sections[model.body_part]['models'].append(model)

    return render_template("browse-by-part.html", order = body_parts, sections = sections)


@bp.route('/by-model')
@auth.login_required
def browse_by_model():

    models = {}
    for model in DBModel.select().order_by(DBModel.model_id, DBModel.code):
        model.parse_data()
        if not model.model_id in models:
            models[model.model_id] = []

        models[model.model_id].append(model)

    model_list = sorted(models.keys())

    return render_template("browse-by-model.html", models=models, model_list=model_list)


@bp.route('/model-diversity')
@auth.login_required
def diversity():
    return render_template("model-diversity.html")


@bp.route('/')
@auth.login_required
def model_root():
    flash('You need to provide a model id to view the model.')
    return render_template("error.html")


@bp.route('/statistics')
@auth.login_required
def statistics():
    return render_template("statistics.html")


@bp.route('/<model>')
@auth.login_required
def model(model):
    return prepare_model(model, current_app.config["SUBMIT_SCREENSHOTS"])

@bp.route('/<model>/screenshot')
@auth.login_required
def model_screenshot_get(model):
    return prepare_model(model, True)

@bp.route('/<model>/screenshot/<int:version>', methods = ['POST'])
@auth.login_required
def model_screenshot_post(model, version):
    if not config.SUBMIT_SCREENSHOTS:
        raise NotFound()

    id, code = model.split("-")

    data = base64.b64decode(request.get_data()[23:])
    fn = os.path.join(config.MODEL_DIR, id, code, "%s-%s-%d-screenshot.jpg" % (id, code, version))
    with open(fn, "wb") as f:
        f.write(data)

    fn = os.path.join(config.GIT_MODEL_DIR, id, code, "%s-%s-%d-screenshot.jpg" % (id, code, version))
    with open(fn, "wb") as f:
        f.write(data)

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


def prepare_model(model, screenshot):

    if model.isdigit() and len(model) == 6:
        models = DBModel.select(DBModel.model_id, DBModel.code).where(DBModel.model_id == model)
        model_list = [ "%s-%s" % (m.model_id, m.code) for m in models ]
        if not model_list:
            raise NotFound("Model %s does not exist." % model)

        if len(model_list) == 1:
            return redirect(url_for("index.view", model=model_list[0]))
        else:
            model_list = [ m for m in models ]
            return render_template("model-disambig.html", model=model, model_list=model_list)

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
    model_file = config.STL_BASE_URL + "/model/m/%s/%s/%s-%s-%d-surface-med.stl" % (id, code, id, code, version)

    solid_file = "%s-%s-%d-solid.stl" % (id, code, version)
    solid_path = "/%s/%s/%s" % (id, code, solid_file)
    surface_file = "%s-%s-%d-surface.stl" % (id, code, version)
    surface_path = "/%s/%s/%s" % (id, code, surface_file)

    if not current_app.debug:
        solid_path += ".gz"
        surface_path += ".gz"

    solid_size = os.path.getsize(config.MODEL_DIR + solid_path)
    surface_size = os.path.getsize(config.MODEL_DIR + surface_path)

    downloads = {
        'solid' : (size(solid_size, system=alternative), config.STL_BASE_URL + "/model/m" + solid_path, solid_file),
        'surface' : (size(surface_size, system=alternative), config.STL_BASE_URL + "/model/m" + surface_path, surface_file)
    }

    return render_template("view.html", 
        model = model, 
        model_file=model_file, 
        screenshot = int(screenshot),
        color_1 = "9A1085", color_2 = "e8a11e", color_3 = "57ab6d",
        downloads = downloads,
        related = get_related_models(model))
