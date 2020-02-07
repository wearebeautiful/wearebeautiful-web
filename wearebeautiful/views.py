from werkzeug.exceptions import NotFound
from flask import Flask, render_template, flash, url_for, current_app, redirect, Blueprint, request, send_from_directory
from wearebeautiful.auth import _auth as auth
from wearebeautiful.db_model import DBModel
import config

bp = Blueprint('index', __name__)

@bp.route('/model/<path:filename>')
def model(filename):
    return send_from_directory(current_app.config['MODEL_ARCHIVE'], filename)


@bp.route('/')
def index():
    if auth.username():
        return render_template("index.html")
    else:
        return redirect(url_for("index.soon"))


@bp.route('/soon')
def soon():
    return render_template("coming-soon.html", bare=True)


@bp.route('/browse')
@auth.login_required
def browse():

    body_parts = DBModel.select(DBModel.body_part).distinct()
    body_parts = [ part.body_part for part in body_parts ]
    body_parts = sorted(body_parts, reverse=True)

    models = DBModel.select().order_by(DBModel.body_part)
    sections = {}
    for model in models:
        if not model.body_part in sections:
            sections[model.body_part] = { 'name' : model.body_part, 'models' : [] }
        sections[model.body_part]['models'].append(model)

    return render_template("browse.html", order = body_parts, sections = sections)


@bp.route('/team')
@auth.login_required
def team():
    return render_template("team.html")


@bp.route('/about')
@auth.login_required
def about():
    return render_template("about.html")


@bp.route('/view/')
@auth.login_required
def view_root():
    flash('You need to provide a model id to view.')
    return render_template("error.html")


@bp.route('/view')
@auth.login_required
def view_simple():
    return redirect(url_for("index.browse"))

@bp.route('/statistics')
@auth.login_required
def statistics():
    return render_template("statistics.html")

@bp.route('/view/<model>')
@auth.login_required
def view(model):
    if model == '-':
        return render_template("view.html", manifest = {'id':''})

    if model.isdigit() and len(model) == 6:
        models = DBModel.select(DBModel.model_id, DBModel.code).where(DBModel.model_id == model)
        model_list = [ "%s-%s" % (m.model_id, m.code) for m in models ]
        if not model_list:
            raise NotFound("Model %s does not exist." % model)

        if len(model_list) == 1:
            return redirect(url_for("index.view", model=model_list[0]))
        else:
            model_list = [ m for m in models ]
            print(model_list)
            return render_template("model-disambig.html", model=model, model_list=model_list)

    try:
        id, code = model.split('-')
    except ValueError as err:
        raise NotFound("Invalid model id/code.")

    model = DBModel.get(DBModel.model_id == id, DBModel.code == code)
    if not model:
        raise NotFound("model %s does not exist." % model)

    id = model.model_id
    code = model.code
    processed = "%d-%02d-%02d" % (model.processed.year, model.processed.month, model.processed.day)
    model_file = "/model/%s/%s-%s/%s-%s-%s-surface-med.stl" % (id, id, code, id, code, processed)

    return render_template("view.html", model = model, model_file=model_file)

    
@bp.route('/company')
def company():
    return render_template("company.html")

@bp.route('/contact')
def contact():
    return render_template("contact.html")

@bp.route('/support')
def support():
    return render_template("support.html")

@bp.route('/support/success')
def support_success():
    return render_template("support-success.html")

@bp.route('/support/cancel')
def support_cancel():
    return render_template("support-cancel.html")

@bp.route('/donate')
def donate():
    return redirect(url_for("index.support"))
