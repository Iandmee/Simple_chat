from typing import Optional
from chat.models import *
from chat import *
from hashlib import sha256
import random, string

def random_str(length) ->str:
    '''
    :param length:
    :return: random string of desired length
    '''
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def check_login_and_password(login:str, password:str)->bool:
    '''
    :param login:
    :param password:
    :return: if login and password - correct
    '''
    return hasattr(User.query.filter_by(login=login, password=sha256((password+hash_salt).encode()).hexdigest()).first(), 'id')

def exists_login(login:str)->bool:
    '''
    :param login:
    :return: if login exists
    '''
    return hasattr(User.query.filter_by(login=login).first(), 'id')
def add_new_user(login:str, password:str)->bool:
    '''
    :param login:
    :param password:
    :return: state of adding new user: success or not
    '''
    success_flag = True
    try:
        new_user = User(login=login, password=sha256((password+hash_salt).encode()).hexdigest())
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        success_flag = False
    return success_flag

def create_new_chat(name:str,password:str)-> Optional[str]:
    '''
    :param name: name of chat
    :param password:
    :return: chat_id of created chat
    '''
    try:
        chat_id = random_str(chat_id_length-1)+'='
        while hasattr(Chat.query.filter_by(chat_id=chat_id), 'id'):
             chat_id = random_str(chat_id_length-1)+'='
        new_chat = Chat(chat_name = name, password = sha256((password + hash_salt).encode()).hexdigest(), chat_id = chat_id)
        db.session.add(new_chat)
        db.session.commit()
        return chat_id
    except Exception as e:
        print(e)
        return None

def check_chat_creds(chat_id:str, password:str) -> Optional[str]:
    '''
    :param chat_id:
    :param password:
    :return: chat_name
    '''
    chat = Chat.query.filter_by(chat_id=chat_id, password=sha256((password + hash_salt).encode()).hexdigest()).first()
    if chat==None:
        return None
    return chat.chat_name

def send(chat_id:str, login:str, message:str)-> bool:
    '''
    :param chat_id:
    :param message:
    :return: state of sending message
    '''
    try:
        chat = Chat.query.filter_by(chat_id=chat_id).first()
        message_to_add = Message(chat_id=chat_id, message_text=message, user_login=login)
        chat.messages.append(message_to_add)
        db.session.add(chat)
        db.session.commit()
        return True
    except Exception as e:
        print(e)
        return False


def get(chat_id:str, count:int = 10) -> Optional[dict]:
    '''
    :param chat_id:
    :param count: count of messages
    :return: list of messages
    '''
    last_message_id=-1
    try:
        messages = Chat.query.filter_by(chat_id=chat_id).first().messages.order_by(Message.id.desc()).limit(count).all()
        messages_text=[]
        for message in messages:
            messages_text.append([message.user_login, message.message_text])
            last_message_id = max(last_message_id, message.id)
        return {"messages": messages_text, "last_message_id": last_message_id}
    except Exception as e:
        print(e)
        return None

def check_messages(chat_id:str,last_message_id:int,current_user_login:str) ->Optional[dict]:
    '''
    Check new messages and return them
    :param chat_id:
    :param last_message_id:
    :return:
    '''
    try:
        messages = Chat.query.filter_by(chat_id=chat_id).first().messages.filter(Message.id> last_message_id).all()
        last_messages=[]
        for message in messages:
            if str(message.user_login) != str(current_user_login):
                last_messages.append([message.user_login, message.message_text])
            last_message_id = max(last_message_id, message.id)
        return {"messages": last_messages, "last_message_id": last_message_id}
    except Exception as e:
        print(e)
        return None