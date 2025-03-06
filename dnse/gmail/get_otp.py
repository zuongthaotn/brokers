import os
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def get_otp(service, message_id):
    # Get the latest message
    msg = service.users().messages().get(userId='me', id=message_id).execute()

    # Get value of 'payload' from dictionary 'txt'
    payload = msg['payload']
    headers = payload['headers']

    # Look for OTP in the body
    otp = None
    for part in payload.get('parts', []):
        body = part.get('body', {}).get('data', '')
        content = str(base64.urlsafe_b64decode(body + '==='))
        words = content.split('\\r\\n\\r\\n')
        otp = words[2]
        break

    return otp


def mark_read_email(service, message_id):
    service.users().messages().modify(userId='me', id=message_id, body={'removeLabelIds': ['UNREAD']}).execute()


def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    data_path = os.path.dirname(__file__)
    if os.path.exists(data_path + '/token.json'):
        creds = Credentials.from_authorized_user_file(data_path + '/token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                data_path + '/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(data_path + '/token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)
        result = service.users().messages().list(userId='me', q='from:noreply@mail.dnse.com.vn').execute()
        last_message_id = result['messages'][0]['id']
        otp = get_otp(service, last_message_id)
        if otp:
            print("OTP: \n")
            print(otp)
            print("\n")
            from pathlib import Path
            auth_folder = str(Path(__file__).parent.parent)
            f = open(auth_folder + "/auth/email_otp.txt", "w")
            f.write(otp)
            f.close()

    except HttpError as error:
        # Handle errors from gmail API.
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()
