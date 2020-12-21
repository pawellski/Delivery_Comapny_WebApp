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

login_namespace = api_app.namespace("login", description = "Login Page API")
logout_namespace = api_app.namespace("logout", description = "Logout Page API")
packages_namespace = api_app.namespace("packages", description = "Packages API")
pickup_package_namespace = api_app.namespace("pickup_package", description = "Pick Up Package API")

log = app.logger
COURIERS = "couriers"
SESSION_ID = "session-id"
COURIER_SESSIONS = "courier-sessions"
NEW = "Nowa"
PASSED_ON = "Przekazana"

log = app.logger

@login_namespace.route("/")
class Login(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument("login", required = True, type=str, help = "Set user login", location="form")
    parser.add_argument("password", required = True, type=str, help = "Set user password", location="form")

    @api_app.response(200, "courier_login.html")
    @api_app.produces(["text/html"])
    def get(self):
        self.add_couriers()
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template("courier_login.html"), 200, headers)

    @api_app.doc(responses = {200: "OK"})
    def post(self):
        form = request.form
        login = form.get("login").encode("utf-8")
        password = form.get("password")

        if db.exists(COURIERS):
            if db.hexists(COURIERS, login):
                if db.hget(COURIERS, login) == password:
                    session_uuid = str(uuid.uuid4())
                    db.hset(COURIER_SESSIONS, session_uuid, login)
                    response = make_response({"login": "Ok"}, 200)
                    response.set_cookie(SESSION_ID, session_uuid, max_age=120, secure=True, httponly=True)
                    return response

        return {"login": "Reject"}, 400
                    
    def add_couriers(self):
        if db.exists(COURIERS):
            if db.hexists(COURIERS, "KR023") == 0:
                db.hset(COURIERS, "KR023", "Pa$$worD1")
            if db.hexists(COURIERS, "KR054") == 0:
                db.hset(COURIERS, "KR054", "Pa$$worD2")
            if db.hexists(COURIERS, "KR091") == 0:
                db.hset(COURIERS, "KR0091", "Pa$$worD3")
        else:
            db.hset(COURIERS, "KR023", "Pa$$worD1")
            db.hset(COURIERS, "KR054", "Pa$$worD2")
            db.hset(COURIERS, "KR0091", "Pa$$worD3")

@logout_namespace.route("/")
class Logout(Resource):

    @api_app.response(200, "courier _login.html")
    @api_app.produces(["text/html"])
    def get(self):
        cookie = request.cookies.get(SESSION_ID)
        if cookie is not None:
            db.hdel(COURIER_SESSIONS, cookie)
        headers = {'Content-Type': 'text-html'}
        return make_response(render_template("courier_login.html"), 200, headers)

@packages_namespace.route("/")
class Packages(Resource):
    @api_app.response(200, "courier_packages.html")
    @api_app.produces(["text/html"])
    def get(self):
        cookie = request.cookies.get(SESSION_ID)
        if cookie is not None:
            if db.hexists(COURIER_SESSIONS, cookie):
                login = db.hget(COURIER_SESSIONS, cookie)
                db.hdel(COURIER_SESSIONS, cookie)
                session_uuid = str(uuid.uuid4())
                db.hset(COURIER_SESSIONS, session_uuid.encode("utf-8"), login)
                headers = {'Content-Type': 'text/html'}
                response = make_response(render_template("courier_packages.html"), 200, headers)
                response.set_cookie(SESSION_ID, session_uuid, max_age=120, secure=True, httponly=True)
                return response
            else:
                return make_response("Unauthorized", 401)
        else:
            return make_response("Unauthorized", 401)

@pickup_package_namespace.route("/")
class PickupPackage(Resource):
    @api_app.response(200, "courier_pickup_package.html")
    @api_app.produces(["text/html"])
    def get(self):
        cookie = request.cookies.get(SESSION_ID)
        if cookie is not None:
            if db.hexists(COURIER_SESSIONS, cookie):
                login = db.hget(COURIER_SESSIONS, cookie)
                db.hdel(COURIER_SESSIONS, cookie)
                session_uuid = str(uuid.uuid4())
                db.hset(COURIER_SESSIONS, session_uuid.encode("utf-8"), login)
                headers = {'Content-Type': 'text/html'}
                response = make_response(render_template("courier_pickup_package.html"), 200, headers)
                response.set_cookie(SESSION_ID, session_uuid, max_age=120, secure=True, httponly=True)
                return response
            else:
                return make_response("Unauthorized", 401)
        else:
            return make_response("Unauthorized", 401)

    def post(self):
        cookie = request.cookies.get(SESSION_ID)
        if cookie is not None:
            if db.hexists(COURIER_SESSIONS, cookie):
                form = request.form
                package_id = form.get("package_id").encode("utf-8")
                login = db.hget(COURIER_SESSIONS, cookie)
                if db.exists(package_id):
                    if db.hget(package_id, "status") == NEW:
                        db.hset(package_id, "status", PASSED_ON)
                        db.sadd(login, package_id)
                        return make_response("Package is passed on correctly.", 200)
                    else:
                        return make_response("Package has not NEW status.", 409)
                else:
                   return make_response("Package does not exist.", 400) 
            else:
                return make_response("Unauthorized", 401)
        else:
            return make_response("Unauthorized", 401)