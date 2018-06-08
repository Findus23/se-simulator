#!/usr/bin/env python
import subprocess
import time
from io import BytesIO
from random import shuffle, randint

import sass
from PIL import ImageFont, Image, ImageDraw
from flask import render_template, send_from_directory, abort, session, jsonify, make_response, redirect, url_for, \
    request, send_file
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_session import Session
from playhouse.flask_utils import PaginatedQuery, get_object_or_404
from playhouse.shortcuts import model_to_dict
from sassutils.wsgi import SassMiddleware

import config
import utils
from app import app
from models import *

app.jinja_env.globals.update(prettydate=utils.prettydate)
app.jinja_env.globals.update(is_light_color=utils.is_light_color)

SESSION_TYPE = config.session_type
SESSION_COOKIE_SECURE = config.production
SESSION_USE_SIGNER = True
SESSION_KEY_PREFIX = "StackDataSessions:"
app.config.from_object(__name__)
app.secret_key = config.secret_key
Session(app)

limiter = Limiter(
    app,
    key_func=get_remote_address,
    headers_enabled=True
)

question_count = utils.load_question_count()


@app.context_processor
def git_hash():
    return dict(git_hash=subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode().strip())


@app.route("/")
@app.route("/s/<string:site>")
def index(site=None):
    query = Question.select(Question, User, Site, Title, SQL(utils.rating_sql)).join(Site).switch(Question).join(
        User).switch(
        Question).join(
        Title)
    if site:
        query = query.where(Site.url == site)
        site_element = Site.select().where(Site.url == site).get()
    else:
        site_element = utils.get_fallback_site()
    query = query.order_by(SQL("ci_lower_bound DESC, random"))
    # return jsonify(model_to_dict(query.get()))
    paginated_query = PaginatedQuery(query, paginate_by=10, check_bounds=True)
    pagearray = utils.create_pagination(paginated_query.get_page_count(), paginated_query.get_page())
    return render_template(
        "list.html",
        pagearray=pagearray,
        num_pages=paginated_query.get_page_count(),
        page=paginated_query.get_page(),
        questions=paginated_query.get_object_list(),
        site=site_element,
        voted=session["voted"] if "voted" in session and not config.make_cacheable else None,
        infohidden="hide" in request.cookies
    )


@app.route("/q/<string:slug>")
def question(slug):
    query = Question.select(Question, Title, User, Site) \
        .join(Title).switch(Question) \
        .join(User).switch(Question) \
        .join(Site).where(Title.slug == slug)
    question = get_object_or_404(query)
    answers = Answer.select(Answer, User, SQL(utils.rating_sql)) \
        .join(User).where(Answer.question == question) \
        .order_by(SQL("ci_lower_bound DESC"))
    return render_template(
        "detail.html",
        question=question,
        answers=answers,
        voted=session["voted"] if "voted" in session and not config.make_cacheable else None,
        infohidden="hide" in request.cookies
    )


@app.route("/quiz/")
def hello():
    return redirect(url_for("quiz", difficulty="easy"), code=302)


@app.route("/quiz/<string:difficulty>")
def quiz(difficulty):
    if difficulty not in ["easy", "hard"]:
        return abort(404)
    time1 = time.time()
    while True:
        random = randint(0, question_count - 1)
        print(random)
        try:
            question = Question.select(Question, Title, User, Site) \
                .join(Title).switch(Question) \
                .join(User).switch(Question) \
                .join(Site).where((Question.upvotes - Question.downvotes >= 0) & (Question.random == random)).get()
        except DoesNotExist:
            continue
        break

    if difficulty == "easy":
        sites = [question.site]
        query = Site.select().where((Site.last_download.is_null(False)) & (Site.id != question.site.id)) \
            .order_by(SQL("RAND()")).limit(3)
        for site in query:
            sites.append(site)
        shuffle(sites)
    else:
        sites = None
    time2 = time.time()
    print("{} ms".format((time2 - time1) * 1000.0))
    return render_template(
        "quiz.html",
        question=question,
        stats=session["quiz"][difficulty] if "quiz" in session else {"total": 0, "correct": 0},
        difficulty=difficulty,
        choices=sites,
        infohidden="hide" in request.cookies
    )


@app.route("/api/quiz/<int:id>/<string:guess>/<string:difficulty>", methods=["POST"])
def quiz_api(id, guess, difficulty):
    if difficulty not in ["easy", "hard"]:
        return abort(404)
    if "quiz" not in session:
        session["quiz"] = {"easy": {"total": 0, "correct": 0}, "hard": {"total": 0, "correct": 0}}
    session["quiz"][difficulty]["total"] += 1
    query = Question.select(Site).join(Site).where(Question.id == id).get()
    if guess == query.site.url:
        correct = True
        session["quiz"][difficulty]["correct"] += 1
    else:
        correct = False
    return jsonify({"site": model_to_dict(query)["site"], "correct": correct})


@app.route("/api/sites")
def sites():
    sites = Site.select().where(Site.last_download.is_null(False))
    data = {}
    for site in sites:
        data[site.url] = (model_to_dict(site))
    return jsonify(data)


@app.route("/image")
@app.route("/image/<int:site_id>")
@limiter.limit("10 per minute")
def image(site_id=None):
    if site_id:
        query = Site.select().where((Site.last_download.is_null(False)) & (Site.id == site_id))
        site = get_object_or_404(query)
    else:
        class DummySite(object):
            pass

        site = DummySite()
        site.foreground_color = "black"
        site.background_color = "white"
    # parameters
    text = "Stack Exchange\nSimulator"
    selected_font = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    font_size = 70
    W, H = (600, 600)
    # # get the size of the text
    img = Image.new("RGBA", (W, H), (site.background_color if site.background_color else "white"))
    font = ImageFont.truetype(selected_font, font_size)
    draw = ImageDraw.Draw(img)
    w, h = draw.multiline_textsize(text, font)

    draw.multiline_text(((W - w) / 2, (H - h) / 2), text,
                        font=font, align="center",
                        fill=(site.foreground_color if site.foreground_color else "black"))

    byte_io = BytesIO()
    img.save(byte_io, "PNG", optimize=True)
    byte_io.seek(0)
    return send_file(byte_io, mimetype="image/png")


@app.route("/api/vote/<string:type>/<int:id>/<string:vote>", methods=["POST"])
@limiter.limit("10 per minute")
def vote(type, id, vote):
    if "voted" not in session:
        session["voted"] = {}
    print(session["voted"])
    if (type, id) in session["voted"]:
        abort(403)
    if type == "question":
        if vote == "up":
            query = Question.update(upvotes=Question.upvotes + 1).where(Question.id == id)
        elif vote == "down":
            query = Question.update(downvotes=Question.downvotes + 1).where(Question.id == id)
        else:
            return abort(404)
    elif type == "answer":
        if vote == "up":
            query = Answer.update(upvotes=Answer.upvotes + 1).where(Answer.id == id)
        elif vote == "down":
            query = Answer.update(downvotes=Answer.downvotes + 1).where(Answer.id == id)
        else:
            return abort(404)
    else:
        return abort(404)
    session["voted"][(type, id)] = vote == "up"
    query.execute()
    if type == "question":
        query = Question.select(Question.upvotes, Question.downvotes).where(Question.id == id).get()
    else:
        query = Answer.select(Answer.upvotes, Answer.downvotes).where(Answer.id == id).get()
    return jsonify({
        "upvotes": query.upvotes,
        "downvotes": query.downvotes
    })


@app.errorhandler(429)
def ratelimit_handler(e):
    return make_response(jsonify(error="ratelimit exceeded {}".format(e.description)), 429)


@app.errorhandler(403)
def ratelimit_handler(e):
    return make_response(jsonify(error="access denied"), 403)


if __name__ == "__main__":
    import logging

    logger = logging.getLogger("peewee")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())


    @app.route("/static/js/<path:path>")
    def send_js(path):
        return send_from_directory("web/static/js", path)


    app.debug = True
    app.wsgi_app = SassMiddleware(app.wsgi_app, manifests={
        "web": ("static/sass", "static/css", "/static/css")
    })
    app.run()

else:
    css, sourcemap = sass.compile(
        filename="web/static/sass/style.scss",
        output_style="compressed",
        source_map_filename="web/static/css/style.css.map"
    )
    with open("web/static/css/style.css", "w") as style_css:
        style_css.write(css)
    with open("web/static/css/style.css.map", "w") as style_css_map:
        style_css_map.write(sourcemap)
