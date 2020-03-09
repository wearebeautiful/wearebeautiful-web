import base64
import os
from werkzeug.exceptions import BadRequest
from flask import Flask, render_template, flash, url_for, current_app, redirect, Blueprint, request, send_file
from wearebeautiful.auth import _auth as auth
from wearebeautiful.db_model import DBModel
import config

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
    return prepare_model(model, current_app.config["SEND_SNAPSHOTS"])

@bp.route('/<model>/screenshot', methods = ['GET', 'POST'])
@auth.login_required
def model_screenshot_get(model):

    if request.method == 'GET':
        return prepare_model(model, True)

    try:
        os.mkdir("screenshot")
    except OSError:
        pass

    data = base64.b64decode(request.get_data()[23:])
    fn = os.path.join("screenshot", "%s.jpg" % model)
    with open(fn, "wb") as f:
        f.write(data)

    return ""


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
        id, code = model.split('-')
    except ValueError as err:
        raise NotFound("Invalid model id/code.")

    model = DBModel.get(DBModel.model_id == id, DBModel.code == code)
    if not model:
        raise NotFound("model %s does not exist." % model)

    model.parse_data()
    id = model.model_id
    code = model.code
    processed = "%d-%02d-%02d" % (model.processed.year, model.processed.month, model.processed.day)
    model_file = config.STL_BASE_URL + "/model/m/%s/%s-%s/%s-%s-%s-surface-low.stl" % (id, id, code, id, code, processed)

    return render_template("view.html", model = model, model_file=model_file, screenshot = int(screenshot),
        color_1 = "9A1085", color_2 = "e8a11e", color_3 = "57ab6d")
