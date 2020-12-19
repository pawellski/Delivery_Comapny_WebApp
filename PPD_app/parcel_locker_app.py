from flask import Flask, request, render_template, make_response
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from flask_restplus import Api, Resource, fields, reqparse
from exception.exception import UnauthorizedError, ForbiddenError
import hashlib, uuid
import redis
import os

app = Flask(__name__)
db = redis.Redis(host="redis-db", port=6379, decode_responses=True)
api_app = Api(app = app, version = "0.1", title = "Parcel Locker App API", description = "REST-full API for Parcel Locker")

user_page_namespace = api_app.namespace("user_page", description = "User Page API")
courier_page_namespace = api_app.namespace("courier_page", description = "Courier Page API")
package_namespace = api_app.namespace("package", description = "Place package API")

NEW = "Nowa"
PENDING = "Oczekująca"
PARCEL_LOCKERS = "parcel_lockers"

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

    @api_app.response(200, "parcel_locker_courier.html")
    @api_app.produces(["text/html"])
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template("parcel_locker_courier.html"), 200, headers)


@package_namespace.route("/")
class Package(Resource):

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
