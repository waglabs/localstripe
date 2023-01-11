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
        capture_method="manual",
        metadata={
            "foo": "bar"
        },
        statement_descriptor_suffix="TEST",
        off_session=True,
        confirm=True
    )
    assert payment_intent['customer'] == customer.id
    assert type(payment_intent.id) is str

    assert stripe.PaymentIntent.retrieve(payment_intent.id)['status'] == 'requires_capture'
    stripe.PaymentIntent.capture(payment_intent.id, statement_descriptor_suffix="CAPTURE")
    assert stripe.PaymentIntent.retrieve(payment_intent.id)['status'] == 'succeeded'
    assert stripe.PaymentIntent.retrieve(payment_intent.id)['statement_descriptor_suffix'] == 'CAPTURE'


def test_automatic_capture_method(faker):
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
    assert type(payment_intent.id) is str

    assert stripe.PaymentIntent.retrieve(payment_intent.id)['status'] == 'succeeded'


def test_invalid_card_failure_on_capture(faker):
    customer = create_customer(faker.email(), 'tok_chargeCustomerFail')
    with pytest.raises(CardError) as card_error:
        stripe.PaymentIntent.create(
            amount=2000,
            currency="usd",
            description="test",
            customer=customer.id,
            capture_method="manual",
            metadata={
                "foo": "bar"
            },
            statement_descriptor_suffix="TEST",
            off_session=True,
            confirm=True
        )

    assert card_error.value.code == 'card_declined'
    assert card_error.value.user_message == 'Your card was declined.'
