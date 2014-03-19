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
