from flask_hype import FlaskHype

import model
from hype.fields import Integer, String



hype = FlaskHype()


class User(hype.Resource):
    @classmethod
    def _obj_to_id(cls, obj):
        return obj.id

    @classmethod
    def _obj_from_id(cls, id):
        session = model.Session()
        obj = session.query(model.User).get(id)
        if not obj:
            raise LookupError('{} {} not found'.format(
              cls.__name__, id
            ))
        return obj

    id = Integer()
    name = String()

    def to_dict(self):
        # FIXME: this is a workaroundu
        return {
            'id': self.id,
            'name': self.name,
        }


class Playlist(hype.Resource):
    @classmethod
    def _obj_from_id(cls, id):
        # FIXME: this is broken atm, needs a solution that works with nesting
        import pdb
        pdb.set_trace()
        return int(id)


# routes
@User.route('users', methods=['GET'])
def query_users(ctx):
    session = model.Session()
    qry = session.query(model.User)
    limit = ctx.params['args'].get('limit')
    if limit:
        qry = qry.limit(int(limit))
    return qry.all()


@User.route(['user'], methods=['GET'])
def dump_user(ctx):
    return ctx.params['user']


@Playlist.route(['user', 'playlist'], methods=['GET'])
def dump_playlist(ctx):
    import pdb
    pdb.set_trace()
    return ''
