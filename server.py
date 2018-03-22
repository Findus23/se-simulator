from datetime import datetime

from flask import render_template, flash
from playhouse.shortcuts import model_to_dict
from sassutils.wsgi import SassMiddleware

import utils
from app import app
from models import *

app.jinja_env.globals.update(prettydate=utils.prettydate)

def query_to_response(query, limit=10, key=False, sort=False, offset=None, list=None, **kwargs):
    """

    :param sort: boolean
    :param offset: int
    :type key: str
    :type limit: int|boolean
    :param **kwargs
    :type query: peewee.ModelSelect
    """
    if limit:
        query = query.limit(limit)
    print(query.sql())
    data = {} if key is not False else []
    order = int(offset) if offset else 0
    for i in query:
        element = model_to_dict(i, **kwargs)
        if list:
            element = element[list]
        if sort:
            element["order"] = order
            order += 1
        if key is not False:
            if "." in key:
                key1, key2 = key.split(".")
                data[getattr(getattr(i, key1), key2)] = element
            else:
                data[getattr(i, key)] = element
        else:
            data.append(element)
    return data


@app.route('/')
def index():
    query = Question.select().limit(10)
    # return query_to_response(Question.select().limit(10), limit=False, max_depth=1)
    # return query_to_response(query, max_depth=1)
    return render_template('list.html', questions=query_to_response(query, max_depth=1))


@app.route('/q/<string:slug>')
def question(slug):
    # query = Question.select().limit(10)
    # return query_to_response(Question.select().limit(10), limit=False, max_depth=1)
    # return query_to_response(query, max_depth=1)
    return render_template("detail.html", question=slug)
    # return render_template('list.html', questions=query_to_response(query, max_depth=1))


if __name__ == '__main__':
    app.debug = True
    app.wsgi_app = SassMiddleware(app.wsgi_app, manifests={
        'web': ('static/sass', 'static/css', '/static/css')
    })
    app.run()
