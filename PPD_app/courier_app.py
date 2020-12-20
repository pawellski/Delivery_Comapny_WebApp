from flask import Flask, request, render_template, make_response
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from flask_restplus import Api, Resource, fields, reqparse
from exception.exception import UnauthorizedError, ForbiddenError
import hashlib, uuid
import redis
import os

app = Flask(__name__)
db = redis.Redis(host="redis-db", port=6379, decode_responses=True)
api_app = Api(app = app, version = "0.1", title = "Courier App API", description = "REST-full API for Courier")

login_page_namespace = api_app.namespace("login_page", description = "Login Page API")
packages_namespace = api_app.namespace("packages", description = "Packages API")
pickup_package_namespace = api_app.namespace("pickup_package", description = "Pick Up Package API")

log = app.logger
COURIERS = "couriers"

@login_page_namespace.route("/")
class LoginPage(Resource):

    @api_app.response(200, "courier_login.html")
    @api_app.produces(["text/html"])
    def get(self):
        self.add_couriers()
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template("courier_login.html"), 200, headers)


    def add_couriers(self):
        if db.exists(COURIERS):
            if db.exists("KR023") == 0:
                db.set("KR023", "Pa$$worD1")
            if db.exists("KR054") == 0:
                db.sadd("KR054", "Pa$$worD2")
            if db.exists("KR091") == 0:
                db.sadd("KR091", "Pa$$worD3")        
        else:
            db.sadd(COURIERS, "KR023")
            db.sadd(COURIERS, "KR054")
            db.sadd(COURIERS, "KR091")  


@packages_namespace.route("/")
class Packages(Resource):
    @api_app.response(200, "courier_packages.html")
    @api_app.produces(["text/html"])
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template("courier_packages.html"), 200, headers)

@pickup_package_namespace.route("/")
class PickupPackage(Resource):
    @api_app.response(200, "courier_pickup_package.html")
    @api_app.produces(["text/html"])
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template("courier_pickup_package.html"), 200, headers)