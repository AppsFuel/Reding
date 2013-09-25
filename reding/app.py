from flask import Flask
from flask.ext import restful
from reding.resources import RatingDetailResource, RatingListResource
from reding.resources import ObjDetailResource, ObjListResource

app = Flask(__name__)
api = restful.Api(app)

api.add_resource(ObjListResource, '/<string:namespace>/obj/')
api.add_resource(ObjDetailResource, '/<string:namespace>/obj/<string:obj_id>/')
api.add_resource(RatingListResource, '/<string:namespace>/obj/<string:obj_id>/user/')
api.add_resource(RatingDetailResource, '/<string:namespace>/obj/<string:obj_id>/user/<string:user_id>/')
