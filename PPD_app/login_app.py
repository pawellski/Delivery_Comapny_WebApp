from flask import Flask, render_template, make_response
from flask import request, jsonify
import hashlib
import logging
import redis

GET = "GET"
POST = "POST"
users = "users"

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
        login = form.get("login")

        errors = registration_validation(form)
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
            response = make_response(body, 200)
    else:
        return render_template("registration.html")

@app.route("/login", methods=[GET])
def login():
    return render_template("login.html")

@app.route("/user/<string:user>", methods=[GET])
def check_user(user):
    if db.scard(users) != 0:
        if db.sismember(users, user):
            log.debug(db.smembers(users))
            return jsonify({"user_exists": "True"}), 200
    return jsonify({"user_exists": "False"}), 404


def registration_validation(form):
    errors = {}
    if form.get("name").isalpha() == False:
        errors["name"] = "Name incorret."
    if form.get("surname").isalpha() == False:
        errors["name"] = "Surname incorrect."
    if form.get("pesel").isdigit() == False:
        errors["pesel"] = "Pesel incorrect."
    if form.get("date_of_birth").isspace() == True:
        errors["date_of_birth"] = "Date of birth incorrect."
    if form.get("street").isspace() == True:
        errors["street"] = "Street incorrect."
    if form.get("number").isspace() == True:
        errors["number"] = "Number incorrect."
    if form.get("postal_code").isspace() == True:
        errors["postal_code"] = "Postal code incorrect."
    if form.get("city").isalpha() == False:
        errors["city"] = "City incorrect."
    if form.get("country").isalpha() == False:
        errors["country"] = "Country incorrect."
    if form.get("login").isalpha() == False:
        errors["login"] = "Login incorrect."
    if form.get("password").isspace() == True:
        errors["password"] = "Password incorrect."
    
    return errors