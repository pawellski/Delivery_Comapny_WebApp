from flask import Flask, render_template, send_file, request, jsonify, make_response
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_cors import CORS
from datetime import datetime
import uuid
import logging
import redis
import os

GET = "GET"
POST = "POST"
waybills = "waybills"
SECRET_KEY = "LOGIN_JWT_SECRET"
TOKEN_EXPIRES_IN_SECONDS = 120

app = Flask(__name__, static_url_path="")
db = redis.Redis(host="redis-db", port=6379, decode_responses=True)

app.config["JWT_SECRET_KEY"] = os.environ.get(SECRET_KEY)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = TOKEN_EXPIRES_IN_SECONDS

jwt = JWTManager(app)
cors = CORS(app)

log = app.logger

@app.route("/", methods=[GET])
def index():
    return render_template("index-files.html")


@app.route("/add_package", methods=[POST])
@jwt_required
def add_package():
    login = get_jwt_identity()
    waybills_login = "waybills_" + login
    form = request.form
    if add_package_validation(form):
        now = datetime.now()
        now_string = now.strftime("%d/%m/%Y %H:%M:%S")
        unique_id = uuid.uuid4().hex.encode("utf-8")

        db.hset(waybills_login.encode("utf-8"), unique_id, now_string.encode("utf-8"))

        db.hset(unique_id, "sender_name", form.get("sender_name").encode("utf-8"))
        db.hset(unique_id, "sender_surname", form.get("sender_surname").encode("utf-8"))
        db.hset(unique_id, "sender_street", form.get("sender_street").encode("utf-8"))
        db.hset(unique_id, "sender_number", form.get("sender_number").encode("utf-8"))
        db.hset(unique_id, "sender_postal_code", form.get("sender_postal_code").encode("utf-8"))
        db.hset(unique_id, "sender_city", form.get("sender_city").encode("utf-8"))
        db.hset(unique_id, "sender_country", form.get("sender_country").encode("utf-8"))
        db.hset(unique_id, "sender_phone_number", form.get("sender_phone_number").encode("utf-8"))

        db.hset(unique_id, "recipient_name", form.get("recipient_name").encode("utf-8"))
        db.hset(unique_id, "recipient_surname", form.get("recipient_surname").encode("utf-8"))
        db.hset(unique_id, "recipient_street", form.get("recipient_street").encode("utf-8"))
        db.hset(unique_id, "recipient_number", form.get("recipient_number").encode("utf-8"))
        db.hset(unique_id, "recipient_postal_code", form.get("recipient_postal_code").encode("utf-8"))
        db.hset(unique_id, "recipient_city", form.get("recipient_city").encode("utf-8"))
        db.hset(unique_id, "recipient_country", form.get("recipient_country").encode("utf-8"))
        db.hset(unique_id, "recipient_phone_number", form.get("recipient_phone_number").encode("utf-8"))

        log.debug(db.hgetall(waybills_login))
        log.debug(db.hgetall(unique_id))

        return jsonify({"add_package": "Correct"}), 200
                    
    else:
        return jsonify({"add_package": "Incorrect"}), 400

@app.route("/get_packages", methods=[GET])
@jwt_required
def get_packages():
    login = get_jwt_identity()
    waybills_login = "waybills_" + login
    packages = db.hgetall(waybills_login)
    return jsonify(packages), 200


def add_package_validation(form):
    errors = 0
    if form.get("sender_name").isspace():
        errors = errors + 1
    if form.get("sender_surname").isspace():
        errors = errors + 1
    if form.get("sender_street").isspace():
        errors = errors + 1
    if form.get("sender_number").isspace():
        errors = errors + 1
    if form.get("sender_postal_code").isspace():
        errors = errors + 1
    if form.get("sender_city").isspace():
        errors = errors + 1
    if form.get("sender_country").isspace():
        errors = errors + 1
    if form.get("sender_phone_number").isspace():
        errors = errors + 1
    if form.get("recipient_name").isspace():
        errors = errors + 1
    if form.get("recipient_surname").isspace():
        errors = errors + 1
    if form.get("recipient_street").isspace():
        errors = errors + 1
    if form.get("recipient_number").isspace():
        errors = errors + 1
    if form.get("recipient_postal_code").isspace():
        errors = errors + 1
    if form.get("recipient_city").isspace():
        errors = errors + 1
    if form.get("recipient_country").isspace():
        errors = errors + 1
    if form.get("recipient_phone_number").isspace():
        errors = errors + 1
    
    if errors == 0:
        return True
    else:
        return False
