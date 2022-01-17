import os
from datetime import datetime
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


app = Flask(__name__)

db_server = os.environ.get("POSTGRES_SERVER")
db_port = os.environ.get("POSTGRES_PORT")
db_username = os.environ.get("POSTGRES_USER")
db_password = os.environ.get("POSTGRES_PASSWORD")
db_name = os.environ.get("POSTGRES_DB")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{db_username}:{db_password}@{db_server}:{db_port}/{db_name}"
app.config['JSON_SORT_KEYS'] = False
db = SQLAlchemy(app)

class Blacklist(db.Model):
    __tablename__ = "blocked_users"
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(120), unique=True, nullable=False)
    path = db.Column(db.String(120), nullable=False)
    block_date = db.Column(db.DateTime, nullable=False,
        default=datetime.utcnow)

    def __repr__(self):
        return '<IP %r>' % self.ip

    def __init__(self, path, ip):
        self.ip = ip
        self.path = path


def send_email(receiver, text):
    port = int(os.environ.get("SMTP_PORT"))
    smtp_server = os.environ.get("SMTP_SERVER")
    context = ssl.create_default_context()
    sender_email = os.environ.get("SENDER_EMAIL")
    password = os.environ.get("EMAIL_PASSWORD")
    message = MIMEMultipart("alternative")
    message["Subject"] = "Hello from app"
    message["From"] = sender_email
    message["To"] = receiver
    message.attach(MIMEText(text, "plain"))
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver, message.as_string())

@app.before_request
def block_method():
    if request.headers.get("X-Forwarded-For"):
        ip = request.headers.get("X-Forwarded-For")
    else:
        ip = request.environ.get('REMOTE_ADDR')
    if ip in [row.ip for row in db.session.query(Blacklist).all()]:
        abort(403)

@app.route("/unban/", methods = ["GET"])
def unban():
    ip = request.args.get("ip")
    if ip in [row.ip for row in db.session.query(Blacklist).all()]:
        db.session.query(Blacklist).filter(Blacklist.ip == ip).delete()
        db.session.commit()
    else:
        return "We don't have this user in black list", 404
    return "IP {} removed from blacklist".format(ip), 200

@app.route("/blacklisted", methods = ["GET"])
def ban():
    print("Blocked")
    if request.headers.get("X-Forwarded-For"):
        ip = request.headers.get("X-Forwarded-For")
    else:
        ip = request.environ.get('REMOTE_ADDR')
    record = Blacklist(path="/blacklisted", ip=ip)
    db.session.add(record)
    db.session.commit()
    if os.environ.get("SEND_EMAIL").lower() == "true":
        message = "User with IP {} has been blocked".format(ip)
        receiver = os.environ.get("RECEIVER")
        send_email(receiver, message)
    return "Blocked", 444

@app.route("/list_blacklist", methods = ["GET"])
def list_blacklist():
    data = [{"ip": row.ip, "path": row.path, "block_date": row.block_date} for row in db.session.query(Blacklist).all()]

    return jsonify(data), 200

@app.route("/", methods = ["GET"])
def hello():
    parameters = request.args
    keys = parameters.keys()
    for key in keys:
        if key.isnumeric():
            data = {"Result": int(key)*int(key)}
            return jsonify(data), 200
    return "Hello", 200

if __name__ == "__main__":
    db.create_all()
    app.run()

