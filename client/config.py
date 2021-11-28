from requests import Session

Options_file = "options.bin"


class Server:
    domain = "localhost"
    port = "1337"
    secure = False


class Client:
    login = "Guest"
    password = ""
    session = Session()
    chat_id = None
    last_message_id = 0
