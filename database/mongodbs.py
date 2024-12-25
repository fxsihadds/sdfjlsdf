from database.connects import connect_db
from datetime import datetime

mycol = connect_db()


def adduser(_, cmd):
    user_dict = {
        '_id': cmd.from_user.id,
        'fname': cmd.from_user.first_name,
        'lname': cmd.from_user.last_name,
        'is_trial': False,
        'Status': 'p',
        'date': datetime.now()}
    insert = mycol.insert_one(user_dict)


def find_one(id):
    find_user = mycol.find_one({'_id': id})
    return find_user


def is_exsist(id) -> bool:
    exsist = mycol.find_one({'_id': id})
    return True if exsist else False


def total_user():
    ...
