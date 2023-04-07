from django.core.mail import send_mail
from core import constants


def send_email(subject, message, receivers=[]):
    try:
        send_mail(
            subject,
            message,
            constants.EMAIL_SENDER,
            receivers,
            fail_silently=False,
        )
        return True, "EMail sent successfully."
    except Exception as ex:
        print("EMail sending failed due to: ", str(ex))
        return False, "EMail sending failed."
