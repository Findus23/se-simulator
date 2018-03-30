import random
from datetime import datetime

import sys
from slugify import slugify

import utils
from models import *
from text_generator import get_chain, generate_text


def get_unused_users(site, count):
    return User.select().join(Question, JOIN.LEFT_OUTER).switch(User).join(Answer, JOIN.LEFT_OUTER) \
        .where((User.site == site) & (Question.id.is_null()) & (Answer.id.is_null()))


def add_username(site, count=500):
    chain = get_chain(site.url, "Usernames")
    for _ in range(count):
        username = generate_text(chain, "Usernames")
        User.create(username=username, site=site)


def add_title(site, count=100):
    # TODO: Make sure that every slug is unique
    chain = get_chain(site.url, "Titles")
    for _ in range(count):
        title = generate_text(chain, "Titles")
        slug = slugify(title, max_length=70, word_boundary=True)
        Title.create(text=title, slug=slug, site=site)


def add_answer(site, count=300):
    users = get_unused_users(site, count)
    chain = get_chain(site.url, "Answers")

    for i in range(count):
        text = generate_text(chain, "Answers")
        user = users[i]
        time = datetime.now()
        Answer.create(text=text, user_id=user, site_id=site, datetime=time)


def add_question(site, count=100):
    users = get_unused_users(site, count)
    titles = Title.select().join(Question, JOIN.LEFT_OUTER) \
        .where((Title.site == site) & (Question.id.is_null())) \
        .limit(count)
    chain = get_chain(site.url, "Questions")

    for i in range(count):
        text = generate_text(chain, "Questions")
        title = titles[i]
        user = users[i]
        time = datetime.now()
        question = Question.create(text=text, title_id=title, user_id=user, site_id=site, datetime=time,
                                   random=utils.rand())
        num_answers = random.randint(1, 4)
        answers = Answer.select().where((Answer.site == site) & (Answer.question.is_null())).limit(num_answers)
        for answer in answers:
            answer.question = question
            answer.save()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        sites = sys.argv[1:]
        query = Site.select().where((Site.last_download.is_null(False)) & (Site.url.in_(sites)))
    else:
        query = Site.select().where(Site.last_download.is_null(False))
    for s in query:
        add_username(s)
        add_title(s)
        add_answer(s)
        add_question(s)
