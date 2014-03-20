import os

from flask import Flask, make_response
from flask.ext.arrest import RestBlueprint
from flask.ext.arrest.json import json_enc
from sqlalchemy import create_engine

from flask_debug import Debug
from model import create_fixtures, Session
from model import Base
from resources import User, hype


api = RestBlueprint('api', __name__)
api.outgoing.add_mimetype('application/beatnik+json')


@api.content_renderer.renders('application/beatnik+json')
def render_beatnik_json(data, mimetype):
    # FIXME: for now, we do not have a cleaned up replacement for the
    # rendering capabilities of hype yet
    #
    # Currently, the model objects seem to be in need of being registered
    # with hype, which seems slightly questionable?
    #
    # FIXME: Hack for now - just dump some json directly from the model
    buf = json_enc.encode(data)
    response = make_response(buf)
    response.headers['Content-Type'] = 'application/beatnik+json'
    return response


def create_app(configfile=None):
    # we do something silly here
    dbpath = '/tmp/devdb'
    if os.path.exists(dbpath):
        os.unlink(dbpath)
    engine = create_engine('sqlite:///' + dbpath, echo=False)

    # create db structure
    Base.metadata.create_all(bind=engine)
    Session.configure(bind=engine)

    # create some sample data
    session = Session()
    create_fixtures(session)
    session.commit()

    # create app
    app = Flask(__name__)

    hype.init_blueprint(api)
    app.register_blueprint(api, url_prefix='/api')
    Debug(app)

    return app
