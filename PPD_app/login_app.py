from flask import Flask, render_template, make_response, abort
from flask import request, jsonify, redirect, url_for
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
import hashlib, uuid
import logging
import redis
import os

GET = "GET"
POST = "POST"
SESSION_ID = "session-id"
users = "users"
sessions = "sessions"
SECRET_KEY = "LOGIN_JWT_SECRET"
TOKEN_EXPIRES_IN_SECONDS = 120

app = Flask(__name__, static_url_path="")
db = redis.Redis(host="redis-db", port=6379, decode_responses=True)

app.config["JWT_SECRET_KEY"] = os.environ.get(SECRET_KEY)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = TOKEN_EXPIRES_IN_SECONDS

jwt = JWTManager(app)

log = app.logger

@app.route("/", methods=[GET])
def index():
    return render_template("index.html")

@app.route("/register", methods=[GET, POST])
def register():
    if request.method == POST:
        form = request.form
        login = form.get("login").encode("utf-8")

        errors = registration_validation(form)
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
        
            return jsonify({"registration_status": "OK"}), 201
        else:
            body = errors
            response = make_response(body, 400)
            return response
    else:
        return render_template("registration.html")

@app.route("/login", methods=[GET, POST])
def login():
    if request.method == POST:
        form = request.form
        login = form.get("login")
        password = hashlib.sha512(form.get("password").encode("utf-8")).hexdigest()

        if db.sismember(users, login):
            if db.hget(login, "password") == password:
                session_uuid = str(uuid.uuid4())
                log.debug("Login user")
                log.debug(login)
                log.debug("SESSION ID")
                log.debug(session_uuid)
                db.hset(sessions, session_uuid.encode("utf-8"), login.encode("utf-8"))
                log.debug(db.hgetall(sessions))
                access_token = create_access_token(identity=login)
                response = make_response(jsonify({"login": "Ok", "access_token": access_token}), 200)
                response.set_cookie(SESSION_ID, session_uuid, max_age=120, secure=True, httponly=True)
                return response

        return jsonify({"login": "Reject"}), 400
    else:
        return render_template("login.html")

@app.route("/user/<string:user>", methods=[GET])
def check_user(user):
    if db.scard(users) != 0:
        if db.sismember(users, user):
            log.debug(db.smembers(users))
            return jsonify({"user_exists": "True"}), 200
    return jsonify({"user_exists": "False"}), 404


@app.route("/user_homepage", methods=[GET])
def user_homepage():
    cookie = request.cookies.get(SESSION_ID)
    if cookie is not None:
        if db.hexists(sessions, cookie):
            login = db.hget(sessions, cookie)
            db.hdel(sessions, cookie)
            session_uuid = str(uuid.uuid4())
            db.hset(sessions, session_uuid.encode("utf-8"), login)
            response = make_response(render_template("user_homepage.html"))
            response.set_cookie(SESSION_ID, session_uuid, max_age=120, secure=True, httponly=True)
            return response
        else:
            abort(401)
    else:
        abort(401)

@app.route("/logout", methods=[GET])
def logout():
    cookie = request.cookies.get(SESSION_ID)
    log.debug(cookie)
    if cookie is not None:
        db.hdel(sessions, cookie)
        log.debug(db.hgetall(sessions))
    
    return render_template("index.html")

@app.route("/add_package",methods=[GET, POST])
def add_package():
    cookie = request.cookies.get(SESSION_ID)
    if cookie is not None:
        if db.hexists(sessions, cookie):
            login = db.hget(sessions, cookie)
            db.hdel(sessions, cookie)
            session_uuid = str(uuid.uuid4())
            db.hset(sessions, session_uuid.encode("utf-8"), login)
            response = make_response(render_template("add_package.html"))
            response.set_cookie(SESSION_ID, session_uuid, max_age=120, secure=True, httponly=True)
            return response
        else:
            abort(401)
    else:
        abort(401)

@app.route("/get_token", methods=[GET])
def get_token():
    cookie = request.cookies.get(SESSION_ID)
    if cookie is not None:
        if db.hexists(sessions, cookie):
            login = db.hget(sessions, cookie)
            access_token = create_access_token(identity=login)
            return jsonify({"access_token": access_token}), 200
        else:
            abort(401)
    else:
        abort(401)

@app.errorhandler(400)
def bad_request(error):
    return render_template("errors/400.html", error=error)

@app.errorhandler(401)
def page_unauthorized(error):
    return render_template("errors/401.html", error=error)

@app.errorhandler(403)
def page_not_available(error):
    return render_template("errors/403.html", error=error)

@app.errorhandler(404)
def page_not_found(error):
    return render_template("errors/404.html", error=error)

@app.errorhandler(500)
def server_error(error):
    return render_template("errors/500.html", error=error)

    
def registration_validation(form):
    errors = {}
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
