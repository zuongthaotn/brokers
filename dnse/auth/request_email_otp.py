import requests
from pathlib import Path

DNSE_EMAIL_OTP_URL = 'https://services.entrade.com.vn/dnse-auth-service/api/email-otp'


def request_email_otp(token):
    header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36', 'ContentType': 'application/json', 'Authorization': 'Bearer ' + token}

    x = requests.get(DNSE_EMAIL_OTP_URL, headers=header)
    return x


if __name__ == "__main__":
    current_folder = str(Path(__file__).parent)
    f = open(current_folder + "/jwt_token.txt", "r")
    bearer_token = f.read()
    f.close()
    if bearer_token:
        print("Requesting email otp token......")
        request_email_otp(bearer_token)
        print("Requested email otp token. Waiting 55s.")
