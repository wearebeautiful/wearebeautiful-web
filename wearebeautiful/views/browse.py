import os
from operator import attrgetter
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
    tag_counts = {}
    last_id = ""
    model_list = []
    model_tags = []
    for model in DBModel.select().order_by(DBModel.model_id, DBModel.code):
        model.parse_data()
        model.common_tags_list = []

        if last_id and last_id != model.model_id:
            for tag in tag_counts:
                if len(model_list) == tag_counts[tag]:
                    model_tags.append(tag)
                    for m in model_list:
                        m.tags_list.remove(tag)

            for m in model_list:
                m.common_tags_list = model_tags

            model_list = []
            model_tags = []
            tag_counts = {}
            
        if not model.model_id in models:
            models[model.model_id] = []

        models[model.model_id].append(model)
      
        for tag in model.tags_list:
            try:
                tag_counts[tag] += 1
            except KeyError:
                tag_counts[tag] = 1

        last_id = model.model_id 
        model_list.append(model)



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
            if not tag:
                continue
            try:
                tags[tag].append(model)
            except KeyError:
                tags[tag] = [ model ]

        for event in model.history_list:
            if not event:
                continue
            try:
                events[event].append(model)
            except KeyError:
                events[event] = [ model ]

        if model.links:
            info['link'] = model

        if model.comment:
            info['comment'] = model

#    tags = sorted(tags, key=attrgetter('tag'))

    return render_template("browse/browse-by-history.html", 
        models=models, info=info, tags=tags, events=events)
