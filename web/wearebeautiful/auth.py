import json 
import os

from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import config

_auth = None
users = {
    config.SITE_USERNAME :  generate_password_hash(config.SITE_PASSWORD),
}

with open(os.path.join(config.MODEL_DIR, "wab-passwds.json"), "r") as f:
    passwds = json.loads(f.read())

for user, passwd in passwds:
    users[user] = generate_password_hash(passwd)

def init_auth():
    global _auth

    _auth = HTTPBasicAuth()

    @_auth.verify_password
    def verify_password(username, password):

        if not config.USE_SITE_AUTH:
            return True

        if username in users:
            return check_password_hash(users.get(username), password)
        return False

    return _auth
