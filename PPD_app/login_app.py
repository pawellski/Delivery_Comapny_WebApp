from flask import Flask, render_template, request
import redis

app = Flask(__name__, static_url_path="")
db = redis.Redis(host="redis-db", port=6379, decode_responses=True)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET"])
def register():
    return render_template("registration.html")

@app.route("/login", methods=["GET"])
def login():
    return render_template("login.html")
