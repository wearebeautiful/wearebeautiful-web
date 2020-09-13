import os
from werkzeug.exceptions import NotFound
from flask import render_template,  url_for, Blueprint, send_file
from wearebeautiful.auth import _auth as auth
from wearebeautiful.kits import load_kit_list


bp = Blueprint('exhibit', __name__)


@bp.route('/kit/<slug>')
@auth.login_required
def send_model(slug):
    filename = make_kit_filename(slug)
    if not os.path.exists(filename):
        raise NotFound()

    return send_file(filename, attachment_filename=filename, as_attachment=True)


@bp.route('/')
@auth.login_required
def index():
    kits = load_kit_list()
    return render_template("exhibit/index.html", kits=kits)
