from db import db
from datetime import datetime

def is_admin(username):
    sql = "select admin from users where username=:username"
    result = db.session.execute(sql, {"username":username})
    admin = result.fetchone()[0]
    return admin

def get_password(username):
    sql = "select password from users where username=:username"
    result = db.session.execute(sql, {"username":username})
    password = result.fetchone()
    return password

def new_user(username, hashed_password):
    sql = "insert into users (username, password, admin) values (:username, :password, False)"
    db.session.execute(sql, {"username":username, "password":hashed_password})
    db.session.commit()

def count_users_with_same_username(username):
    sql = "select count(*) from users where username=:username"
    result = db.session.execute(sql, {"username":username})
    count = result.fetchone()[0]
    return count

def get_topics():
    #sql = "select t.id, t.topic, t.public, count(c.topics_id) from topics t, chains c where t.id=c.topics_id group by t.id"
    sql = "select t.id, t.topic, t.public, count(c.topics_id) from topics t left join chains c on t.id=c.topics_id group by t.id order by t.id desc"
    result = db.session.execute(sql)
    topics = result.fetchall()
    return topics

def create_a_new_chain(topics_id, user_id, title):
    sql = "insert into chains (topics_id, user_id, title) values (:id, :user_id, :title) returning id"
    result = db.session.execute(sql, {"id":id, "user_id":user_id, "title":title})
    chain_id = result.fetchone()[0]
    db.session.commit()
    return chain_id

def create_a_new_message(content, user_id, chain_id, begining):
    time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    sql = "insert into messages (content, user_id, posting_date, begining, chain_id) values (:content, :user_id, :time, :begining, :chain_id)"
    result = db.session.execute(sql, {"content":content, "user_id":user_id, "time":time, "begining":begining, "chain_id":chain_id})
    db.session.commit()

def get_the_amount_of_comments_per_topic():
    sql = "select t.id, count(m.id) from topics t left join chains c on t.id=c.topics_id left join messages m on m.chain_id=c.id and m.begining=False group by t.id"
    result = db.session.execute(sql)
    comments = result.fetchall()
    return comments

#def get_the_amount_of_chains_per_topic():
#    sql = "select t.id, t.topic, count(c.topics_id) from topics t left join chains c on t.id=c.topics_id group by t.id order by t.id"
#    result db.session.execute(sql)
#    chains = result.fetchall()
#    return chains

def get_the_amount_of_chains_in_one_topic(id):
    sql = "select count(topics_id) from chains where topics_id=:id"
    result = db.session.execute(sql, {"id":id})
    chains = result.fetchone()[0]
    return chains

def get_user_id(username):
    sql = "select id from users where username=:username"
    result = db.session.execute(sql, {"username":username})
    user_id = result.fetchone()[0]
    return user_id

def get_chains_from_topic(id):
    #sql = "select c.id, c.title, m.content, m.posting_date from chains c, messages m where m.chain_id=c.id and m.begining=True and c.topics_id=:id"
    sql = "select c.id, c.title, m.content, m.posting_date, u.username from chains c, messages m, users u where m.chain_id=c.id and m.begining=True and m.user_id=u.id and c.topics_id=:id"
    result = db.session.execute(sql, {"id":id})
    chains = result.fetchall()
    return chains

def get_chain_opening(id):
    sql = "select c.topics_id, c.id, c.title, m.content, m.posting_date, u.username from chains c, messages m, users u where m.chain_id=c.id and m.begining=True and m.user_id=u.id and c.id=:id"
    result = db.session.execute(sql, {"id":id})
    chain_opening = result.fetchone()
    return chain_opening

def get_comments_of_a_chain(id):
    sql = "select m.content, u.username, m.posting_date from messages m, users u where u.id=m.user_id and m.begining=False and m.chain_id=:id"
    result = db.session.execute(sql, {"id":id})
    comments = result.fetchall()
    return comments

def get_topic_title(id):
    sql = "select topic from topics where id=:id"
    result = db.session.execute(sql, {"id":id})
    title = result.fetchone()[0]
    return title


