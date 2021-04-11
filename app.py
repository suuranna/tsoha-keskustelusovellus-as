from flask import Flask
from flask import render_template, redirect, request, session
from flask_sqlalchemy import SQLAlchemy
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///suuranna"
db = SQLAlchemy(app)
app.secret_key = getenv("SECRET_KEY")

@app.route("/")
def index():
    sql = "select id, topic from topics"
    result = db.session.execute(sql)
    topics = result.fetchall()
    return render_template("index.html",topics=topics)

@app.route("/login",methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    sql = "select password from users where username=:username"
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()
    if user == None:
        return render_template("login_failed.html")
    else:
        hash_value = user[0]
        if check_password_hash(hash_value,password):
            session["username"] = username
            return redirect("/")
        else:
            return render_tempalte("login_failed.html")

@app.route("/sign_up1")
def sign_up1():
    return render_template("sign_up.html")

@app.route("/sign_up", methods=["POST"])
def sign_up():
    username = request.form["username"]
    password = request.form["password"]
    hash_value = generate_password_hash(password)
    sql = "select count(*) from users where username=:username or password=:password"
    result = db.session.execute(sql, {"username":username,"password":hash_value})
    result2 = result.fetchone()[0]
    if result2 == 0:
        sql = "insert into users (username, password) values (:username, :password)"
        db.session.execute(sql, {"username":username, "password":hash_value})
        db.session.commit()
        return redirect("/")
    else:
        return render_template("sign_up_failed.html")

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/topic/<int:id>")
def topic(id):
    sql = "select topic from topics where id=:id"
    result = db.session.execute(sql, {"id":id})
    topic = result.fetchone()[0]
    sql = "select id, title from chains where topics_id=:id"
    return render_template("topic.html", topic=topic)

