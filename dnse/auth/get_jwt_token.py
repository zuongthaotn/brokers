import requests
from pathlib import Path
import json

HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36', 'ContentType': 'application/json'}
DNSE_LOGIN_URL = 'https://services.entrade.com.vn/dnse-auth-service/login'
DNSE_EMAIL_OTP_URL = 'https://services.entrade.com.vn/dnse-auth-service/api/email-otp'


def doLogin():
    current_dir = Path(__file__).parent
    file = open(str(current_dir) + '/credentials.json', "r")

    # Reading from file
    data = json.loads(file.read())
    username = data['dnse-auth']['email-otp']['username']
    password = data['dnse-auth']['email-otp']['password']

    params = {"username": username, "password": password}

    x = requests.post(DNSE_LOGIN_URL, json=params, headers=HEADERS)
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
