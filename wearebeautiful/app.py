import os
from flask import Flask, render_template, flash, url_for, current_app, redirect
from flask_httpauth import HTTPBasicAuth
from flask_fontawesome import FontAwesome
from flask_static_digest import FlaskStaticDigest
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import generate_password_hash, check_password_hash
import config
import json
from wearebeautiful.db_model import db, DB_FILE
from wearebeautiful.auth import init_auth
from wearebeautiful.utils import static_url, url_for_screenshot_m, url_for_screenshot

STATIC_PATH = "/static"
STATIC_FOLDER = "../static"
TEMPLATE_FOLDER = "../template"

auth = init_auth()
flask_static_digest = FlaskStaticDigest()

app = Flask(__name__,
            static_url_path = STATIC_PATH,
            static_folder = STATIC_FOLDER, 
            template_folder = TEMPLATE_FOLDER)
app.secret_key = config.SECRET_KEY
app.config.from_object('config')
app.config['FONTAWESOME_SERVE_LOCAL'] = False

app.wsgi_app = ProxyFix(app.wsgi_app)

fa = FontAwesome(app)
flask_static_digest.init_app(app)

db_file = os.path.join(config.MODEL_DIR, DB_FILE)
print(db_file)
db.init(db_file)

from wearebeautiful.views.index import bp as index_bp
from wearebeautiful.views.model import bp as model_bp
from wearebeautiful.views.browse import bp as browse_bp
from wearebeautiful.views.docs import bp as docs_bp
app.register_blueprint(index_bp)
app.register_blueprint(model_bp, url_prefix='/model')
app.register_blueprint(browse_bp, url_prefix='/browse')
app.register_blueprint(docs_bp, url_prefix='/docs')


def static_url(filename):
    return config.STATIC_BASE_URL + "/static" + filename

def url_for_screenshot_m(model):
    return config.IMAGE_BASE_URL + "/model/m/%s/%s/%s-%s-%d-screenshot.jpg" % (model.model_id, model.code, model.model_id, model.code, model.version)

def url_for_screenshot(id, code, version):
    return config.IMAGE_BASE_URL + "/model/m/%s/%s/%s-%s-%d-screenshot.jpg" % (id, code, id, code, version)

app.jinja_env.globals.update(static_url=static_url)
app.jinja_env.globals.update(url_for_screenshot=url_for_screenshot)
app.jinja_env.globals.update(url_for_screenshot_m=url_for_screenshot_m)

@app.errorhandler(404)
def page_not_found(message):
    return render_template('errors/404.html', message=message), 404

@app.errorhandler(403)
def page_not_found(message):
    return render_template('errors/403.html', message=message), 403
