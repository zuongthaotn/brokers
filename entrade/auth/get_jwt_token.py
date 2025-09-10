import requests
from pathlib import Path
import json
from telegram_api import send_telegram_message

HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36', 'ContentType': 'application/json'}
ENTRADE_LOGIN_URL = 'https://services.entrade.com.vn/entrade-api/v2/auth'


def doLogin():
    current_dir = Path(__file__).parent
    file = open(str(current_dir) + '/credentials.json', "r")

    # Reading from file
    data = json.loads(file.read())
    username = data['entrade-auth']['email-otp']['username']
    password = data['entrade-auth']['email-otp']['password']

    params = {"username": username, "password": password}

    x = requests.post(ENTRADE_LOGIN_URL, json=params, headers=HEADERS)
    return x.json()


if __name__ == "__main__":
    current_folder = str(Path(__file__).parent)
    login_res = doLogin()
    bearer_token = login_res["token"]
    if bearer_token:
        print("JWT token:")
        print(bearer_token)
        f = open(current_folder + "/jwt_token.txt", "w")
        f.write(bearer_token)
        f.close()
        msg = "Today trading token is generated."
        send_telegram_message(msg)
    else:
        raise Exception("Sorry, The requesting JWT token has problem!")
