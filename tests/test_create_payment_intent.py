import pytest
import json
import stripe
from stripe.error import CardError

from . import create_customer

def test_statement_descriptor_suffix_in_charge_capture(faker):
    customer = create_customer(faker.email(), 'tok_visa')
    payment_intent = stripe.PaymentIntent.create(
        amount=2000,
        currency="usd",
        description="test",
        customer=customer.id,
        capture_method="automatic",
        metadata={
            "foo": "bar"
        },
        statement_descriptor_suffix="TEST",
        off_session=True,
        confirm=True
    )
    assert payment_intent['customer'] == customer.id
