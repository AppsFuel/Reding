from flask import request
from flask.ext.restful import reqparse, marshal_with, abort
from flask.ext import restful
from reding.errors import DoesNotExists
from reding.models import RatingModel, ObjModel, ObjManager
from reding.settings import PAGINATION_DEFAULT_OFFSET as OFFSET
from reding.settings import PAGINATION_DEFAULT_SIZE as SIZE


class RedingResource(restful.Resource):
    parser_cls = reqparse.RequestParser

    def __init__(self):
        super(RedingResource, self).__init__()
        self.parser = self.parser_cls()
        self.configure()

    def configure(self):
        pass


class RedingListResource(RedingResource):
    @staticmethod
    def parse_sort(value):
        c = value[0]
        if c in ('+', '-'):
            value = value[1:]
        else:
            c = '+'
        return c == '+', value


class RatingDetailResource(RedingResource):
    @marshal_with(RatingModel.fields)
    def get(self, namespace, obj_id, user_id):
        try:
            return RatingModel(namespace=namespace, user_id=user_id, obj_id=obj_id).get()
        except DoesNotExists:
            abort(404)

    @marshal_with(RatingModel.fields)
    def post(self, namespace, obj_id, user_id):
        self.parser.add_argument('vote', type=int, required=True)
        args = self.parser.parse_args()
        model = RatingModel(namespace=namespace, user_id=user_id, obj_id=obj_id)
        model.set(**dict([(k, args.get(k, v)) for k, v in request.form.items()]))
        return model.get()

    def delete(self, namespace, obj_id, user_id):
        RatingModel(namespace=namespace, user_id=user_id, obj_id=obj_id).delete()
        return '', 204


class RatingListResource(RedingListResource):
    def configure(self):
        super(RatingListResource, self).configure()
        self.parser.add_argument('sort', type=str, default='+when')
        self.parser.add_argument('offset', type=int, default=OFFSET)
        self.parser.add_argument('size', type=int, default=SIZE)
        self.parser.add_argument('vote_min', type=int)
        self.parser.add_argument('vote_max', type=int)
        self.parser.add_argument('when_min', type=int)
        self.parser.add_argument('when_max', type=int)

    @marshal_with(RatingModel.fields)
    def get(self, namespace, obj_id):
        args = self.parser.parse_args()
        sort_desc, sort_key = self.parse_sort(args['sort'])
        return ObjModel(namespace=namespace, obj_id=obj_id).details(
            offset=args['offset'],
            size=args['size'],
            vote_min=args['vote_min'],
            vote_max=args['vote_max'],
            when_min=args['when_min'],
            when_max=args['when_max'],
            sort_desc=sort_desc,
            sort_key=sort_key,
        )


class ObjDetailResource(RedingResource):
    @marshal_with(ObjModel.fields)
    def get(self, namespace, obj_id):
        try:
            return ObjModel(namespace=namespace, obj_id=obj_id).get()
        except DoesNotExists:
            abort(404)


class ObjListResource(RedingListResource):
    def configure(self):
        super(ObjListResource, self).configure()
        self.parser.add_argument('object_id', type=str, action='append')
        self.parser.add_argument('sort', type=str, default='+amount')
        self.parser.add_argument('offset', type=int, default=OFFSET)
        self.parser.add_argument('size', type=int, default=SIZE)
        self.parser.add_argument('updated_min', type=int)
        self.parser.add_argument('updated_max', type=int)

    @marshal_with(ObjModel.fields)
    def get(self, namespace):
        args = self.parser.parse_args()
        sort_desc, sort_key = self.parse_sort(args['sort'])
        return ObjManager(namespace=namespace).list(
            objects_id=args['object_id'],
            offset=args['offset'],
            size=args['size'],
            updated_min=args['updated_min'],
            updated_max=args['updated_max'],
            sort_key=sort_key,
            sort_desc=sort_desc,
        )
