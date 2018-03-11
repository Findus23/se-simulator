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
    enabled=BooleanField(default=True)


class Alias(BaseModel):
    site = ForeignKeyField(Site)
    url = CharField(unique=True, max_length=50)
