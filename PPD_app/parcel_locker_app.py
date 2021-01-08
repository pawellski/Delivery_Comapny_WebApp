from flask import Flask, request, render_template, make_response
from flask_jwt_extended import JWTManager, get_jwt_identity, jwt_required
from flask_restplus import Api, Resource, fields, reqparse
from flask_socketio import SocketIO, join_room, leave_room, emit, send
from flask_cors import CORS
from jwt import decode, InvalidTokenError
from exception.exception import UnauthorizedError, ForbiddenError
from datetime import datetime
import hashlib, uuid
import redis
import os
import json

app = Flask(__name__, static_url_path="")
db = redis.Redis(host="redis-db", port=6379, decode_responses=True)
socket_io = SocketIO(app, cors_allowed_origins="*")
api_app = Api(app = app, version = "0.1", title = "Parcel Locker App API", description = "REST-full API for Parcel Locker")

user_page_namespace = api_app.namespace("user_page", description = "User Page API")
courier_page_namespace = api_app.namespace("courier_page", description = "Courier Page API")
put_package_namespace = api_app.namespace("put_package", description = "Put Package API")
pickup_package_namespace = api_app.namespace("pickup_package", description = "Pick Up Package API")
available_packages_page_namespace = api_app.namespace("available_packages", description = "Available Packages Page API")
packages_namespace = api_app.namespace("packages", description = "Packages API")

SECRET_KEY = "COURIER_JWT_SECRET"
NEW = "Nowa"
PENDING = "Oczekująca"
PICK_UP = "Odebrana"
PARCEL_LOCKERS = "parcel_lockers"
COURIERS = "couriers"
URL = "https://localhost:8082/packages/list/"
ROOM_ID = "room_id"
MESSAGE = "message"

app.config["JWT_SECRET_KEY"] = os.environ.get(SECRET_KEY)

jwt = JWTManager(app)
cors = CORS(app)

log = app.logger

@user_page_namespace.route("/")
class UserPage(Resource):

    @api_app.response(200, "parcel_locker_user.html")
    @api_app.produces(["text/html"])
    def get(self):
        self.add_parcel_locker()
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template("parcel_locker_user.html"), 200, headers)


    def add_parcel_locker(self):
        if db.exists(PARCEL_LOCKERS):
            if db.sismember(PARCEL_LOCKERS, "PL079") == 0:
                db.sadd(PARCEL_LOCKERS, "PL079")
            if db.sismember(PARCEL_LOCKERS, "PL183") == 0:
                db.sadd(PARCEL_LOCKERS, "PL183")
            if db.sismember(PARCEL_LOCKERS, "PL271") == 0:
                db.sadd(PARCEL_LOCKERS, "PL271")          
        else:
            db.sadd(PARCEL_LOCKERS, "PL079")
            db.sadd(PARCEL_LOCKERS, "PL183")
            db.sadd(PARCEL_LOCKERS, "PL271")  

@courier_page_namespace.route("/")
class CourierPage(Resource):

    parser = reqparse.RequestParser()
    
    parser.add_argument("token", required = True, type=str, help = "Token cannot be blank", location="form")
    parser.add_argument("parcel_locker_id", required = True, type=str, help = "Parcel locker id cannot be blank", location="form")

    @api_app.response(200, "parcel_locker_courier.html")
    @api_app.produces(["text/html"])
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template("parcel_locker_courier.html"), 200, headers)

    @api_app.expect(parser)
    @api_app.doc(responses = {200: "Authorization: Correct, access_token", 400: "Authorization: Incorrect. Wrong id.", 401: "Authorization: Unauthorized"})
    def post(self):
        form = request.form
        token = form.get("token")
        parcel_locker_id = form.get("parcel_locker_id")

        if token is None:
            return make_response({"Authorization": "Unauthorized"}, 401)
        
        if not self.valid(token):
            return make_response({"Authorization": "Unauthorized"}, 401)

        if db.sismember(PARCEL_LOCKERS, parcel_locker_id):
            return make_response({"Authorization": "Correct", "access_token": token}, 200)
        else:
            return make_response({"Authorization": "Incorrect. Wrong id."}, 400)
        
        
    
    def valid(self, token):
        try:
            token_json = decode(token, os.environ.get(SECRET_KEY))
        except InvalidTokenError as e:
            log.error(str(e))
            return False
        courier = token_json['identity']
        if db.hexists(COURIERS, courier.encode("utf-8")):
            log.debug("Token and identity valid!")
            return True
        log.debug("Token identity invalid!")
        return False



@put_package_namespace.route("/")
class PutPackage(Resource):
    parser = reqparse.RequestParser()
    
    parser.add_argument("parcel_locker_id", required = True, type=str, help = "Parcel locker id cannot be blank", location="form")
    parser.add_argument("waybill_hash", required = True, type=str, help = "Waybill hash id cannot be blank", location="form")

    @api_app.expect(parser)
    @api_app.doc(responses = {200: "Changed status of package", 400: "Wrong parcel locker id or package id", 409: "Already package is in parcel locker"})
    def post(self):
        form = request.form
        parcel_locker_id = form.get("parcel_locker_id")
        waybill_hash = form.get("waybill_hash")

        if parcel_locker_id is not None and db.sismember(PARCEL_LOCKERS, parcel_locker_id.encode("utf-8")):
            if waybill_hash is not None and db.exists(waybill_hash.encode("utf-8")):
                if db.sismember(parcel_locker_id.encode("utf-8"), waybill_hash.encode("utf-8")) == 0 and db.hget(waybill_hash.encode("utf-8"), "status") == NEW:
                    db.sadd(parcel_locker_id.encode("utf-8"), waybill_hash.encode("utf-8"))
                    db.hset(waybill_hash.encode("utf-8"), "status", PENDING)
                    return "Changed status of package.", 200
                elif db.hget(waybill_hash.encode("utf-8"), "status") == PENDING:
                    return "Already package is in parcel locker", 409
        
        return "Wrong parcel locker id or package id", 400


@pickup_package_namespace.route("/")
class PickupPackage(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("Authorization", required = True, location="headers")
    
    parser.add_argument("package_id", required = True, type=str, help = "Package id cannot be blank", location="form")
    parser.add_argument("parcel_locker_id", required = True, type=str, help = "Parcel locker id cannot be blank", location="form")

    @api_app.expect(parser)
    @api_app.doc(responses = {200: "Package is picked up correctly.", 400: "Wrong parcel locker id or package id."})
    @jwt_required
    def post(self):
        form = request.form
        courier = get_jwt_identity()
        package_id = form.get("package_id")
        parcel_locker_id = form.get("parcel_locker_id")
        
        if parcel_locker_id is not None and db.sismember(PARCEL_LOCKERS, parcel_locker_id.encode("utf-8")):
            if package_id is not None and db.exists(package_id.encode("utf-8")):
                db.srem(parcel_locker_id.encode("utf-8"), package_id.encode("utf-8"))
                now = datetime.now()
                now_string = now.strftime("%d/%m/%Y %H:%M:%S")
                db.hset(courier, package_id.encode('utf-8'), now_string.encode('utf-8'))
                db.hset(package_id.encode("utf-8"), "status", PICK_UP)
                return "Package is picked up correctly.", 200

        return "Wrong parcel locker id or package id.", 400



@available_packages_page_namespace.route("/")
class AvailablePackagesPage(Resource):

    @api_app.response(200, "available_packages_page_parcel_locker.html")
    @api_app.produces(["text/html"])
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template("available_packages_page_parcel_locker.html"), 200, headers)


@packages_namespace.route("/list/<int:start>")
class PackageList(Resource):
    
    parser = reqparse.RequestParser()
    parser.add_argument("Authorization", required = True, location="headers")

    @api_app.expect(parser)
    @api_app.doc(responses = {200: "packages, previous, next", 400: "Start is incorrect", 401: "Unauthorized"})
    @jwt_required
    def get(self, start):
        courier_id = get_jwt_identity()
        parcel_locker_id = token = request.headers.get('PL') or request.args.get('PL')

        if parcel_locker_id is None or db.sismember(PARCEL_LOCKERS, parcel_locker_id) == 0:
            return make_response("Wrong parcel locker id.", 400)

        packages_id = list(db.smembers(parcel_locker_id.encode("utf-8")))
        count = len(packages_id)

        packages=[]
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
        

    def get_package_json(self, package_id):
        package_info = {"id": package_id}
        return package_info    
            
@socket_io.on("connect")
def handle_on_connect():
    app.logger.debug("Connected -> OK")
    emit("connection response", {"data": "Correctly connected"})


@socket_io.on("disconnect")
def handle_on_disconnect():
    app.logger.debug("Disconnected -> Bye")


@socket_io.on("join")
def handle_on_join(data):
    room_id = data[ROOM_ID]
    join_room(room_id)
    emit("joined_room", {"room_id": room_id})
    app.logger.debug(f"Added to the room: {room_id}")


@socket_io.on("new_message")
def handle_new_message(data):
    app.logger.debug(f"Received data: {data}.")
    emit("chat_message", {MESSAGE: data[MESSAGE]}, room=data[ROOM_ID])