from flask import Flask, request, render_template, make_response, send_file
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_restplus import Api, Resource, fields, reqparse
from jwt import decode, InvalidTokenError
from flask_cors import CORS
from model.waybill import *
from exception.exception import UnauthorizedError, ForbiddenError
from datetime import datetime
import uuid
import logging
import redis
import os

app = Flask(__name__)
db = redis.Redis(host="redis-db", port=6379, decode_responses=True)
api_app = Api(app = app, version = "0.1", title = "Files App API", description = "REST-full API for login")

home_namespace = api_app.namespace("home", description = "Home API")
add_package_namespace = api_app.namespace("add_package", description = "Add package API")
packages_namespace = api_app.namespace("packages", description = "Packages API")
waybill_namespace = api_app.namespace("waybill", description = "Waybill API")

waybills = "waybills"
SECRET_KEY = "LOGIN_JWT_SECRET"
FILES_PATH = "waybill_files/"
IMAGES_PATH = "waybill_images/"
PATH_AND_FILENAME = "path_and_filename"
PATH_AND_IMAGE = "path_and_image"
TOKEN_EXPIRES_IN_SECONDS = 120

app.config["JWT_SECRET_KEY"] = os.environ.get(SECRET_KEY)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = TOKEN_EXPIRES_IN_SECONDS

jwt = JWTManager(app)
cors = CORS(app)

log = app.logger

@home_namespace.route("/")
class Home(Resource):

    @api_app.response(200, "index-files.html")
    @api_app.produces(["text/html"])
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template("index-files.html"), 200, headers)

@add_package_namespace.route("/")
class AddPackage(Resource):
    
    parser = reqparse.RequestParser()
    
    parser.add_argument("sender_name", required = True, type=str, help = "Sender name cannot be blank", location="form")
    parser.add_argument("sender_surname", required = True, type=str, help = "Sender surname cannot be blank", location="form")
    parser.add_argument("sender_street", required = True, type=str, help = "Sender street cannot be blank", location="form")
    parser.add_argument("sender_number", required = True, type=str, help = "Sender number cannot be blank", location="form")
    parser.add_argument("sender_postal_code", required = True, type=str, help = "Sender postal code cannot be blank", location="form")
    parser.add_argument("sender_city", required = True, type=str, help = "Sender city cannot be blank", location="form")
    parser.add_argument("sender_country", required = True, type=str, help = "Sender country cannot be blank", location="form")
    parser.add_argument("sender_phone_number", required = True, type=str, help = "Sender phone number cannot be blank", location="form")
    
    parser.add_argument("recipient_name", required = True, type=str, help = "Recipient name cannot be blank", location="form")
    parser.add_argument("recipient_surname", required = True, type=str, help = "Recipient surname cannot be blank", location="form")
    parser.add_argument("recipient_street", required = True, type=str, help = "Recipient street cannot be blank", location="form")
    parser.add_argument("recipient_number", required = True, type=str, help = "Recipient number cannot be blank", location="form")
    parser.add_argument("recipient_postal_code", required = True, type=str, help = "Recipient postal code cannot be blank", location="form")
    parser.add_argument("recipient_city", required = True, type=str, help = "Recipient city cannot be blank", location="form")
    parser.add_argument("recipient_country", required = True, type=str, help = "Recipient country cannot be blank", location="form")
    parser.add_argument("recipient_phone_number", required = True, type=str, help = "Recipient phone number cannot be blank", location="form")
    
    @api_app.expect(parser)
    @api_app.doc(responses = {200: "add_package: Correct", 400: "add_package: Incorrect"})
    @jwt_required
    def post(self):
        login = get_jwt_identity()
        waybills_login = "waybills_" + login
        form = request.form
        if self.add_package_validation(form):
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

            new_filename = self.save_file(request.files["package_image"], unique_id.decode("utf-8"))
            if(new_filename != "Empty content of image!"):
                db.hset(unique_id, PATH_AND_IMAGE, new_filename)
            log.debug(db.hgetall(unique_id))
            response = make_response({"add_package": "Correct"}, 200)
            return response
                    
        else:
            return {"add_package": "Incorrect"}, 400
    

    def add_package_validation(self, form):
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
    
    def save_file(self, file_to_save, unique_id):
        if len(file_to_save.filename) > 0:
            file_to_save.filename = unique_id + ".png"
            path_to_file = os.path.join(IMAGES_PATH, file_to_save.filename)
            file_to_save.save(path_to_file)
            return file_to_save.filename
        else:
            return "Empty content of image!"

@packages_namespace.route("/")
class Packages(Resource):

    @api_app.doc(responses = {200: "packages"})
    @jwt_required
    def get(self):
        login = get_jwt_identity()
        waybills_login = "waybills_" + login
        packages = db.hgetall(waybills_login)
        return packages, 200

@waybill_namespace.route("/<string:waybill_hash>")
class Waybills(Resource):

    @api_app.doc(responses = {200: "File", 401: "You are unathorized", 403: "File is forbidden"})
    def get(self, waybill_hash):
        token = request.headers.get('token') or request.args.get('token')
        log.debug("TOKEN")
        log.debug(token)
        log.debug("WAYBILL_HASH")
        log.debug(waybill_hash)

        if token is None:
            raise UnauthorizedError
        
        if not self.valid(token, waybill_hash):
            raise ForbiddenError

        filename = waybill_hash + ".pdf"

        if db.hexists(waybill_hash, PATH_AND_FILENAME):
            filepath = db.hget(waybill_hash, PATH_AND_FILENAME)
            if os.path.isfile(filepath):
                try:
                    return send_file(filepath, as_attachment=True)
                except Exception as e:
                    log.error(e)
            else:
                filepath = self.create_and_save_file(waybill_hash)
                try:
                    return send_file(filepath, as_attachment=True)
                except Exception as e:
                    log.error(e)
        else:
            filepath = self.create_and_save_file(waybill_hash)
            try:
                return send_file(filepath, as_attachment=True)
            except Exception as e:
                log.error(e)

    def valid(self, token, waybill_hash):
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

    def create_and_save_file(self, waybill_hash):
        waybill = self.to_waybill(waybill_hash)
        filepath = waybill.generate_and_save(FILES_PATH, IMAGES_PATH)
        db.hset(waybill_hash, PATH_AND_FILENAME, filepath)
        return filepath

    def to_waybill(self, filename):
        id = filename
        sender = self.to_sender(filename)
        recipient = self.to_recipient(filename)
        return Waybill(id, sender, recipient)

    def to_sender(self, filename):
        sender_name = db.hget(filename, "sender_name")
        sender_surname = db.hget(filename, "sender_surname")
        sender_phone_number = db.hget(filename, "sender_phone_number")
        sender_address = self.to_sender_address(filename)
        return Person(sender_name, sender_surname, sender_address, sender_phone_number)

    def to_recipient(self, filename):
        recipient_name = db.hget(filename, "recipient_name")
        recipient_surname = db.hget(filename, "recipient_surname")
        recipient_phone_number = db.hget(filename, "recipient_phone_number")
        recipient_address = self.to_recipient_address(filename)
        return Person(recipient_name, recipient_surname, recipient_address, recipient_phone_number)

    def to_sender_address(self, filename):
        sender_street = db.hget(filename, "sender_street")
        sender_number = db.hget(filename, "sender_number")
        sender_postal_code = db.hget(filename, "sender_postal_code")
        sender_city = db.hget(filename, "sender_city")
        sender_country = db.hget(filename, "sender_country")
        return Address(sender_street, sender_number, sender_postal_code, sender_city, sender_country)

    def to_recipient_address(self, filename):
        recipient_street = db.hget(filename, "recipient_street")
        recipient_number = db.hget(filename, "recipient_number")
        recipient_postal_code = db.hget(filename, "recipient_postal_code")
        recipient_city = db.hget(filename, "recipient_city")
        recipient_country = db.hget(filename, "recipient_country")
        return Address(recipient_street, recipient_number, recipient_postal_code, recipient_city, recipient_country)
        
@app.errorhandler(400)
def handle_unauthorized(error):
    return make_response(render_template("/errors/400.html"), 400)

@app.errorhandler(UnauthorizedError)
def handle_unauthorized(error):
    return make_response(render_template("/errors/401.html"), 401)

@app.errorhandler(ForbiddenError)
def handle_unauthorized(error):
    return make_response(render_template("/errors/403.html"), 403)

@app.errorhandler(404)
def handle_not_found(error):
    return make_response(render_template("/errors/404.html"), 404) 

@app.errorhandler(500)
def handle_not_found(error):
    return make_response(render_template("/errors/500.html"), 500) 