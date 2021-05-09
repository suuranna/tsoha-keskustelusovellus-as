from werkzeug.security import check_password_hash, generate_password_hash
from app import app
from flask import render_template, redirect, request, session
from db import db
import functions

@app.route("/")
def index():
    topics = functions.get_topics()
    comments = functions.get_the_amount_of_comments_per_topic()
    return render_template("index.html",topics=topics, comments=comments)

@app.route("/login",methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    hashed_password = functions.get_password(username)
    if hashed_password == None:
        return render_template("error.html", message="Käyttäjänimi tai salasana on väärä", route="/")
    else:
        hash_value = hashed_password[0]
        if check_password_hash(hash_value,password):
            session["username"] = username
            session["user_id"] = functions.get_user_id(username)
            session["admin"] = functions.is_admin(username)
            session["permissions"] = functions.get_users_permissions(session["user_id"])
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
    count = functions.count_users_with_same_username(username)
    if count == 0:
        functions.new_user(username, hash_value)
        return redirect("/")
    else:
        return render_template("error.html", message="Käyttäjätunnus on jo käytössä", route="/signing_up")

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/topic/<int:id>")
def topic(id):
    if functions.is_deleted(id, "topic"):
        return render_template("error.html", message="Tämä alue on poistettu", route="/")
    topic = functions.get_topic_title(id)
    chains = functions.get_chains_from_topic(id)
    amount = functions.get_the_amount_of_chains_in_one_topic(id)
    return render_template("topic.html", topic=topic, chains=chains, amount=amount, id=id)

@app.route("/delete_topic/<int:id>")
def delete_topic(id):
    return render_template("delete_topic.html", id=id)

@app.route("/deleting_topic", methods=["POST"])
def deleting_topic():
    id = request.form["id"]
    functions.delete_topic(id)
    return render_template("success.html", message="Alue poistettu onnistuneesti", route="/")

@app.route("/delete_chain/<int:id>")
def delete_chain(id):
    chain = functions.get_chain_opening(id)
    return render_template("delete_chain.html", chain=chain)

@app.route("/delete_comment/<int:id>")
def delete_comment(id):
    comment = functions.get_comment(id)
    return render_template("delete_comment.html", comment=comment, id=id)

@app.route("/deleting_comment", methods=["POST"])
def deleting_comment():
    id = request.form["id"]
    chain_id = request_form["chain_id"]
    functions.delete_comment(id)
    return render_template("success.html", message="Kommentti poistettu onnistuneesti", route="/chain/"+str(chain_id))

@app.route("/deleting_chain", methods=["POST"])
def deleting_chain():
    id = request.form["id"]
    topics_id = request.form["topics_id"]
    functions.delete_chain(id)
    return render_template("success.html", message="Ketju poistettu onnistuneesti", route="/topic/"+str(topics_id))


@app.route("/edit_chain/<int:id>")
def edit_chain(id):
    chain = functions.get_chain_opening(id)
    return render_template("edit_chain.html", chain=chain)

@app.route("/editing_chain/", methods=["POST"])
def editing_chain():
    id = request.form["id"]
    content = request.form["content"]
    title = request.form["title"]
    route = "/edit_chain/"+str(id)
    if len(content) > 150:
        return render_template("error.html", message="Uusi aloitusviesti on liian pitkä", route=route)
    if len(content) == 0:
        return render_template("error.html", message="Ketjulta puuttuu aloitusviesti", route=route)
    if len(title) > 50:
        return render_template("error.html", message="Uusi otsikko on liian pitkä", route=route)
    if len(title) == 0:
        return render_template("error.html", message="Ketjulta puuttuu otsikko", route=route)
    if len(title) == 0 and len(content) == 0:
        return render_template("error.html", message="Ketju ei voi olla tyhjä", route=route)
    functions.edit_chain(id, title, content)
    return render_template("success.html", message="Ketjua muokattu onnistuneesti", route="/chain/"+str(id))

@app.route("/new_comment/<int:id>")
def new_comment(id):
    return render_template("new_comment.html", id=id)

@app.route("/edit_comment/<int:id>")
def edit_comment(id):
    comment = functions.get_comment(id)
    return render_template("edit_comment.html", comment=comment, id=id)

@app.route("/editing_comment", methods=["POST"])
def editing_comment():
    id = request.form["id"]
    content = request.form["content"]
    functions.edit_comment(id, content)
    return render_template("success.html", message="Kommenttia muokattu onnistuneesti")

@app.route("/new_topic")
def new_topic():
    return render_template("new_topic.html")

@app.route("/create_topic", methods=["POST"])
def create_topic():
    topic = request.form["topic"]
    answer = request.form["answer"]
    route = "/new_topic"
    if answer == None:
        return render_template("error.html", message="Valitse onko alue julkinen vai yksityinen", route=route)
    if len(topic) > 30:
        return render_template("error.html", message="Alueen nimi on liian pitkä", route=route)
    if len(topic) == 0:
        return render_template("error.html", message="Anna alueelle nimi", route=route)
    public = True
    if answer == "2":
        public = False
    functions.create_a_new_topic(topic, public)
    return redirect("/")

@app.route("/new_chain/<int:id>")
def new_chain(id):
    return render_template("new_chain.html", id=id)

@app.route("/create_chain", methods=["POST"])
def create_chain():
    id = request.form["id"]
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
    chain_id = functions.create_a_new_chain(id, session["user_id"], title)
    functions.create_a_new_message(content, session["user_id"], chain_id, True)
    return redirect("/topic/"+str(id))

@app.route("/create_comment", methods=["POST"])
def create_comment():
    content = request.form["content"]
    route = "/new_comment/"+str(id)
    if len(content) > 100:
        return render_template("error.html", message="Kommentti on liian pitkä", route=route)
    if len(content) == 0:
        return render_template("error.html", message="Anna kommentille sisältö", route=route)
    functions.create_a_new_message(content, session["user_id"], id, False)
    return redirect("/chain/"+str(id))

@app.route("/chain/<int:id>")
def chain(id):
    if functions.is_deleted(id, "chain"):
        return render_template("error.html", message="Tämä ketju on poistettu", route="/")
    chain_opening = functions.get_chain_opening(id)
    comments = functions.get_comments_of_a_chain(id)
    return render_template("chain.html", id=id, comments=comments, chain_opening=chain_opening)

@app.route("/result")
def result():
    query = request.args["query"]
    messages = functions.find_messages(query, False)
    opening_messages = functions.find_messages(query, True)
    return render_template("result.html", messages=messages, opening_messages=opening_messages)

@app.route("/give_permission/<int:id>")
def give_permission(id):
    return render_template("give_permission.html", id=id)

@app.route("/giving_permission", methods=["POST"])
def giving_permission():
    id = request.form["id"]
    username = request.form["username"]
    user_id = functions.get_user_id(username)
    if user_id != None:
        functions.give_permission(id, user_id)
        return render_template("success.html", message="Oikeudet annettu onnistuneesti")
    else:
        return render_template("error.html", message="Antamasi käyttäjänimi ei vastaa ketään käyttäjää", route="/give_permission/"+str(id))



