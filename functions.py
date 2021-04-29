from db import db

#def is_admin(username):
#    sql = "select admin from users where username=:username"
#    result = db.session.execute(sql, {"username":username})

#def is_their_message(username, message_id):


def get_user_id(username):
    sql = "select id from users where username=:username"
    result = db.session.execute(sql, {"username":username})
    user_id = result.fetchone()[0]
    return user_id




