import os
from werkzeug.exceptions import NotFound
from flask import Flask, render_template, flash, url_for, current_app, redirect, Blueprint, request
from wearebeautiful.auth import _auth as auth
from wearebeautiful.db_model import DBModel
import config

bp = Blueprint('index', __name__)


@bp.route('/')
def index():
    if auth.username():
        return render_template("index.html")
    else:
        return redirect(url_for("index.soon"))


@bp.route('/browse')
def browse():
    return redirect(url_for("model.browse_by_part"))


@bp.route('/soon')
def soon():
    return render_template("coming-soon.html", bare=True)


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
