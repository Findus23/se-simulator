from peewee import *

from basemodel import BaseModel


class Site(BaseModel):
    shortname = CharField(unique=True, max_length=30)
    url = CharField()
    name = CharField()
    icon_url = CharField()
    last_download = DateTimeField(null=True)
    tag_background_color = CharField(max_length=7)
    tag_foreground_color = CharField(max_length=7)
    link_color = CharField(max_length=7)
    enabled = BooleanField(default=True)


class Alias(BaseModel):
    site = ForeignKeyField(Site)
    url = CharField(unique=True, max_length=50)


class Title(BaseModel):
    text = CharField()
    slug = CharField()
    site = ForeignKeyField(Site)


class User(BaseModel):
    username = CharField()
    site = ForeignKeyField(Site)


class Question(BaseModel):
    text = TextField()
    upvotes = IntegerField(default=0)
    downvotes = IntegerField(default=0)
    title = ForeignKeyField(Title)
    user = ForeignKeyField(User)
    site = ForeignKeyField(Site)


class Answer(BaseModel):
    text = TextField()
    upvotes = IntegerField()
    downvotes = IntegerField()
    user = ForeignKeyField(User)
    site = ForeignKeyField(Site)
