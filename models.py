# -*- coding: utf-8 -*-

from peewee import BooleanField
from peewee import CharField
from peewee import DateTimeField
from peewee import ForeignKeyField
from peewee import IntegerField
from peewee import TextField

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
    background_color = CharField(max_length=7, null=True)
    foreground_color = CharField(max_length=7, null=True)
    primary_color = CharField(max_length=7, null=True)
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
    upvotes = IntegerField(default=1)
    downvotes = IntegerField(default=1)
    title = ForeignKeyField(Title)
    user = ForeignKeyField(User)
    site = ForeignKeyField(Site)
    datetime = DateTimeField()
    random = IntegerField(null=True)


class Answer(BaseModel):
    text = TextField()
    upvotes = IntegerField(default=1)
    downvotes = IntegerField(default=1)
    datetime = DateTimeField()
    question = ForeignKeyField(Question, null=True)
    user = ForeignKeyField(User)
    site = ForeignKeyField(Site)

