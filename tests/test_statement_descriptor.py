import stripe

from . import create_customer


def test_statement_descriptor_suffix_in_charge_create(faker):
    customer = create_customer(faker.email(), 'tok_visa')
    charge: stripe.Charge = stripe.Charge.create(
        customer=customer['id'],
        amount=1000,
        currency='usd',
        capture=False,
        statement_descriptor_suffix='temp-hold'
    )
    assert charge['statement_descriptor_suffix'] == 'temp-hold'


def test_statement_descriptor_suffix_in_charge_capture(faker):
    customer = create_customer(faker.email(), 'tok_visa')

    charge: stripe.Charge = stripe.Charge.create(
        customer=customer['id'],
        amount=1000,
        currency='usd',
        capture=False,
        statement_descriptor_suffix='temp-hold'
    )
    assert charge['statement_descriptor_suffix'] == 'temp-hold'

    charge.capture(
        amount=1000,
        statement_descriptor_suffix='captured'
    )

    charge = stripe.Charge.retrieve(charge['id'])

    assert charge['statement_descriptor_suffix'] == 'captured'


def test_statement_descriptor_in_charge_create(faker):
    customer = create_customer(faker.email(), 'tok_visa')
    charge: stripe.Charge = stripe.Charge.create(
        customer=customer['id'],
        amount=1000,
        currency='usd',
        capture=False,
        statement_descriptor='temp-hold'
    )
    assert charge['statement_descriptor'] == 'temp-hold'


def test_statement_descriptor_in_charge_capture(faker):
    customer = create_customer(faker.email(), 'tok_visa')

    charge: stripe.Charge = stripe.Charge.create(
        customer=customer['id'],
        amount=1000,
        currency='usd',
        capture=False,
        statement_descriptor='temp-hold'
    )
    assert charge['statement_descriptor'] == 'temp-hold'

    charge.capture(
        amount=1000,
        statement_descriptor='captured'
    )

    charge = stripe.Charge.retrieve(charge['id'])

    assert charge['statement_descriptor'] == 'captured'
