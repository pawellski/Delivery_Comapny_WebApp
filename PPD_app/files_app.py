from flask import Flask, render_template, send_file, request, jsonify, make_response, abort
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from jwt import decode, InvalidTokenError
from flask_cors import CORS
from datetime import datetime
import uuid
import logging
import redis
import os
from model.waybill import *

GET = "GET"
POST = "POST"
waybills = "waybills"
SECRET_KEY = "LOGIN_JWT_SECRET"
FILES_PATH = "waybill_files/"
IMAGES_PATH = "waybill_images/"
PATH_AND_FILENAME = "path_and_filename"
PATH_AND_IMAGE = "path_and_image"
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

        new_filename = save_file(request.files["package_image"], unique_id.decode("utf-8"))
        if(new_filename != "Empty content of image!"):
            db.hset(unique_id, PATH_AND_IMAGE, new_filename)

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

@app.route("/waybill/<string:waybill_hash>", methods=[GET])
def download_waybill(waybill_hash):
    token = request.headers.get('token') or request.args.get('token')
    log.debug("TOKEN " + token)
    log.debug("WAYBILL_HASH" + waybill_hash)

    if token is None:
        abort(401)
    
    if not valid(token, waybill_hash):
        abort(403)

    filename = waybill_hash + ".pdf"

    if db.hexists(waybill_hash, PATH_AND_FILENAME):
        filepath = db.hget(waybill_hash, PATH_AND_FILENAME)
        if os.path.isfile(filepath):
            try:
                return send_file(filepath, as_attachment=True)
            except Exception as e:
                log.error(e)
        else:
            filepath = create_and_save_file(waybill_hash)
            try:
                return send_file(filepath, as_attachment=True)
            except Exception as e:
                log.error(e)
    else:
        filepath = create_and_save_file(waybill_hash)
        try:
            return send_file(filepath, as_attachment=True)
        except Exception as e:
            log.error(e)


def to_waybill(filename):
    id = filename
    sender = to_sender(filename)
    recipient = to_recipient(filename)

    return Waybill(id, sender, recipient)

def to_sender(filename):
    sender_name = db.hget(filename, "sender_name")
    sender_surname = db.hget(filename, "sender_surname")
    sender_phone_number = db.hget(filename, "sender_phone_number")
    sender_address = to_sender_address(filename)
    return Person(sender_name, sender_surname, sender_address, sender_phone_number)

def to_recipient(filename):
    recipient_name = db.hget(filename, "recipient_name")
    recipient_surname = db.hget(filename, "recipient_surname")
    recipient_phone_number = db.hget(filename, "recipient_phone_number")
    recipient_address = to_recipient_address(filename)
    return Person(recipient_name, recipient_surname, recipient_address, recipient_phone_number)

def to_sender_address(filename):
    sender_street = db.hget(filename, "sender_street")
    sender_number = db.hget(filename, "sender_number")
    sender_postal_code = db.hget(filename, "sender_postal_code")
    sender_city = db.hget(filename, "sender_city")
    sender_country = db.hget(filename, "sender_country")
    return Address(sender_street, sender_number, sender_postal_code, sender_city, sender_country)

def to_recipient_address(filename):
    recipient_street = db.hget(filename, "recipient_street")
    recipient_number = db.hget(filename, "recipient_number")
    recipient_postal_code = db.hget(filename, "recipient_postal_code")
    recipient_city = db.hget(filename, "recipient_city")
    recipient_country = db.hget(filename, "recipient_country")
    return Address(recipient_street, recipient_number, recipient_postal_code, recipient_city, recipient_country)

def create_and_save_file(waybill_hash):
    waybill = to_waybill(waybill_hash)
    filepath = waybill.generate_and_save(FILES_PATH, IMAGES_PATH)
    db.hset(waybill_hash, PATH_AND_FILENAME, filepath)
    return filepath

def valid(token, waybill_hash):
    try:
        token_json = decode(token, os.environ.get(SECRET_KEY))
    except InvalidTokenError as e:
        log.error(str(e))
        return False
    waybills_login = "waybills_" + token_json['identity']
    if db.hexists(waybills_login, waybill_hash):
        log.debug("Token and identity valid!")
        return True
        log.debug("Token identity invalid!")
    return False

def save_file(file_to_save, unique_id):
    if len(file_to_save.filename) > 0:
        file_to_save.filename = unique_id + ".png"
        path_to_file = os.path.join(IMAGES_PATH, file_to_save.filename)
        file_to_save.save(path_to_file)
        return file_to_save.filename
    else:
        return "Empty content of image!"

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
