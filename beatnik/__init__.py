import os

from flask import Blueprint, Flask
from flask.ext.arrest import RestBlueprint
from flask.ext.arrest.helpers import serialize_response
from sqlalchemy import create_engine

from flask_debug import Debug
from model import create_fixtures, Session
from model import Base


def logging_url_for(*args, **kwargs):
    print 'URL_FOR_CALLED'
    print args
    print kwargs
    return None


def render_object_json(obj):
    from hype.mime.application_json import serialize

    return serialize(obj, logging_url_for)


# database setup
from resources import User, hype


dbpath = '/tmp/devdb'
if os.path.exists(dbpath):
    os.unlink(dbpath)

engine = create_engine('sqlite:///' + dbpath, echo=True)
Base.metadata.create_all(bind=engine)
Session.configure(bind=engine)

# create some sample data
session = Session()
create_fixtures(session)
session.commit()


api = RestBlueprint('api', __name__)
api.outgoing.add_mimetype('application/beatnik+json')


@api.route('/')
def index():
    return serialize_response({'hello': 'world'})


def create_app(configfile=None):
    app = Flask(__name__)

    hype.init_blueprint(api)
    app.register_blueprint(api, url_prefix='/api')
    Debug(app)

    return app
