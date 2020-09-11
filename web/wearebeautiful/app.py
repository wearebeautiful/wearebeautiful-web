import json
import os
import sys

from flask import Flask, render_template, flash, url_for, current_app, redirect
from flask_httpauth import HTTPBasicAuth
from flask_static_digest import FlaskStaticDigest
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import generate_password_hash, check_password_hash

from wearebeautiful.db_model import db, DB_FILE
from wearebeautiful.auth import init_auth
import wearebeautiful.utils as utils
import config


STATIC_FOLDER = "../static"
TEMPLATE_FOLDER = "../template"

auth = init_auth()
flask_static_digest = FlaskStaticDigest()

app = Flask(__name__,
            static_folder = STATIC_FOLDER, 
            template_folder = TEMPLATE_FOLDER)
app.secret_key = config.SECRET_KEY
app.config.from_object('config')
app.config['FONTAWESOME_SERVE_LOCAL'] = False
app.config['FLASK_STATIC_DIGEST'] = flask_static_digest

app.wsgi_app = ProxyFix(app.wsgi_app)

flask_static_digest.init_app(app)

db_file = os.path.join(config.MODEL_DIR, DB_FILE)
if not os.path.exists(db_file):
    print("WARNING: Cannot find models db: %s" % db_file)

db.init(db_file)

from wearebeautiful.views.index import bp as index_bp
from wearebeautiful.views.model import bp as model_bp
from wearebeautiful.views.browse import bp as browse_bp
from wearebeautiful.views.docs import bp as docs_bp
app.register_blueprint(index_bp)
app.register_blueprint(model_bp, url_prefix='/model')
app.register_blueprint(browse_bp, url_prefix='/browse')
app.register_blueprint(docs_bp, url_prefix='/docs')

app.jinja_env.globals.update(static_url=utils.static_url)
app.jinja_env.globals.update(url_for_screenshot=utils.url_for_screenshot)
app.jinja_env.globals.update(url_for_screenshot_m=utils.url_for_screenshot_m)
app.jinja_env.globals.update(url_for_tagged_screenshot=utils.url_for_tagged_screenshot)
app.jinja_env.globals.update(url_for_tagged_screenshot_m=utils.url_for_tagged_screenshot_m)

@app.errorhandler(404)
def page_not_found(message):
    return render_template('errors/404.html', message=message), 404

@app.errorhandler(403)
def page_not_found(message):
    return render_template('errors/403.html', message=message), 403
