import os
import flask_testing
from flask import url_for
from werkzeug.exceptions import BadRequest, InternalServerError, NotFound

from wearebeautiful.app import app
from utils import ServerTestCase

class BrowseViewsTestCase(ServerTestCase):

    def setUp(self):
        ServerTestCase.setUp(self)

    def test_by_part(self):
        resp = self.client.get(url_for('browse.by_part'))
        self.assert200(resp)

    def test_by_model(self):
        resp = self.client.get(url_for('browse.by_model'))
        self.assert200(resp)

    def test_by_attributes(self):
        resp = self.client.get(url_for('browse.by_attributes'))
        self.assert200(resp)

    def test_illustrated_guide(self):
        resp = self.client.get(url_for('browse.illustrated_guide'))
        self.assert200(resp)
