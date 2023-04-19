import json
import logging

import requests

from core import creds
from core.helpers.decorators import handle_unknown_exception

PAYMENT_LINK_BASE_URL = "https://sandbox.cashfree.com/pg/links"
LOGGER = logging.getLogger(__name__)


@handle_unknown_exception(logger=LOGGER)
def create_payment_link(link_id, link_amount, link_purpose, customer, expiry_time):
    payload = json.dumps(
        {
            "link_id": link_id,
            "link_amount": int(link_amount),
            "link_currency": "INR",
            "link_purpose": link_purpose,
            "customer_details": {
                "customer_phone": customer.mobile_number,
                "customer_name": customer.full_name,
                "customer_email": customer.email,
            },
            "link_expiry_time": str(expiry_time),
            "link_notify": {"send_email": True, "send_sms": True},
        }
    )
    headers = {
        "x-client-id": creds.PAYMENT_LINK_CLIENT_ID,
        "x-client-secret": creds.PAYMENT_LINK_CLIENT_SECRET,
        "x-api-version": "2022-09-01",
        "Content-Type": "application/json",
    }

    response = requests.request(
        "POST", PAYMENT_LINK_BASE_URL, headers=headers, data=payload
    )

    return True, response
