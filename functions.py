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
    sql = "select t.id, t.topic, t.public, count(c.topics_id) from topics t left join chains c on t.id=c.topics_id and c.deleted=False group by t.id having t.id in (select id from topics where deleted=False) order by t.id desc"
    result = db.session.execute(sql)
    topics = result.fetchall()
    return topics

def create_a_new_chain(topics_id, user_id, title):
    sql = "insert into chains (topics_id, user_id, title, deleted) values (:topics_id, :user_id, :title, False) returning id"
    result = db.session.execute(sql, {"topics_id":topics_id, "user_id":user_id, "title":title})
    chain_id = result.fetchone()[0]
    db.session.commit()
    return chain_id

def create_a_new_topic(topic, public):
    sql = "insert into topics (topic, public, deleted) values (:topic, :public, False)"
    result = db.session.execute(sql, {"topic":topic, "public":public})
    db.session.commit()

def create_a_new_message(content, user_id, chain_id, begining):
    time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    sql = "insert into messages (content, user_id, posting_date, begining, chain_id, deleted) values (:content, :user_id, :time, :begining, :chain_id, False)"
    result = db.session.execute(sql, {"content":content, "user_id":user_id, "time":time, "begining":begining, "chain_id":chain_id})
    db.session.commit()

def delete_topic(id):
    sql = "update topics set deleted=True where id=:id"
    result = db.session.execute(sql, {"id":id})
    sql = "update chains set deleted=True where topics_id=:id"
    result = db.session.execute(sql, {"id":id})
    sql = "update messages set deleted=True where chain_id in (select id from chains where topics_id=:id)"
    result = db.session.execute(sql, {"id":id})
    db.session.commit()

def delete_chain(id):
    sql = "update chains set deleted=True where id=:id"
    result = db.session.execute(sql, {"id":id})
    sql = "update messages set deleted=True where chain_id=:id"
    result = db.session.execute(sql, {"id":id})
    db.session.commit()

def delete_comment(id):
    sql = "update messages set deleted=True where id=:id"
    result = db.session.execute(sql, {"id":id})
    db.session.commit()

def get_the_amount_of_comments_per_topic():
    sql = "select t.id, count(m.id) from topics t left join chains c on t.id=c.topics_id left join messages m on m.chain_id=c.id and m.begining=False and m.deleted=False group by t.id"
    result = db.session.execute(sql)
    comments = result.fetchall()
    return comments

def get_the_amount_of_chains_in_one_topic(id):
    sql = "select count(topics_id) from chains where deleted=False and topics_id=:id"
    result = db.session.execute(sql, {"id":id})
    chains = result.fetchone()[0]
    return chains

def get_user_id(username):
    sql = "select id from users where username=:username"
    result = db.session.execute(sql, {"username":username})
    user_id = result.fetchone()
    if user_id == None:
        return None
    return user_id[0]

def get_chains_from_topic(id):
    sql = "select c.id, c.title, m.content, m.posting_date, u.username from chains c, messages m, users u where m.chain_id=c.id and m.begining=True and m.user_id=u.id and c.deleted=False and c.topics_id=:id"
    result = db.session.execute(sql, {"id":id})
    chains = result.fetchall()
    return chains

def get_chain_opening(id):
    sql = "select c.topics_id, c.id, c.title, m.content, m.posting_date, u.username, c.deleted from chains c, messages m, users u where m.chain_id=c.id and m.begining=True and m.user_id=u.id and c.id=:id"
    result = db.session.execute(sql, {"id":id})
    chain_opening = result.fetchone()
    return chain_opening

def get_comments_of_a_chain(id):
    sql = "select m.content, u.username, m.posting_date, m.id from messages m, users u where u.id=m.user_id and m.begining=False and m.deleted=False and m.chain_id=:id"
    result = db.session.execute(sql, {"id":id})
    comments = result.fetchall()
    return comments

def get_topic_title(id):
    sql = "select topic, deleted from topics where id=:id"
    result = db.session.execute(sql, {"id":id})
    title = result.fetchone()
    return title

def find_messages(query, begining):
    sql = "select id, content, user_id, posting_date, chain_id from messages where begining=:begining and deleted=False and content LIKE :query"
    result = db.session.execute(sql, {"query":"%"+query+"%", "begining":begining})
    messages = result.fetchall()
    return messages

def edit_chain(id, title, content):
    sql = "update chains set title=:title where id=:id"
    result = db.session.execute(sql, {"title":title, "id":id})
    sql = "update messages set content=:content where chain_id=:id"
    result = db.session.execute(sql, {"content":content, "id":id})
    db.session.commit()

def edit_comment(id, content):
    sql = "update messages set content=:content where id=:id"
    result = db.session.execute(sql, {"content":content, "id":id})
    db.session.commit()

def get_comment(id):
    sql = "select content, user_id, chain_id, deleted from messages where id=:id"
    result = db.session.execute(sql, {"id":id})
    comment = result.fetchone()
    return comment

def give_permission(id, user_id):
    sql = "insert into private_topics_permissions (topics_id, user_id) values (:id, :user_id)"
    result = db.session.execute(sql, {"id":id, "user_id":user_id})
    db.session.commit()

def get_users_permissions(id):
    sql = "select topics_id from private_topics_permissions where user_id=:id"
    result = db.session.execute(sql, {"id":id})
    permissions = result.fetchall()
    permissions_as_list = []
    for permission in permissions:
        permissions_as_list.append(permission[0])
    return permissions_as_list

def is_deleted(id, object):
    if object == "topic":
        sql = "select deleted from topics where id=:id"
        result = db.session.execute(sql, {"id":id})
        deleted = result.fetchone()[0]
        return deleted
    elif object == "chain":
        sql = "select deleted from chains where id=:id"
        result = db.session.execute(sql, {"id":id})
        deleted = result.fetchone()[0]
        return deleted
    else:
        return True

def get_users_with_permission(id):
    sql = "select distinct u.username from private_topics_permissions p, users u where u.id=p.user_id and p.topics_id=:id"
    result = db.session.execute(sql, {"id":id})
    users = result.fetchall()
    return users
