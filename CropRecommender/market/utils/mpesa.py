# THE UTILS FOLDER WAS IMPLEMENTED BY ME FOR MPESA SO YOU CAN ALSO DELETE IT
# farmers/utils/mpesa.py
import requests
import base64
from datetime import datetime
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def get_mpesa_access_token():
    """Obtain OAuth access token from M-Pesa."""
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    auth = base64.b64encode(
        f"{settings.MPESA_CONSUMER_KEY}:{settings.MPESA_CONSUMER_SECRET}".encode()
    ).decode()
    headers = {"Authorization": f"Basic {auth}"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get("access_token")
    except requests.RequestException as e:
        logger.error(f"Failed to get M-Pesa access token: {str(e)}")
        raise Exception("Unable to authenticate with M-Pesa API")

def initiate_stk_push(phone_number, amount, order_id, callback_url):
    """Initiate STK Push payment."""
    access_token = get_mpesa_access_token()
    url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode(
        f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}".encode()
    ).decode()

    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),  # M-Pesa requires integer amounts
        "PartyA": phone_number,  # Customer's phone number
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": callback_url,
        "AccountReference": f"Order {order_id}",
        "TransactionDesc": f"Payment for Order {order_id}"
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Failed to initiate STK Push: {str(e)}")
        raise Exception("Unable to initiate STK Push")