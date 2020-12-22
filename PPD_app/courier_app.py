from flask import Flask, request, render_template, make_response
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from flask_restplus import Api, Resource, fields, reqparse
from exception.exception import UnauthorizedError, ForbiddenError
import hashlib, uuid
import redis
import os
import json

app = Flask(__name__, static_url_path="")
db = redis.Redis(host="redis-db", port=6379, decode_responses=True)
api_app = Api(app = app, version = "0.1", title = "Courier App API", description = "REST-full API for Courier")

login_namespace = api_app.namespace("login", description = "Login Page API")
logout_namespace = api_app.namespace("logout", description = "Logout Page API")
packages_namespace = api_app.namespace("packages", description = "Packages API")
pickup_package_namespace = api_app.namespace("pickup_package", description = "Pick Up Package API")
token_namespace = api_app.namespace("token", description = "Token API")
error_namespace = api_app.namespace("error", description = "Error API")
offline_namespace = api_app.namespace("offline", description = "Offline API")

COURIERS = "couriers"
SESSION_ID = "session-id"
COURIER_SESSIONS = "courier-sessions"
PARCEL_LOCKERS = "parcel_lockers"
NEW = "Nowa"
PASSED_ON = "Przekazana"
SECRET_KEY = "COURIER_JWT_SECRET"
URL = "https://localhost:8083/packages/list/"
TOKEN_EXPIRES_IN_SECONDS = 60

app.config["JWT_SECRET_KEY"] = os.environ.get(SECRET_KEY)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = TOKEN_EXPIRES_IN_SECONDS

jwt = JWTManager(app)
log = app.logger

@error_namespace.route("/")
class Error(Resource):
    @api_app.response(200, "courier_error.html")
    @api_app.produces(["text/html"])
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template("courier_error.html"), 200, headers)

@offline_namespace.route("/") 
class Offline(Resource):
    @api_app.response(200, "courier_offline.html")
    @api_app.produces(["text/html"])
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template("courier_offline.html"), 200, headers)

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

    @api_app.doc(responses = {200: "login: Ok", 400: "login: Reject"})
    @api_app.expect(parser)
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
                db.hset(COURIERS, "KR091", "Pa$$worD3")
        else:
            db.hset(COURIERS, "KR023", "Pa$$worD1")
            db.hset(COURIERS, "KR054", "Pa$$worD2")
            db.hset(COURIERS, "KR091", "Pa$$worD3")

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

    parser = reqparse.RequestParser()
    parser.add_argument("package_id", required = True, type=str, help = "Package id cannot be blank", location="form")
    
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

    @api_app.expect(parser)
    @api_app.doc(responses = {200: "Package is passed on correctly.", 400: "Package does not exist.", 401: "Unauthorized", 409: "Package has not NEW status."})
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

@token_namespace.route("/")
class Token(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("parcel_locker_id", required = True, type=str, help = "Parcel locker id cannot be blank", location="form")

    @api_app.expect(parser)
    @api_app.doc(responses = {200: "token: True, access_token", 400: "token: False, Wrong parcel locker id.", 401: "Unauthorized"})
    def post(self):
        form = request.form
        cookie = request.cookies.get(SESSION_ID)
        parcel_locker_id = form.get("parcel_locker_id")
        if cookie is not None:
            if db.hexists(COURIER_SESSIONS, cookie):
                if db.sismember(PARCEL_LOCKERS, parcel_locker_id):
                    login = db.hget(COURIER_SESSIONS, cookie)
                    access_token = create_access_token(identity=login)
                    return {"token": "True", "access_token": access_token}, 200
                else:
                    return make_response({"token": "False", "message":"Wrong parcel locker id."}, 400)
            else:
                return make_response("Unauthorized", 401)
        else:
            return make_response("Unauthorized", 401)


@packages_namespace.route("/list/<int:start>")
class PackagesList(Resource):

    @api_app.doc(responses = {200: "packages, previous, next", 400: "Start is incorrect", 401: "Unauthorized"})
    def get(self, start):
        cookie = request.cookies.get(SESSION_ID)
        if cookie is not None and db.hexists(COURIER_SESSIONS, cookie):
            courier_id = db.hget(COURIER_SESSIONS, cookie)
            packages_id = list(db.smembers(courier_id.encode("utf-8")))
            count = len(packages_id)

            packages = []

            limit = 5
            
            if start <= count:
                if start == count:
                    start = start-limit
            
                if count != 0:
                    for i in range(start, start + limit):
                        if i < count:
                            p = self.get_package_json(packages_id[i])
                            packages.append(p)
            
                if start < 1:
                    previous = URL + "0"
                else:
                    previous = URL + str(start - limit)
            
                if start + limit > count:
                    next = URL + str(start)
                else:
                    next = URL + str(start + limit)

                message = {"packages": packages, "previous": previous, "next": next, "numberOfPackages": count}
                message_json = json.dumps(message)
                return message_json, 200

            else:
                return make_response("Start is incorrect.", 400)

        else:
            return make_response("Unauthorized", 401)

    def get_package_json(self, package_id):
        package_info = {"id": package_id}
        return package_info