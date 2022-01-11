from datetime import datetime
import itertools
from flask import Flask, request, abort
import sqlite3

app = Flask(__name__)
db = "temp.db"

def db_init():
    try:
        sqlite_connection = sqlite3.connect(db)
        cursor = sqlite_connection.cursor()

        sqlite_select_query = "select sqlite_version();"
        cursor.execute(sqlite_select_query)
        record = cursor.fetchall()
        print("DB_version is ", record)
        cursor.close()
        sqlite_create_table_query = '''CREATE TABLE IF NOT EXISTS blocked_users (
                                    id INTEGER PRIMARY KEY,
                                    path TEXT NOT NULL,
                                    IP text NOT NULL UNIQUE,
                                    block_date datetime);'''

        cursor = sqlite_connection.cursor()
        print("connected to sql")
        cursor.execute(sqlite_create_table_query)
        sqlite_connection.commit()
        print("Table is created")

        cursor.close()
    except sqlite3.Error as error:
        print("Error connection to sqlite", error)

    finally:
        if (sqlite_connection):
            sqlite_connection.close()
            print("DB connection closed")

def add_blocked_user(path, ip):
    try:
        sqlite_connection = sqlite3.connect(db)
        record = """INSERT INTO blocked_users(path, IP, block_date )  
        VALUES  ('{}', '{}', '{}')""".format(path, ip, datetime.now())
        cursor = sqlite_connection.cursor()
        cursor.execute(record)
        sqlite_connection.commit()
    except sqlite3.Error as error:
        print("Error connection to sqlite", error)

    finally:
        if (sqlite_connection):
            sqlite_connection.close()
            print("DB connection closed")

def get_blocked_users():
    try:
        sqlite_connection = sqlite3.connect(db)
        select = """select * from blocked_users"""
        cursor = sqlite_connection.cursor()
        cursor.execute(select)
        desc = cursor.description
        column_names = [col[0] for col in desc]
        data = [dict(itertools.zip_longest(column_names, row))
                for row in cursor.fetchall()]
        ip_list = [record["IP"] for record in data]
    except sqlite3.Error as error:
        print("Error connection to sqlite", error)

    finally:
        if (sqlite_connection):
            sqlite_connection.close()
            print("DB connection closed")

    global banned_users, ip_ban_list
    banned_users = data
    ip_ban_list = ip_list

def remove_user(ip):
    try:
        sqlite_connection = sqlite3.connect(db)
        sql = """DELETE FROM blocked_users WHERE IP=?"""
        cursor = sqlite_connection.cursor()
        cursor.execute(sql, (ip,))
        sqlite_connection.commit()
    except sqlite3.Error as error:
        print("Error connection to sqlite", error)

    finally:
        if (sqlite_connection):
            sqlite_connection.close()
            print("DB connection closed")

@app.before_request
def block_method():
    if request.headers.get("X-Forwarded-For"):
        ip = request.headers.get("X-Forwarded-For")
    else:
        ip = request.environ.get('REMOTE_ADDR')
    if ip in ip_ban_list:
        abort(403)

@app.route("/unban/", methods = ["GET"])
def unban():
    ip = request.args.get("ip")
    if ip in ip_ban_list:
        remove_user(ip)
    else:
        return "We don't have this user in black list", 404
    get_blocked_users()
    return "IP {} removed from blacklist".format(ip), 200

@app.route("/blacklisted", methods = ["GET"])
def ban():
    print("Blocked")
    if request.headers.get("X-Forwarded-For"):
        ip = request.headers.get("X-Forwarded-For")
    else:
        ip = request.environ.get('REMOTE_ADDR')
    add_blocked_user("blacklisted", ip)
    get_blocked_users()
    return "Blocked", 444

@app.route("/list_blacklist", methods = ["GET"])
def list_blacklist():

    return str(banned_users), 200

@app.route("/", methods = ["GET"])
def hello():
    parameters = request.args
    keys = parameters.keys()
    for key in keys:
        if key.isnumeric():
            return str(int(key)*int(key)), 200
    return "Hello", 200

if __name__ == "__main__":
    db_init()
    get_blocked_users()
    app.run()

