import stripe
import os
import requests


def init_stripe():
    stripe.api_base = os.environ.get('STRIPE_BASE_URL') or "http://localhost:8420"
    stripe.api_key = os.environ.get('STRIPE_SECRET_KEY') or "sk_test_12345"


def create_customer(email, card_token=None) -> stripe.Customer:
    customer = stripe.Customer.create(
        email=email
    )
    assert isinstance(customer, stripe.Customer)
    if card_token is not None:
        customer.create_source(customer['id'], source=card_token)
    return customer
