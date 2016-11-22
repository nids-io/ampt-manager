'''AMPT manager database routines'''

import os.path
from peewee import *
from flask import Flask
from playhouse.flask_utils import FlaskDB

from .models import *
from ..web import app
from ..web.crypt import bcrypt
from .. import settings


MODEL_LIST = [ProbeGenerator, EventMonitor, MonitoredSegment, ReceivedProbeLog,
              GeneratedProbeLog, User]

def get_generator_choices():
    '''
    Produce list of tuples of Probe Generator objects suitable for use as
    the `choices` attribute on the Monitored Segment form

    '''
    return (ProbeGenerator.select(ProbeGenerator.id, ProbeGenerator.name)
                          .order_by(ProbeGenerator.name)
                          .tuples())

def get_random_admin_pass(n):
    '''
    Return random alphanumeric string of length `n` for default admin
    account password

    '''
    return ''.join(random.SystemRandom().choice(
        string.ascii_letters + string.digits) for _ in range(n))

def initialize_database(args, admin_user, admin_pw):
    '''
    Initialize ampt_manager database.

    Create initial database tables from model definitions. This is used during
    creation of new app instance/config.

    '''
    ampt_db = SqliteDatabase(app.config['DATABASE'])
    database = FlaskDB(app, ampt_db)

    # Create tables from peewee models
    for model in MODEL_LIST:
        # If told to force initialization, drop existing tables. Fail silently
        # if force option specified but no tables exist.
        if args.force:
            model.drop_table(fail_silently=True)
        model.create_table()

    # Create default admin user
    pw_hash = bcrypt.generate_password_hash(admin_pw)
    initial_user = User()
    initial_user.username=admin_user
    initial_user.display_name='Admin User'
    initial_user.password=pw_hash
    initial_user.email='root@localhost'
    initial_user.save()

    # Create local probe generator
    ProbeGenerator.create(name='Local',
                          address='localhost',
                          port=settings.probe_generator_default_port,
                          active=False,
                          created_by=initial_user,
                          last_modified_by=initial_user)

