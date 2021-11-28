import json, base64, threading, sys
from config import *
import colorama
from colorama import Style
from termcolor import colored
from time import sleep

colorama.init(autoreset=True)


def get_url() -> str:
    """
    :return: built url
    """
    if Server.secure:
        return f"https://{Server.domain}:{Server.port}"
    else:
        return f"http://{Server.domain}:{Server.port}"


def get_options() -> dict:
    """
    :return: saved options or None
    """
    try:
        file = open(Options_file, "r")
        data = base64.b64decode(file.readline().strip().encode()).decode()
        options = json.loads(data)
        file.close()
        return options
    except Exception as e:
        return {}


def set_options(**kwargs) -> bool:
    """
    :param kwargs:
    :return: state of setting options
    """
    try:
        current_options = get_options()
        update = kwargs
        for option, value in update.items():
            current_options[option] = value
        file_with_options = open(Options_file, "w")
        file_with_options.writelines(
            base64.b64encode(json.dumps(current_options).encode()).decode() + "\n"
        )
        file_with_options.close()
        return True
    except Exception as e:
        pass
    return False


def api(**kwargs) -> json:
    """
    Function for api server using
    :param kwargs:
    :return: json response from server
    """
    data = kwargs
    if "login" in data.values():
        return Client.session.post(
            get_url() + "/login",
            data={"login": data["login"], "password": data["password"]},
        ).text
    if "register" in data.values():
        return Client.session.post(
            get_url() + "/register",
            data={
                "login": data["login"],
                "password": data["password"],
                "password_check": data["password_check"],
            },
        ).text
    if "connect" in data.values():
        return Client.session.post(
            get_url() + "/connect",
            data={"chat_id": data["chat_id"], "password": data["password"]},
        ).text
    if "create" in data.values():
        return Client.session.post(
            get_url() + "/create",
            data={
                "chat_name": data["chat_name"],
                "password": data["password"],
                "password_check": data["password_check"],
            },
        ).text
    if "send_message" in data.values():
        return Client.session.post(
            get_url() + "/send_message", data={"message": data["message"]}
        ).text
    if "get_messages" in data.values():
        if "count" in data.keys():
            return Client.session.post(
                get_url() + "/get_messages", data={"count": data["count"]}
            ).text
        else:
            return Client.session.post(get_url() + "/get_messages").text
    if "poll" in data.values():
        return Client.session.post(
            get_url() + "/poll", data={"last_message_id": data["last_message_id"]}
        ).text


def print_initial_menu() -> None:
    """
    Just print initial menu
    :param logged_in:
    :return: None
    """
    print(colored("### S3cur3 Ch2t ###", "magenta"))
    print(colored("1. ", "cyan") + "Sign in")
    print(colored("2. ", "cyan") + "Register")
    print(colored("3. ", "cyan") + "Options")
    print(colored("4. ", "cyan") + "Exit")


def print_logged_in_menu() -> None:
    """
    Just print initial menu
    :param logged_in:
    :return: None
    """
    print(
        colored("### ", "magenta")
        + colored("Us3r: ", "cyan")
        + Style.BRIGHT
        + colored(Client.login, "green")
        + Style.RESET_ALL
        + colored(" ###", "magenta")
    )
    print(colored("1. ", "cyan") + "Connect to chat")
    print(colored("2. ", "cyan") + "Create chat")
    print(colored("3. ", "cyan") + "Logout")


def print_settings_menu() -> None:
    """
    Just print settings menu
    :return:
    """
    print(
        colored("### ", "magenta")
        + colored("Options", "cyan")
        + colored(" ###", "magenta")
    )
    print(
        colored("1. ", "cyan") + "Server ip/domain: " + colored(Server.domain, "green")
    )
    print(colored("2. ", "cyan") + "Server port: " + colored(Server.port, "green"))
    if Server.secure:
        print(colored("3. ", "cyan") + "Https: " + colored("True", "green"))
    else:
        print(colored("3. ", "cyan") + "Https: " + colored("False", "red"))
    print(colored("4. ", "cyan") + "Save for next times")
    print(colored("5. ", "cyan") + "Go back")


def print_messages() -> None:
    """
    Checking and printing new messages in chat
    :return:
    """
    poll = threading.currentThread()
    while getattr(poll, "do_run", True):
        try:
            messages = json.loads(
                api(last_message_id=Client.last_message_id, type="poll")
            )
            if len(messages["messages"]) > 0:
                print("\n", end="")
                print(
                    "\033[A                             \033[A"
                )  # for deleting previous string in console
                for user, message in messages["messages"]:
                    print(
                        colored(f"({user})", "blue")
                        + Style.BRIGHT
                        + colored("> ", "cyan")
                        + base64.b64decode(message.encode()).decode()
                    )
                Client.last_message_id = messages["last_message_id"]
                print(
                    Style.BRIGHT
                    + colored(f"({Client.login})", "green")
                    + colored("> ", "cyan"),
                    end="",
                )
        except Exception as e:
            pass
        sleep(1)


def chat_session(chat_name: str) -> None:
    """
    Chat session
    :return:
    """
    print(
        colored("### ", "magenta")
        + Style.BRIGHT
        + colored(f"Ch2t: {chat_name} ", "cyan")
        + Style.RESET_ALL
        + colored(" ###", "magenta")
    )
    try:
        messages_and_last_message_id = json.loads(api(count=20, type="get_messages"))
        Client.last_message_id = messages_and_last_message_id["last_message_id"]
        if messages_and_last_message_id["status"]:
            for user, message in reversed(messages_and_last_message_id["messages"]):
                print(
                    colored(f"({user})", "blue")
                    + Style.BRIGHT
                    + colored("> ", "cyan")
                    + base64.b64decode(message.encode()).decode()
                )
        else:
            print(
                Style.BRIGHT
                + colored(messages_and_last_message_id["status_message"], "red")
            )
            Client.chat_id = None
            return None
    except Exception as e:
        print(Style.BRIGHT + colored("Some error occurred!", "red"))
        Client.chat_id = None
        return None

    poll = threading.Thread(target=print_messages)
    poll.start()
    while 1:
        try:
            print(
                Style.BRIGHT
                + colored(f"({Client.login})", "green")
                + colored("> ", "cyan"),
                end="",
            )
            user_message = sys.stdin.readline().strip()
            print(
                "\033[A                             \033[A"
            )  # for deleting previous string in console
            if user_message == "#Exit".lower():
                Client.chat_id = None
                poll.do_run = False
                break
            status = json.loads(
                api(
                    message=base64.b64encode(user_message.encode()).decode(),
                    type="send_message",
                )
            )
            if status["status"]:
                print(
                    colored(f"({Client.login})", "blue")
                    + Style.BRIGHT
                    + colored("> ", "cyan")
                    + user_message
                )
            else:
                print(Style.BRIGHT + colored(status["status_message"], "red"))
        except Exception as e:
            print(Style.BRIGHT + colored("Message didn't send!", "red"))


def logged_in() -> None:
    """
    Initial function when user logged in
    :return:
    """
    while 1:
        try:
            print_logged_in_menu()
            print(colored("> ", "cyan"), end="")
            user_input = sys.stdin.readline().strip()
            if user_input == "1":
                print("Chat_id: ", end="")
                chat_id = sys.stdin.readline().strip()
                print("Password: ", end="")
                password = sys.stdin.readline().strip()
                status = json.loads(
                    api(chat_id=chat_id, password=password, type="connect")
                )
                if status["status"]:
                    print(Style.BRIGHT + colored(status["status_message"], "green"))
                    Client.chat_id = chat_id
                    chat_session(status["chat_name"])
                else:
                    print(Style.BRIGHT + colored(status["status_message"], "red"))

            elif user_input == "2":
                print("Chat_name: ", end="")
                chat_name = sys.stdin.readline().strip()
                print("Password_check: ", end="")
                password = sys.stdin.readline().strip()
                print("Password_check: ", end="")
                password_check = sys.stdin.readline().strip()
                status = json.loads(
                    api(
                        chat_name=chat_name,
                        password=password,
                        password_check=password_check,
                        type="create",
                    )
                )
                if status["status"]:
                    print(Style.BRIGHT + colored(status["status_message"], "green"))
                    print(
                        Style.BRIGHT
                        + colored("(REMEMBER IT!)", "red")
                        + colored(f"Your chat_id: {status['chat_id']}")
                    )
                else:
                    print(Style.BRIGHT + colored(status["status_message"], "red"))
            elif user_input == "3":
                print(colored("Logged out", "blue"))
                Client.session.close()
                break
            else:
                print(colored("Incorrect number!", "red"))
        except Exception as e:
            print(Style.BRIGHT + colored("Some error occurred!", "red"))


def recover_session(options: dict) -> bool:
    """
    Try to recover last session using creds from file
    :param options:
    :return:  state of recovering
    """
    if "login" in options.keys() and "password" in options.keys():
        Client.login = options["login"]
        Client.password = options["password"]
        print(colored("Load saved user?(Y/n): ", "cyan"), end="")
        user_input = sys.stdin.readline().strip()
        if user_input == "Y":
            try:
                status = json.loads(
                    api(login=Client.login, password=Client.password, type="login")
                )
                if status["status"]:
                    print(Style.BRIGHT + colored(status["status_message"], "green"))
                else:
                    print(Style.BRIGHT + colored(status["status_message"], "red"))
                return status["status"]
            except Exception as e:
                print(Style.BRIGHT + colored("Some error occurred!", "red"))
    return False


def save_creds_question() -> None:
    """
    Try to save creds in file
    :return:
    """
    print(
        Style.BRIGHT
        + colored("(Unsafe!)", "red")
        + "Save your login and password?(Y/n): ",
        end="",
    )
    user_input = sys.stdin.readline().strip()
    if user_input == "Y":
        if set_options(login=Client.login, password=Client.password):
            print(Style.BRIGHT + colored("Saved!", "green"))


def options_setting() -> None:
    """
    Options setting main function
    :return:
    """
    while 1:
        try:
            print_settings_menu()
            print("Change/Choose option" + Style.BRIGHT + colored("> ", "cyan"), end="")
            user_input = sys.stdin.readline().strip()
            if user_input == "1":
                print("New domain: ", end="")
                new_server_domain = sys.stdin.readline().strip()
                Server.domain = new_server_domain
                print(Style.BRIGHT + colored("Success!", "green"))
            elif user_input == "2":
                print("New server port(\"Enter\" for empty): ", end="")
                new_server_port = sys.stdin.readline().strip()
                Server.port = new_server_port
                print(Style.BRIGHT + colored("Success!", "green"))
            elif user_input == "3":
                Server.secure = not Server.secure
                print(Style.BRIGHT + colored("Success!", "green"))
            elif user_input == "4":
                if set_options(
                    domain=Server.domain, port=Server.port, secure=Server.secure
                ):
                    print(Style.BRIGHT + colored("Saved!", "green"))
                else:
                    print(Style.BRIGHT + colored("Failed to save!", "red"))
            elif user_input == "5":
                break
            else:
                print(Style.BRIGHT + colored("Invalid number!", "red"))
        except Exception as e:
            print(Style.BRIGHT + colored("Some error occurred!", "red"))


def main_func() -> None:
    """
    Main body of client script
    :return:
    """

    try:
        options = get_options()
        if "domain" in options.keys():
            Server.domain = options["domain"]
        if "port" in options.keys():
            Server.port = options["port"]
        if "secure" in options.keys():
            Server.secure = options["secure"]
        if recover_session(options):
            logged_in()
    except Exception as e:
        pass

    while 1:
        try:
            print_initial_menu()
            print(Style.BRIGHT + colored("> ", "cyan"), end="")
            user_input = sys.stdin.readline().strip()

            if user_input == "1":
                print(colored("### Login form ###", "magenta"))
                print("Login: ", end="")
                Client.login = sys.stdin.readline().strip()
                print("Password: ", end="")
                Client.password = sys.stdin.readline().strip()
                status = json.loads(
                    api(login=Client.login, password=Client.password, type="login")
                )
                if status["status"]:
                    print(Style.BRIGHT + colored(status["status_message"], "green"))
                    save_creds_question()
                    logged_in()
                else:
                    print(Style.BRIGHT + colored(status["status_message"], "red"))

            elif user_input == "2":
                print(colored("### Register form ###", "magenta"))
                print("Login: ", end="")
                Client.login = sys.stdin.readline().strip()
                print("Password: ", end="")
                Client.password = sys.stdin.readline().strip()
                print("Repeat Password: ", end="")
                password_check = sys.stdin.readline().strip()
                status = json.loads(
                    api(
                        login=Client.login,
                        password=Client.password,
                        password_check=password_check,
                        type="register",
                    )
                )
                if status["status"]:
                    print(Style.BRIGHT + colored(status["status_message"], "green"))
                    save_creds_question()
                    logged_in()
                else:
                    print(Style.BRIGHT + colored(status["status_message"], "red"))

            elif user_input == "3":
                options_setting()
            elif user_input == "4":
                print(colored("Exiting...", "blue"))
                exit(0)
            else:
                print(colored("Incorrect number!", "red"))
        except Exception as e:
            print(Style.BRIGHT + colored("Some error occurred!", "red"))


if __name__ == "__main__":
    main_func()
