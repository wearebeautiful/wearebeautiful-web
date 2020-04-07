import os
from werkzeug.exceptions import NotFound
from flask import Flask, render_template, flash, url_for, current_app, redirect, Blueprint, request
from wearebeautiful.auth import _auth as auth
from wearebeautiful.db_model import DBModel
from wearebeautiful.utils import url_for_screenshot_m
import config

bp = Blueprint('index', __name__)


@bp.route('/')
def soon():
    return render_template("coming-soon.html", bare=True)


@bp.route('/index')
@auth.login_required
def index():
    models = DBModel.select(DBModel.model_id, DBModel.code, DBModel.body_part, DBModel.version) \
                    .order_by(DBModel.id.desc()) \
                    .limit(3)

    model_list = []
    for m in models:
        m.parse_data()
        model_list.append(m)

    slide_models_ids = [
        ("476551", "VLNN", 1),
        ("554268", "PLRN", 1),
        ("320912", "FSAN", 1),
        ("833579", "LSNN", 1)
    ]

    slide_models = []
    for slide in slide_models_ids:
        m = DBModel.get(DBModel.model_id == slide[0], DBModel.code == slide[1], DBModel.version == slide[2])
        m.parse_data()

        slide_models.append({
            "desc" : "%s model %s" % (m.body_part, m.display_code),
            "screenshot" : url_for_screenshot_m(m),
            "link" : "/model" + m.display_code
        })

    return render_template("index.html", slide_models=slide_models, recent_models=model_list)


@bp.route('/browse')
def browse():
    return redirect(url_for("model.browse_by_part"))


@bp.route('/team')
@auth.login_required
def team():
    return render_template("team.html")


@bp.route('/about')
@auth.login_required
def about():
    return render_template("about.html")


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

@bp.route('/privacy')
def privacy():
    return render_template("privacy.html")

@bp.route('/view')
@auth.login_required
def view():
    return redirect(url_for("model.browse_by_part"))

@bp.route('/view/<model>')
@auth.login_required
def view_model(model):
    return redirect(url_for("model.model", model=model))
