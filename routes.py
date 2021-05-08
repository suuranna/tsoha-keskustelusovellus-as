from werkzeug.security import check_password_hash, generate_password_hash
from app import app
from flask import render_template, redirect, request, session
from db import db
import functions

@app.route("/")
def index():
    #sql = "select id, topic from topics where public=True"
    #result = db.session.execute(sql)
    #topics = result.fetchall() OK OK OK
    topics = functions.get_topics()
    comments = functions.get_the_amount_of_comments_per_topic()
    #chains = functions.get_the_amount_of_chains_per_topic()
    return render_template("index.html",topics=topics, comments=comments) # chains=chains)

@app.route("/login",methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    #sql = "select password from users where username=:username"
    #result = db.session.execute(sql, {"username":username})
    #hashed_password = result.fetchone() OK OK OK
    hashed_password = functions.get_password(username)
    if hashed_password == None:
        return render_template("error.html", message="Käyttäjänimi tai salasana on väärä", route="/")
    else:
        hash_value = hashed_password[0]
        if check_password_hash(hash_value,password):
            session["username"] = username
            session["user_id"] = functions.get_user_id(username)
            session["admin"] = functions.is_admin(username)
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
    password_again = request.form["password_again"]
    if username == "" or password == "":
        return render_template("error.html", message="Syötä käyttäjänimi ja salasana", route="/signing_up")
    if len(username) > 14 or len(username) < 6:
       return render_template("error.html", message="Käyttäjänimi ei vastaa pituusvaatimuksia", route="/signing_up")
    if len(password) > 18 or len(password) < 8:
       return render_template("error.html", message="Salasana ei vastaa pituusvaatimuksia", route="/signing_up")
    if password != password_again:
       return render_template("error.html", message="Salasanat eivät täsmää", route="/signing_up")
    hash_value = generate_password_hash(password)
    #sql = "select count(*) from users where username=:username"
    #result = db.session.execute(sql, {"username":username})
    #result2 = result.fetchone()[0] OK OK OK
    count = functions.count_users_with_same_username(username)
    if count == 0:
        functions.new_user(username, hash_value)
        #sql = "insert into users (username, password, admin) values (:username, :password, False)"
        #db.session.execute(sql, {"username":username, "password":hash_value})
        #db.session.commit() OK OK OK
        return redirect("/")
    else:
        return render_template("error.html", message="Käyttäjätunnus on jo käytössä", route="/signing_up")

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/topic/<int:id>")
def topic(id):
    #sql = "select topic, id from topics where id=:id"
    #result = db.session.execute(sql, {"id":id})
    #topic = result.fetchone()
    #sql = "select id, title from chains where topics_id=:id"
    #result = db.session.execute(sql, {"id":id})
    #chains = result.fetchall() OK OK OK
    topic = functions.get_topic_title(id)
    chains = functions.get_chains_from_topic(id)
    #sql = "select content, posting_date, chain_id from messages where begining=True"
    #result = db.session.execute(sql)
    #opening_messages = result.fetchall() OK OK OK
    #sql = "select count(*) from chains where topics_id=:id"
    #result = db.session.execute(sql, {"id":id})
    #amount = result.fetchone()[0] OK OK OK
    amount = functions.get_the_amount_of_chains_in_one_topic(id)
    return render_template("topic.html", topic=topic, chains=chains, amount=amount, id=id)

@app.route("/new_comment/<int:id>")
def new_comment(id):
    return render_template("new_comment.html", id=id)

@app.route("/new_chain/<int:id>")
def new_chain(id):
    return render_template("new_chain.html", id=id)

@app.route("/create_chain/<int:id>", methods=["POST"])
def create_chain(id):
    #username = session["username"] Ok
    #sql = "select id from users where username=:username"
    #result = db.session.execute(sql, {"username":username})
    #user_id = result.fetchone()[0] OK OK OK
    content = request.form["content"]
    title = request.form["title"]

    route = "/new_chain/"+str(id)
    if len(content) > 150:
        return render_template("error.html", message="Aloitusviesti on liian pitkä", route=route)
    if len(content) == 0:
        return render_template("error.html", message="Ketjulta puuttuu aloitusviesti", route=route)
    if len(title) > 50:
        return render_template("error.html", message="Otsikko on liian pitkä", route=route)
    if len(title) == 0:
        return render_template("error.html", message="Ketjulta puuttuu otsikko", route=route)
    if len(title) == 0 and len(content) == 0:
        return render_template("error.html", message="Ei voi julkaista tyhjää ketjua", route=route)
    #sql = "insert into chains (topics_id, user_id, title) values (:id, :user_id, :title) returning id"
    #result = db.session.execute(sql, {"id":id, "user_id":user_id, "title":title})
    #chain_id = result.fetchone()[0] OK OK OK
    chain_id = functions.create_a_new_chain(id, session["user_id"], title)
    functions.create_a_new_message(content, session["user_id"], chain_id, True)
    #sql = "insert into messages (content, user_id, posting_date, begining, chain_id) values 
    #       (:content, :user_id, datetime.now().strftime(%d/%m/%Y, %H:%M:%S), True, :chain_id) returning id"
    #result = db.session.execute(sql, {"content":content, "user_id":user_id, "chain_id":chain_id})
    #db.session.commit() OK OK OK
    return redirect("/topic/"+str(id))

@app.route("/create_comment/<int:id>", methods=["POST"])
def create_comment(id):
    #username = session["username"]
    #sql = "select id from users where username=:username"
    #result = db.session.execute(sql, {"username":username})
    #user_id = result.fetchone()[0]
    content = request.form["content"]

    route = "/new_comment/"+str(id)
    if len(content) > 100:
        return render_template("error.html", message="Kommentti on liian pitkä", route=route)
    if len(content) == 0:
        return render_template("error.html", message="Anna kommentille sisältö", route=route)

    #sql = "insert into messages (content, user_id, posting_date, begining, chain_id) values (:content, :user_id, NOW(), False, :id)"
    #result = db.session.execute(sql, {"content":content, "user_id":user_id, "id":id})
    #db.session.commit() OK OK OK
    functions.create_a_new_message(content, session["user_id"], id, False)
    return redirect("/chain/"+str(id))

@app.route("/chain/<int:id>")
def chain(id):
    #sql = "select user_id from messages where chain_id=:id and begining=True"
    #result = db.session.execute(sql, {"id":id})
    #user_id = result.fetchone()[0]
    #sql = "select username from users where id=:user_id"
    #result = db.session.execute(sql, {"user_id":user_id})
    #username = result.fetchone()[0]
    #sql = "select content, posting_date from messages where chain_id=:id and begining=True"
    #result =db.session.execute(sql, {"id":id})
    #opening_message = result.fetchone()
    #sql = "select title, topics_id from chains where id=:id"
    #result = db.session.execute(sql, {"id":id})
    #title_and_topic_id = result.fetchone()
    #sql = "select content, user_id, posting_date from messages where chain_id=:id and begining=False"
    #result =db.session.execute(sql, {"id":id})
    #messages = result.fetchall()
    #sql = "select id, username from users"
    #result = db.session.execute(sql)
    #usernames = result.fetchall() OK OK OK
    chain_opening = functions.get_chain_opening(id)
    comments = functions.get_comments_of_a_chain(id)
    return render_template("chain.html", id=id, comments=comments, chain_opening=chain_opening)

@app.route("/result")
def result():
    query = request.args["query"]
    sql = "select id, content, user_id, posting_date, chain_id from messages where begining = False and content LIKE :query"
    result = db.session.execute(sql, {"query":"%"+query+"%"})
    messages = result.fetchall()
    sql = "select id, content, user_id, posting_date, chain_id from messages where begining = True and content LIKE :query"
    result = db.session.execute(sql, {"query":"%"+query+"%"})
    opening_messages = result.fetchall()
    return render_template("result.html", messages=messages, opening_messages=opening_messages)

