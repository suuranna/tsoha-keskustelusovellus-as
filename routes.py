from werkzeug.security import check_password_hash, generate_password_hash
from app import app
from flask import render_template, redirect, request, session
from db import db

@app.route("/")
def index():
    sql = "select id, topic from topics where public=True"
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
        return render_template("error.html", message="Käyttäjänimi tai salasana on väärä", route="/")
    else:
        hash_value = user[0]
        if check_password_hash(hash_value,password):
            session["username"] = username
            return redirect("/")
        else:
            return render_template("error.html", message="Käyttäjänimi tai salasana on väärä", route="/")

@app.route("/signing_up")
def signing_up():
    return render_template("sign_up.html")

@app.route("/sign_up", methods=["POST"])
def sign_up():
    username = request.form["username"]
    password = request.form["password"]
    if username == "" or password == "":
        return render_template("error.html", message="Syötä käyttäjänimi ja salasana", route="/signing_up")
    hash_value = generate_password_hash(password)
    sql = "select count(*) from users where username=:username or password=:password"
    result = db.session.execute(sql, {"username":username,"password":hash_value})
    result2 = result.fetchone()[0]
    if result2 == 0:
        sql = "insert into users (username, password, admin) values (:username, :password, False)"
        db.session.execute(sql, {"username":username, "password":hash_value})
        db.session.commit()
        return redirect("/")
    else:
        return render_template("error.html", message="Käyttäjätunnus tai salasana on jo käytössä", route="/signing_up")

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/topic/<int:id>")
def topic(id):
    sql = "select topic, id from topics where id=:id"
    result = db.session.execute(sql, {"id":id})
    topic = result.fetchone()
    sql = "select id, title from chains where topics_id=:id"
    result = db.session.execute(sql, {"id":id})
    chains = result.fetchall()
    sql = "select content, posting_date, chain_id from messages where begining=True"
    result = db.session.execute(sql)
    opening_messages = result.fetchall()
    sql = "select count(*) from chains where topics_id=:id"
    result = db.session.execute(sql, {"id":id})
    amount = result.fetchone()[0]
    return render_template("topic.html", topic=topic, chains=chains, opening_messages=opening_messages, amount=amount, id=id)

@app.route("/new_comment/<int:id>")
def new_comment(id):
    return render_template("new_comment.html", id=id)

@app.route("/new_chain/<int:id>")
def new_chain(id):
    return render_template("new_chain.html", id=id)

@app.route("/create_chain/<int:id>", methods=["POST"])
def create_chain(id):
    username = session["username"]
    sql = "select id from users where username=:username"
    result = db.session.execute(sql, {"username":username})
    user_id = result.fetchone()[0]
    content = request.form["content"]

    route = "/new_chain/"+str(id)
    if len(content) > 100:
        return render_template("error.html", message="Aloitusviesti on liian pitkä", route=route)
    if len(content) == 0:
        return render_template("error.html", message="Ketjulta puuttuu aloitusviesti", route=route)
    title = request.form["title"]
    if len(title) > 50:
        return render_template("error.html", message="Otsikko on liian pitkä", route=route)
    if len(title) == 0:
        return render_template("error.html", message="Ketjulta puuttuu otsikko", route=route)
    if len(title) == 0 and len(content) == 0:
        return render_template("error.html", message="Ei voi julkaista tyhjää ketjua", route=route)


    sql = "insert into chains (topics_id, user_id, title) values (:id, :user_id, :title) returning id"
    result = db.session.execute(sql, {"id":id, "user_id":user_id, "title":title})
    chain_id = result.fetchone()[0]
    sql = "insert into messages (content, user_id, posting_date, begining, chain_id) values (:content, :user_id, NOW(), True, :chain_id) returning id"
    result = db.session.execute(sql, {"content":content, "user_id":user_id, "chain_id":chain_id})
    db.session.commit()
    return redirect("/topic/"+str(id))

@app.route("/create_comment/<int:id>", methods=["POST"])
def create_comment(id):
    username = session["username"]
    sql = "select id from users where username=:username"
    result = db.session.execute(sql, {"username":username})
    user_id = result.fetchone()[0]
    content = request.form["content"]

    route = "/chain/"+str(id)
    if len(content) > 100:
        return render_template("error.html", message="Kommentti on liian pitkä", route=route)
    if len(content) == 0:
        return render_template("error.html", message="Anna kommentille sisältö", route=route)

    sql = "insert into messages (content, user_id, posting_date, begining, chain_id) values (:content, :user_id, NOW(), False, :id)"
    result = db.session.execute(sql, {"content":content, "user_id":user_id, "id":id})
    db.session.commit()
    return redirect("/chain/"+str(id))

@app.route("/chain/<int:id>")
def chain(id):
    sql = "select user_id from messages where chain_id=:id and begining=True"
    result = db.session.execute(sql, {"id":id})
    user_id = result.fetchone()[0]
    sql = "select username from users where id=:user_id"
    result = db.session.execute(sql, {"user_id":user_id})
    username = result.fetchone()[0]
    sql = "select content, posting_date from messages where chain_id=:id and begining=True"
    result =db.session.execute(sql, {"id":id})
    opening_message = result.fetchone()
    sql = "select title from chains where id=:id"
    result = db.session.execute(sql, {"id":id})
    title = result.fetchone()[0]
    sql = "select content, user_id, posting_date from messages where chain_id=:id and begining=False"
    result =db.session.execute(sql, {"id":id})
    messages = result.fetchall()
    sql = "select id, username from users"
    result = db.session.execute(sql)
    usernames = result.fetchall()
    return render_template("chain.html", id=id, username=username, opening_message=opening_message, title=title, messages=messages, usernames=usernames)

