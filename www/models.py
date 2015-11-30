#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Models for user, project, chart.
'''

__author__ = 'TBBack'

import time, uuid

from orm import Model, StringField, BooleanField, FloatField, TextField, IntegerField

def next_id():
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)

class User(Model):
    __table__ = 'users'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    email = StringField(ddl='varchar(50)')
    passwd = StringField(ddl='varchar(50)')
    admin = BooleanField()
    name = StringField(ddl='varchar(50)')
    image = StringField(ddl='varchar(500)')
    created_at = FloatField(default=time.time)

class Project(Model):
    __table__ = 'projects'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_image = StringField(ddl='varchar(500)')
    title = StringField(ddl='varchar(50)')
    summary = StringField(ddl='varchar(200)')
    status = BooleanField()
    created_at = FloatField(default=time.time)

class Chart(Model):
    __table__ = 'charts'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    project_id = StringField(ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    index = IntegerField()
    status = BooleanField()
    created_at = FloatField(default=time.time)
    type = StringField(ddl='varchar(50)')
    option = TextField()
    description = TextField()