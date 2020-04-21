import os
import flask_testing
from flask import url_for
from werkzeug.exceptions import BadRequest, InternalServerError, NotFound

from wearebeautiful.app import app
from utils import ServerTestCase

class DocsViewsTestCase(ServerTestCase):

    def setUp(self):
        ServerTestCase.setUp(self)

    def test_printing_guide(self):
        resp = self.client.get(url_for('docs.printing_guide'))
        self.assert200(resp)

    def test_our_data(self):
        resp = self.client.get(url_for('docs.our_data'))
        self.assert200(resp)

    def test_faq(self):
        resp = self.client.get(url_for('docs.faq'))
        self.assert200(resp)
