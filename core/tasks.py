from celery import shared_task
from core.services.email import send_email
from core.services.sms import send_sms
from core import constants


@shared_task
def send_email_task(subject, message, receivers=[]):
    success, response = send_email(subject, message, receivers)
    print("Success and Response for send email task: ", success, response)
    return True, "EMail sent successfully."


@shared_task
def send_sms_task(message, mobile_number):
    success, response = send_sms(
        body=message,
        to_=mobile_number,
    )
    print("Success and Response for send sms task: ", success, response)
    return True, "SMS sent successfully."
