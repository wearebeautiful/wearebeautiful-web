from flask import Flask, render_template, Blueprint
from wearebeautiful.auth import _auth as auth
import config

bp = Blueprint('docs', __name__)

@bp.route('/printing-guide')
@auth.login_required
def printing_guide():
    return render_template("docs/printing-guide.html")

@bp.route('/our-data')
@auth.login_required
def our_data():
    return render_template("docs/our-data.html")

@bp.route('/faq')
@auth.login_required
def faq():
    return render_template("docs/faq.html")

@bp.route('/guide')
@auth.login_required
def visual_guide():
    return render_template("docs/visual-guide.html")
