from flask import Flask, request, render_template, make_response
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from flask_restplus import Api, Resource, fields, reqparse
from exception.exception import UnauthorizedError, ForbiddenError
import hashlib, uuid
import redis
import os

app = Flask(__name__)
db = redis.Redis(host="redis-db", port=6379, decode_responses=True)
api_app = Api(app = app, version = "0.1", title = "Parcel Locker App API", description = "REST-full API for Parcel Locker")

home_namespace = api_app.namespace("home", description = "Home API")
package_namespace = api_app.namespace("package", description = "Place package API")

PENDING = "Oczekująca"

@home_namespace.route("/")
class Home(Resource):

    @api_app.response(200, "parcel_locker_user.html")
    @api_app.produces(["text/html"])
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template("parcel_locker_user.html"), 200, headers)

@package_namespace.route("/")
class Package(Resource):

    @api_app.doc(responses = {200: "Changed status of package", 400: "Wrong package id"})
    def post(self):
        form = request.form
        waybill_hash = form.get("id")

        if waybill_hash is not None and db.exists(waybill_hash.encode("utf-8")):
            db.hset(waybill_hash.encode("utf-8"), "status", PENDING)
            return "Changed status of package.", 200
        else:
            return "Wrong package id", 400
