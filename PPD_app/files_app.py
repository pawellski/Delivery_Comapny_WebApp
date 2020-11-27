from flask import Flask, render_template, send_file, request, jsonify, make_response
from flask_jwt_extended import JWTManager, jwt_required
from flask_cors import CORS
import logging
import redis
import os

GET = "GET"
POST = "POST"
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
