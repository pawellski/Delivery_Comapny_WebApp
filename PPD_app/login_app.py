from flask import Flask, render_template

app = Flask(__name__, static_url_path="")

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET"])
def register():
    return render_template("registration.html")

@app.route("/login", methods=["GET"])
def login():
    return render_template("login.html")