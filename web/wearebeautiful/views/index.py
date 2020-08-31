import os
import json
from peewee import *
from werkzeug.exceptions import NotFound
from flask import Flask, render_template, flash, url_for, current_app, redirect, Blueprint, request
from wearebeautiful.auth import _auth as auth
from wearebeautiful.db_model import DBModel
from wearebeautiful.utils import url_for_screenshot_m
import config

bp = Blueprint('index', __name__)


@bp.route('/')
def soon():
    return render_template("about/coming-soon.html", bare=True)

def load_slide_models(slide_model_ids):
    slide_models = []
    for slide in slide_model_ids:
        m = DBModel.get(DBModel.model_id == slide[0], DBModel.code == slide[1], DBModel.version == slide[2])
        m.parse_data()

        slide_models.append({
            "desc" : "%s model %s" % (m.body_part, m.display_code),
            "screenshot" : url_for_screenshot_m(m),
            "link" : "/model/" + m.display_code
        })

    return slide_models

@bp.route('/index')
@auth.login_required
def index():
    model_count = DBModel.select().count()
    models = DBModel.select(DBModel.model_id, DBModel.code, DBModel.body_part, DBModel.version) \
                    .order_by(DBModel.id.desc()) \
                    .limit(3)

    with open("static/stats/aggregated_stats.json", "r") as j:
        stats = json.loads(j.read())

    min_age = 1000
    max_age = 18
    for age in stats["ages"]:
        age = int(age)
        min_age = age if age < min_age else min_age
        max_age = age if age > max_age else max_age

    model_list = []
    for m in models:
        m.parse_data()
        model_list.append(m)

    sample_model_ids = [
        ("476551", "VLNN", 1),
        ("554268", "PLRN", 1),
        ("320912", "FSAN", 1),
        ("833579", "LSNN", 1)
    ]
    sample_models = load_slide_models(sample_model_ids)

    picks_model_ids = [
        ("591522", "FSAN", 1),
        ("591522", "FSAN", 2),
        ("591522", "FSAN", 4),
        ("591522", "FSAN", 5),
    ]
    picks_models = load_slide_models(picks_model_ids)

    return render_template("index.html", 
        sample_models=sample_models, 
        picks_models=picks_models, 
        recent_models=model_list, 
        model_count=model_count,
        min_age=min_age,
        max_age=max_age)


@bp.route('/browse')
@auth.login_required
def browse():
    return redirect(url_for("browse.by_part"))


@bp.route('/team')
@auth.login_required
def team():
    return render_template("about/team.html")


@bp.route('/about')
@auth.login_required
def about():
    return render_template("about/about.html")


@bp.route('/company')
@auth.login_required
def company():
    return render_template("about/company.html")

@bp.route('/contact')
@auth.login_required
def contact():
    return render_template("about/contact.html")

@bp.route('/support')
def support():
    return render_template("support/support.html")

@bp.route('/support/success')
def support_success():
    return render_template("support/support-success.html")

@bp.route('/support/cancel')
def support_cancel():
    return render_template("support/support-cancel.html")

@bp.route('/donate')
def donate():
    return redirect(url_for("index.support"))

@bp.route('/privacy')
@auth.login_required
def privacy():
    return render_template("about/privacy.html")
