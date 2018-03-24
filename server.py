import sass
from flask import render_template, jsonify
from playhouse.flask_utils import PaginatedQuery, get_object_or_404
from playhouse.shortcuts import model_to_dict
from sassutils.wsgi import SassMiddleware

import utils
from app import app
from models import *

app.jinja_env.globals.update(prettydate=utils.prettydate)


@app.route('/')
def index():
    select = """
    *,
  ((upvotes + 1.9208) / (upvotes + downvotes) -
   1.96 * SQRT((upvotes * downvotes) / (upvotes + downvotes) + 0.9604) /
   (upvotes + downvotes)) / (1 + 3.8416 / (upvotes + downvotes))
    AS ci_lower_bound
    """
    query = Question.select(SQL(select)).order_by(SQL("ci_lower_bound DESC, random"))
    paginated_query = PaginatedQuery(query, paginate_by=10, check_bounds=True)
    pagearray = utils.create_pagination(paginated_query.get_page_count(), paginated_query.get_page())
    return render_template(
        'list.html',
        pagearray=pagearray,
        num_pages=paginated_query.get_page_count(),
        page=paginated_query.get_page(),
        questions=paginated_query.get_object_list()
    )


@app.route('/q/<string:slug>')
def question(slug):
    query = Question.select().join(Title).where(Title.slug == slug)
    question = get_object_or_404(query)
    return render_template(
        "detail.html",
        debug=model_to_dict(question),
        question=question
    )


if __name__ == '__main__':
    app.debug = True
    app.wsgi_app = SassMiddleware(app.wsgi_app, manifests={
        'web': ('static/sass', 'static/css', '/static/css')
    })
    app.run()
else:
    sass.compile(dirname=('web/static/sass', 'web/static/css'), output_style='compressed')
