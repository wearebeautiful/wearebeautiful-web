import os
from flask import Flask, render_template, flash, url_for, current_app, redirect
from flask_httpauth import HTTPBasicAuth
from flask_fontawesome import FontAwesome
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bootstrap import Bootstrap
import config
import json
from wearebeautiful.db_model import db
from wearebeautiful.auth import init_auth


STATIC_PATH = "/static"
STATIC_FOLDER = "../static"
TEMPLATE_FOLDER = "../template"

auth = init_auth()

app = Flask(__name__,
            static_url_path = STATIC_PATH,
            static_folder = STATIC_FOLDER, 
            template_folder = TEMPLATE_FOLDER)
app.secret_key = config.SECRET_KEY
app.config.from_object('config')

app.wsgi_app = ProxyFix(app.wsgi_app)

Bootstrap(app)
fa = FontAwesome(app)

db.init(os.path.join(config.MODEL_DIR, "wab-models.db"))

from wearebeautiful.views.index import bp as index_bp
from wearebeautiful.views.model import bp as model_bp
app.register_blueprint(index_bp)
app.register_blueprint(model_bp, url_prefix='/model')

def static_url(filename):
    o = config.STATIC_BASE_URL + filename
    print(o)
    return o

app.jinja_env.globals.update(static_url=static_url)

@app.errorhandler(404)
def page_not_found(message):
    return render_template('errors/404.html', message=message), 404

@app.errorhandler(403)
def page_not_found(message):
    return render_template('errors/403.html', message=message), 403
