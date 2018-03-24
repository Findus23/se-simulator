from datetime import datetime

from slugify import slugify

import utils
from models import *
from text_generator import get_chain, generate_text


def add_username(site, count=100):
    """

    :type site: Site
    """
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


def add_question(site, count=100):
    users = User.select().where(User.site == site).limit(count)
    titles = Title.select().where(Title.site == site).limit(count)
    chain = get_chain(site.url, "Questions")

    for i in range(count):
        text = generate_text(chain, "Questions")
        title = titles[i]
        print(title.text)
        user = users[i]
        print(user.username)
        time = datetime.now()
        Question.create(text=text, title_id=title, user_id=user, site_id=site, datetime=time, random=utils.rand())


if __name__ == "__main__":
    query = Site.select().where(Site.last_download.is_null(False))
    for s in query:
        add_username(s)
        add_title(s)
        add_question(s)
