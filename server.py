import sass
from flask import render_template, send_from_directory, abort, session, jsonify, make_response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from playhouse.flask_utils import PaginatedQuery, get_object_or_404
from playhouse.shortcuts import model_to_dict
from sassutils.wsgi import SassMiddleware

import config
import utils
from app import app
from models import *

app.jinja_env.globals.update(prettydate=utils.prettydate)

app.secret_key = config.secret_key

limiter = Limiter(
    app,
    key_func=get_remote_address,
    headers_enabled=True
)
import logging

logger = logging.getLogger('peewee')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


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
    answers = Answer.select().where(Answer.question == question) # TODO: Sort by score
    return render_template(
        "detail.html",
        debug=model_to_dict(question),
        question=question,
        answers=answers
    )


@app.route('/test')
def sdfdsfds():
    user = User.select().get()

    return jsonify(
        model_to_dict(Answer.select().where((Answer.question.is_null())).get()))


@app.route('/api/vote/<int:id>/<string:type>', methods=["POST"])
@limiter.limit("10 per minute")
def vote(id, type):
    if "voted" not in session:
        voted = []
    else:
        voted = session["voted"]
    print(voted)
    if id in voted:
        abort(403)
    if type == "up":
        query = Question.update(upvotes=Question.upvotes + 1).where(Question.id == id)
    elif type == "down":
        query = Question.update(downvotes=Question.downvotes + 1).where(Question.id == id)
    else:
        return abort(404)
    voted.append(id)
    session["voted"] = voted
    query.execute()
    query = Question.select(Question.upvotes, Question.downvotes).where(Question.id == id).get()

    return jsonify({
        "upvotes": query.upvotes,
        "downvotes": query.downvotes
    })


@app.errorhandler(429)
def ratelimit_handler(e):
    return make_response(
        jsonify(error="ratelimit exceeded {}".format(e.description))
        , 429
    )


@app.errorhandler(403)
def ratelimit_handler(e):
    return make_response(
        jsonify(error="access denied")
        , 403
    )


if __name__ == '__main__':
    @app.route('/static/js/<path:path>')
    def send_js(path):
        return send_from_directory('web/static/js', path)


    app.debug = True
    app.wsgi_app = SassMiddleware(app.wsgi_app, manifests={
        'web': ('static/sass', 'static/css', '/static/css')
    })
    app.run()

else:
    sass.compile(dirname=('web/static/sass', 'web/static/css'), output_style='compressed')
