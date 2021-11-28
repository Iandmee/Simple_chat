import json
from chat.utils import *
from chat.models import *
from chat import app, login_length, password_length
from flask import request, jsonify, session, redirect, url_for
import threading, base64,datetime

@app.route('/login', methods=['POST'])
def login() -> json:
    '''
    Login  process
    :return: json string with success status or non success status
    '''
    try:
        login = request.form['login']
    except Exception as e:
        login = None
        print(e)

    try:
        password = request.form['password']
    except Exception as e:
        password = None
        print(e)
    if login == None or password == None or len(login) > login_length or len(
            password) > password_length or not check_login_and_password(login, password):
        return jsonify(status_message="Invalid login/password!", status=0)
    session['login'] = login
    return jsonify(status_message="Logged in...", status=1)


@app.route('/register', methods=['POST'])
def register() -> json:
    '''
    Register  process
    :return: json string with success status or non success status
    '''
    try:
        login = request.form['login']
    except Exception as e:
        login = None
        print(e)

    try:
        password = request.form['password']
    except Exception as e:
        password = None
        print(e)
    try:
        password_check = request.form['password_check']
    except Exception as e:
        password_check = None
        print(e)
    if login == None or password == None or password_check == None:
        return jsonify(status_message="Invalid Login/Password/Password_check!", status=0)
    if password_check != password:
        return jsonify(status_message="Passwords don't match!", status=0)
    if len(password)>password_length or len(login)>login_length:
        return jsonify(status_message="Password/Login so big!", status=0)
    if exists_login(login):
        return jsonify(status_message="Login exist!", status=0)
    add_new_user(login, password)
    session['login'] = login
    return jsonify(status_message="Registered!", status=1)

@app.route('/connect', methods=['POST'])
def connect() -> json:
    '''
    :return: json string with success status or non success status
    '''
    try:
        chat_id = request.form['chat_id']
    except Exception as e:
        chat_id = None
        print(e)
    try:
        password = request.form['password']
    except Exception as e:
        password = None
        print(e)
    chat_name = check_chat_creds(chat_id, password)
    if chat_id == None or password == None or chat_name == None:
        return jsonify(status_message="Connect failed!", status=0)
    session['chat_id'] = chat_id
    return jsonify(status_message="Connecting...",chat_name=chat_name, status=1)

@app.route('/create', methods=['POST'])
def create() -> json:
    '''
    :return: json string with success status and chat_id or non success status
    '''
    if 'login' not in session.keys():
        return jsonify(status_message="You are not logged in!!!", status=0)

    try:
        chat_name = request.form['chat_name']
    except Exception as e:
        chat_name = None
        print(e)
    try:
        password = request.form['password']
    except Exception as e:
        password = None
        print(e)
    try:
        password_check = request.form['password_check']
    except Exception as e:
        password_check = None
        print(e)
    if chat_name == None or password == None or password_check == None:
        return jsonify(status_message="Invalid Chat_name/Password/Password_check!", status=0)
    if password_check != password:
        return jsonify(status_message="Passwords don't match!", status=0)
    if len(password) > password_length or len(chat_name) > login_length:
        return jsonify(status_message="Password/Chat_name so big!", status=0)
    chat_id = create_new_chat(chat_name, password)
    if chat_id == None:
        return jsonify(status_message="Failed!", status=0)
    return jsonify(status_message="Success!", status=1, chat_id=chat_id)



@app.route('/send_message',methods=['POST'])
def send_message() -> json:
    '''
    :return: status of sending message
    '''
    if 'login' not in session.keys():
        return jsonify(status_message="You are not logged in!!!", status=0)
    if 'chat_id' not in session.keys():
        return jsonify(status_message="You are not in chat!!!", status=0)
    try:
        message = request.form['message']
        check = base64.b64decode(message)
    except Exception as e:
        message = None
        print(e)
    if message == None:
        return jsonify(status_message="Invalid message!", status=0)
    if not send(session['chat_id'], session['login'], message):
        return jsonify(status_message="Something went wrong!", status=0)
    return jsonify(status_message="Success!", status=1)


@app.route('/get_messages', methods=['POST'])
def get_messages() -> json:
    '''
    :return: messages and last_message_id
    '''
    if 'login' not in session.keys():
        return jsonify(status_message="You are not logged in!!!", status=0)
    if 'chat_id' not in session.keys():
        return jsonify(status_message="You are not in chat!!!", status=0)
    try:
        count = request.form['count']
        messages_and_last_message_id = get(session['chat_id'], count)
        return jsonify(status_message="Success!", status=1, messages=messages_and_last_message_id['messages'],last_message_id=messages_and_last_message_id['last_message_id'])
    except Exception as e:
        print(e)
    messages_and_last_message_id = get(session['chat_id'])
    return jsonify(status_message="Success!", status=1, messages=messages_and_last_message_id['messages'],last_message_id=messages_and_last_message_id['last_message_id'])

@app.route('/poll',methods=['POST'])
def poll() -> json:
    '''
    Function for longpoll requests
    :return:
    '''
    if 'login' not in session.keys():
        return jsonify(status_message="You are not logged in!!!", status=0)
    if 'chat_id' not in session.keys():
        return jsonify(status_message="You are not in chat!!!", status=0)
    try:
        last_message_id = request.form['last_message_id']
    except Exception as e:
        last_message_id = None
        print(e)
    for i in range(100):
        messages_and_last_id = check_messages(session['chat_id'], int(last_message_id), session['login'])
        if messages_and_last_id!=None and len(messages_and_last_id['messages'])!=0:
            return jsonify(status_message="Success!", status=1, messages=messages_and_last_id['messages'],last_message_id=messages_and_last_id['last_message_id'])
    return jsonify(status_message="Nothing was found!", status=0)
