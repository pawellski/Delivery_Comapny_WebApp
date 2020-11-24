from flask import Flask, render_template, make_response
from flask import request, jsonify, redirect, url_for
import hashlib, uuid
import logging
import redis

GET = "GET"
POST = "POST"
users = "users"
sessions = "sessions"

app = Flask(__name__, static_url_path="")
db = redis.Redis(host="redis-db", port=6379, decode_responses=True)

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
        login = form.get("login").encode("utf-8")
        password = hashlib.sha512(form.get("password").encode("utf-8")).hexdigest()

        if db.sismember(users, login):
            if db.hget(login, "password") == password:
                log.debug("zalogowano!")
                name_hash = hashlib.sha512(login).hexdigest()
                session_id = str(uuid.uuid4())
                log.debug(session_id)
                db.hset(sessions, session_id.encode("utf-8"), name_hash.encode("utf-8"))
                log.debug(db.hgetall(sessions))
                response = make_response(render_template("user_homepage.html"))
                response.set_cookie(session_id, name_hash,
                                    max_age=30, secure=True, httponly=True)
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
    return render_template("user_homepage.html")
    

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
