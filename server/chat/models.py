from chat import *


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(login_length), unique=True, nullable=False)
    password = db.Column(db.String(password_length), unique=False, nullable=False)
    messages = db.relationship("Message", backref="user", lazy="dynamic")


class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_name = db.Column(db.String(chat_name_length), unique=False, nullable=False)
    password = db.Column(db.String(password_length), unique=False, nullable=False)
    messages = db.relationship("Message", backref="chat", lazy="dynamic")
    chat_id = db.Column(db.String(password_length), unique=True, nullable=False)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey("chat.chat_id"))
    message_text = db.Column(db.String(500), unique=False, nullable=False)
    user_login = db.Column(db.Integer, db.ForeignKey("user.login"))
