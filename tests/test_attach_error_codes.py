import pytest
import json
import stripe
from stripe.error import CardError

from . import create_customer


def test_attach_error_on_stolen_card_token(faker):
    customer = create_customer(faker.email())
    with pytest.raises(CardError) as card_error:
        customer.create_source(customer['id'], source='tok_visa_chargeDeclinedStolenCard')

    assert card_error.value.code == 'card_declined'
    assert card_error.value.user_message == 'Your card was declined.'
    assert json.loads(card_error.value.http_body)['error']['decline_code'] == 'stolen_card'


def test_attach_no_error_on_charge_fail_later_token(faker):
    customer = create_customer(faker.email())
    source: stripe.Card = customer.create_source(customer['id'], source='tok_chargeCustomerFail')
    assert source['last4'] == '0341'
