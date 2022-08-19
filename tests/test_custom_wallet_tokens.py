import stripe

from . import create_customer


def test_android_pay_visa_token(faker):
    customer = create_customer(faker.email())
    source: stripe.Card = customer.create_source(customer['id'], source='tok_androidPayVisa')
    assert source['tokenization_method'] == 'android_pay'


def test_apple_pay_visa_token(faker):
    customer = create_customer(faker.email())
    source: stripe.Card = customer.create_source(customer['id'], source='tok_applePayVisa')
    assert source['tokenization_method'] == 'apple_pay'
