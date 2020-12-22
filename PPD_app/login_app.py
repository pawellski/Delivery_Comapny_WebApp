from flask import Flask, request, render_template, make_response
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from flask_restplus import Api, Resource, fields, reqparse
from exception.exception import UnauthorizedError, ForbiddenError
import hashlib, uuid
import redis
import os


app = Flask(__name__, static_url_path="")
db = redis.Redis(host="redis-db", port=6379, decode_responses=True)
api_app = Api(app = app, version = "0.1", title = "Login App API", description = "REST-full API for login")

home_namespace = api_app.namespace("home", description = "Home API")
user_namespace = api_app.namespace("user", description = "Check user API")
register_namespace = api_app.namespace("register", description = "Register API")
login_namespace = api_app.namespace("login", description = "Login API")
logout_namespace = api_app.namespace("logout", description = "Logout API")
user_homepage_namespace = api_app.namespace("user_homepage", description = "User homepage API")
add_package_namespace = api_app.namespace("add_package", description = "Add package API")
token_namespace = api_app.namespace("token", description = "Token API")

SESSION_ID = "session-id"
users = "users"
sessions = "sessions"
SECRET_KEY = "LOGIN_JWT_SECRET"
TOKEN_EXPIRES_IN_SECONDS = 120

app.config["JWT_SECRET_KEY"] = os.environ.get(SECRET_KEY)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = TOKEN_EXPIRES_IN_SECONDS

jwt = JWTManager(app)
log = app.logger

@home_namespace.route("/")
class Home(Resource):

    @api_app.response(200, "index.html")
    @api_app.produces(["text/html"])
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template("index.html"), 200, headers)

@user_namespace.route("/<string:user>")
class User(Resource):
    
    @api_app.doc(responses = {200: "user_exists: False", 404: "user_exists: True"})
    def get(self, user):
        if db.scard(users) != 0:
            if db.sismember(users, user):
                log.debug(db.smembers(users))
                return {"user_exists": "True"}, 200
        return {"user_exists": "False"}, 404

@register_namespace.route("/")
class Register(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument("name", required = True, type=str, help = "User name must contain only letters", location="form")
    parser.add_argument("surname", required = True, type=str, help = "User surname must contain only letters", location="form")
    parser.add_argument("pesel", required = True, type=str, help = "User pesel must be compatible with government format", location="form")
    parser.add_argument("date_of_birth", required = True, type=str, help = "User date of birth cannot be blank", location="form")
    parser.add_argument("street", required = True, type=str, help = "User must contain only letters", location="form")
    parser.add_argument("number", required = True, type=str, help = "User number cannot be blank", location="form")
    parser.add_argument("postal_code", required = True, type=str, help = "User postal code cannot be blank", location="form")
    parser.add_argument("city", required = True, type=str, help = "User city must contain only letters", location="form")
    parser.add_argument("country", required = True, type=str, help = "User country must contain only letters", location="form")
    parser.add_argument("login", required = True, type=str, help = "Login must contain only letters", location="form")
    parser.add_argument("password", required = True, type=str, help = "User password must be strong", location="form")
    parser.add_argument("second_password", required = True, type=str, help = "User second password must be the same", location="form")

    @api_app.response(200, "registration.html")
    @api_app.produces(["text/html"])
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template("registration.html"), 200, headers)
    
    @api_app.expect(parser)
    @api_app.doc(responses = {201: "registration_status: OK", 400: "errors"})
    def post(self):
        form = request.form
        login = form.get("login").encode("utf-8")
        log.debug(login)
        errors = self.validation(form)
        log.debug("ERRORS")
        log.debug(errors)
        if len(errors) == 0:        
            db.sadd(users, login)

            db.hset(login, "name", form.get("name").encode("utf-8"))
            db.hset(login, "surname", form.get("surname").encode("utf-8"))
            db.hset(login, "pesel", form.get("pesel").encode("utf-8"))
            db.hset(login, "date_of_birth", form.get("date_of_birth").encode("utf-8"))
            db.hset(login, "street", form.get("street").encode("utf-8"))
            db.hset(login, "number", form.get("number").encode("utf-8"))
            db.hset(login, "postal_code", form.get("postal_code").encode("utf-8"))
            db.hset(login, "city", form.get("city").encode("utf-8"))
            db.hset(login, "country", form.get("country").encode("utf-8"))
            db.hset(login, "password", hashlib.sha512(form.get("password").encode("utf-8")).hexdigest())
        
            return {"registration_status": "OK"}, 201
        else:
            body = errors
            response = make_response(body, 400)
            return response
    
    def validation(self, form):
        errors = {}
        log.debug(form)
        if form.get("name").encode("utf-8").isalpha() == False:
            errors["name"] = "Name incorret."
        if form.get("surname").encode("utf-8").isalpha() == False:
            errors["surname"] = "Surname incorrect."
        if form.get("pesel").encode("utf-8").isdigit() == False:
            errors["pesel"] = "Pesel incorrect."
        if form.get("date_of_birth").encode("utf-8").isspace() == True:
            errors["date_of_birth"] = "Date of birth incorrect."
        if form.get("street").encode("utf-8").isspace() == True:
            errors["street"] = "Street incorrect."
        if form.get("number").encode("utf-8").isspace() == True:
            errors["number"] = "Number incorrect."
        if form.get("postal_code").encode("utf-8").isspace() == True:
            errors["postal_code"] = "Postal code incorrect."
        if form.get("city").encode("utf-8").isalpha() == False:
            errors["city"] = "City incorrect."
        if form.get("country").encode("utf-8").isalpha() == False:
            errors["country"] = "Country incorrect."
        if form.get("login").encode("utf-8").isalpha() == False:
            errors["login"] = "Login incorrect."
        if form.get("password").encode("utf-8").isspace() == True:
            errors["password"] = "Password incorrect."
        
        return errors

@login_namespace.route("/")
class Login(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument("login", required = True, type=str, help = "Set user login", location="form")
    parser.add_argument("password", required = True, type=str, help = "Set user password", location="form")

    @api_app.response(200, "login.html")
    @api_app.produces(["text/html"])
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template("login.html"), 200, headers)

    @api_app.expect(parser)
    @api_app.doc(responses = {200: "login: Ok, access_token", 400: "login: Reject"})
    def post(self):
        form = request.form
        login = form.get("login").encode("utf-8")
        password = hashlib.sha512(form.get("password").encode("utf-8")).hexdigest()

        if db.sismember(users, login):
            if db.hget(login, "password") == password:
                session_uuid = str(uuid.uuid4())
                log.debug("Login user")
                log.debug(login)
                log.debug("SESSION ID")
                log.debug(session_uuid)
                db.hset(sessions, session_uuid, login)
                log.debug(db.hgetall(sessions))
                access_token = create_access_token(identity=login.decode("utf-8"))
                response = make_response({"login": "Ok", "access_token": access_token}, 200)
                response.set_cookie(SESSION_ID, session_uuid, max_age=120, secure=True, httponly=True)
                return response

        return {"login": "Reject"}, 400

@logout_namespace.route("/")
class Logout(Resource):

    @api_app.response(200, "index.html")
    @api_app.produces(["text/html"])
    def get(self):
        cookie = request.cookies.get(SESSION_ID)
        log.debug(cookie)
        if cookie is not None:
            db.hdel(sessions, cookie)
            log.debug(db.hgetall(sessions))

        headers = {'Content-Type': 'text-html'}
        return make_response(render_template("index.html"), 200, headers)

@user_homepage_namespace.route("/")
class UserHomepage(Resource):

    @api_app.response(200, "user_homepage.html")
    @api_app.produces(["text/html"])
    def get(self):
        cookie = request.cookies.get(SESSION_ID)
        if cookie is not None:
            if db.hexists(sessions, cookie):
                login = db.hget(sessions, cookie)
                db.hdel(sessions, cookie)
                session_uuid = str(uuid.uuid4())
                db.hset(sessions, session_uuid.encode("utf-8"), login)
                headers = {'Content-Type': 'text/html'}
                response = make_response(render_template("user_homepage.html"), 200, headers)
                response.set_cookie(SESSION_ID, session_uuid, max_age=120, secure=True, httponly=True)
                return response
            else:
                raise UnauthorizedError
        else:
            raise UnauthorizedError

            

@add_package_namespace.route("/")
class AddPackage(Resource):

    @api_app.response(200, "add_package.html")
    @api_app.produces(["text/html"])
    def get(self):
        cookie = request.cookies.get(SESSION_ID)
        if cookie is not None:
            if db.hexists(sessions, cookie):
                login = db.hget(sessions, cookie)
                db.hdel(sessions, cookie)
                session_uuid = str(uuid.uuid4())
                db.hset(sessions, session_uuid.encode("utf-8"), login)
                headers = {'Content-Type': 'text/html'}
                response = make_response(render_template("add_package.html"), 200, headers)
                response.set_cookie(SESSION_ID, session_uuid, max_age=120, secure=True, httponly=True)
                return response
            else:
                raise UnauthorizedError
        else:
            raise UnauthorizedError



@token_namespace.route("/")
class Token(Resource):

    @api_app.doc(responses = {200: "access_token", 401: "You are unauthorized."})
    def get(self):
        cookie = request.cookies.get(SESSION_ID)
    
        if cookie is not None:
            if db.hexists(sessions, cookie):
                login = db.hget(sessions, cookie)
                access_token = create_access_token(identity=login)
                return {"access_token": access_token}, 200
            else:
                raise UnauthorizedError
        else:
            raise UnauthorizedError
    

@app.errorhandler(400)
def handle_bad_request(error):
    return make_response(render_template("/errors/400.html"), 400)

@app.errorhandler(UnauthorizedError)
def handle_unauthorized(error):
    return make_response(render_template("/errors/401.html"), 401)

@app.errorhandler(ForbiddenError)
def handle_forbidden(error):
    return make_response(render_template("/errors/403.html"), 403)

@app.errorhandler(404)
def handle_not_found(error):
    return make_response(render_template("/errors/404.html"), 404) 

@app.errorhandler(500)
def handle_internal_server_error(error):
    return make_response(render_template("/errors/500.html"), 500) 