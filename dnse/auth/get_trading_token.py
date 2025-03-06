import requests
from pathlib import Path
from telegram_api import send_telegram_message

DNSE_GET_TRADING_TOKEN_URL = 'https://services.entrade.com.vn/dnse-order-service/trading-token'


def request_trading_token(bearer_token, otp):
    header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
        'ContentType': 'application/json',
        'Authorization': 'Bearer ' + bearer_token,
        'otp': otp
    }

    x = requests.post(DNSE_GET_TRADING_TOKEN_URL, headers=header)
    return x.json()


if __name__ == "__main__":
    current_folder = str(Path(__file__).parent)
    f = open(current_folder + "/jwt_token.txt", "r")
    bearer_token = f.read()
    f.close()
    fx = open(current_folder + "/email_otp.txt", "r")
    otp = fx.read()
    fx.close()
    if bearer_token and otp:
        res = request_trading_token(bearer_token, otp)
        print(res)
        if res:
            if 'tradingToken' in res:
                trading_token = res['tradingToken']
                fw = open(current_folder + "/trading_token.txt", "w")
                fw.write(trading_token)
                fw.close()

                import requests

                msg = "Today trading token is generated."
                send_telegram_message(msg)
            else:
                raise Exception("Sorry, The requesting trading token has problem!")