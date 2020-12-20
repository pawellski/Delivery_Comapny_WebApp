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

log = app.logger
COURIERS = "couriers"

@login_page_namespace.route("/")
class LoginPage(Resource):

    @api_app.response(200, "parcel_locker_user.html")
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
