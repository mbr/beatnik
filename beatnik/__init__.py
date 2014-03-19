import os

from flask import Blueprint, Flask
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


api = Blueprint('api', __name__)


@api.route('/user/<int:user_id>/')
def get_user(user_id):
    res = UserResource.from_id(user_id)

    return render_object_json(res)


@User.route(
    'users', methods=['GET'],
    )
def query_users(ctx):
    return '{!r}'.format(ctx)


@User.route(
    ['user', '/dump/'], methods=['GET'],
)
def dump_user(ctx):
    return '{!r}'.format(ctx)


def create_app(configfile=None):
    app = Flask(__name__)

    app.register_blueprint(api)
    Debug(app)
    hype.init_app(app)

    return app
