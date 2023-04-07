from twilio.rest import Client
from core import creds

account_id = creds.ACCOUNT_SID
token = creds.AUTH_TOKEN
from_ = creds.SMS_FROM_


def send_sms(body, to_):
    try:
        client = Client(account_id, token)
        message = client.messages.create(body=body, from_=from_, to="+91" + to_)
        print(message.sid)
        return True, "SMS sent successfully."
    except Exception as ex:
        print("SMS sending failed due to: ", str(ex))
        return False, "SMS sending failed."
