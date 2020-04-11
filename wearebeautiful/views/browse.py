import os
from werkzeug.exceptions import BadRequest, NotFound
from flask import Flask, render_template, flash, url_for, current_app, redirect, Blueprint, request, send_file
from wearebeautiful.auth import _auth as auth
from wearebeautiful.db_model import DBModel
import config

bp = Blueprint('browse', __name__)


@bp.route('/by-part')
@auth.login_required
def browse_by_part():

    body_parts = DBModel.select(DBModel.body_part).distinct()
    body_parts = [ part.body_part for part in body_parts ]
    body_parts = sorted(body_parts, reverse=True)

    models = DBModel.select().order_by(DBModel.body_part)
    sections = {}
    for model in models:
        model.parse_data()
        if not model.body_part in sections:
            sections[model.body_part] = { 'name' : model.body_part, 'models' : [] }
        sections[model.body_part]['models'].append(model)

    return render_template("browse/browse-by-part.html", order = body_parts, sections = sections)


@bp.route('/by-model')
@auth.login_required
def browse_by_model():

    models = {}
    for model in DBModel.select().order_by(DBModel.model_id, DBModel.code):
        model.parse_data()
        if not model.model_id in models:
            models[model.model_id] = []

        models[model.model_id].append(model)

    model_list = sorted(models.keys())

    return render_template("browse/browse-by-model.html", models=models, model_list=model_list)


@bp.route('/by-history')
@auth.login_required
def browse_by_history():

    models = []
    for model in DBModel.select():
        model.parse_data()
        models.append(model)

    info = {}
    tags = {}
    events = {}
    for model in models:
        for tag in model.tags_list:
            try:
                tags[tag].append(model)
            except KeyError:
                tags[tag] = [ model ]

        for event in model.history_list:
            try:
                events[event].append(model)
            except KeyError:
                events[event] = [ model ]

        if model.links:
            info['link'] = model

        if model.comment:
            info['comment'] = model


    return render_template("browse/browse-by-history.html", 
        models=models, info=info, tags=tags, events=events)
