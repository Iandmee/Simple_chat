from requests import Session
import os
base_dir = os.path.abspath(os.path.dirname(__file__))
Options_file = os.path.join(base_dir, "options.bin")
hash_salt = "secret_s2lt"

class Server:
    domain = "207.154.242.118"
    port = "8080"
    secure = False


class Client:
    login = "Guest"
    password = ""
    session = Session()
    chat_id = None
    last_message_id = 0
