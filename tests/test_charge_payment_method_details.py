import stripe

from . import create_customer


def test_charge_carries_payment_method_details_for_a_card(faker):
    customer = create_customer(faker.email(), 'tok_visa')
    payment_intent = stripe.PaymentIntent.create(
        amount=2750,
        currency="usd",
        customer=customer.id,
        capture_method="automatic",
        off_session=True,
        confirm=True,
    )

    charge = stripe.PaymentIntent.retrieve(payment_intent.id)['charges']['data'][0]
    details = charge['payment_method_details']

    assert details['type'] == 'card'
    assert details['card']['brand'] == 'visa'
    assert details['card']['last4'] == '4242'
    # Stripe reports the brand lowercase here, where the legacy Card spells it 'Visa'.
    assert stripe.Customer.retrieve(customer.id)['default_source'].startswith('card_')


def test_charge_payment_method_details_match_the_payment_method(faker):
    customer = create_customer(faker.email())
    payment_method = stripe.PaymentMethod.create(
        type='card',
        card={
            'number': '4242424242424242',
            'exp_month': 12,
            'exp_year': 2030,
            'cvc': '123',
        },
    )
    stripe.PaymentMethod.attach(payment_method.id, customer=customer.id)

    payment_intent = stripe.PaymentIntent.create(
        amount=1500,
        currency="usd",
        customer=customer.id,
        payment_method=payment_method.id,
        capture_method="automatic",
        off_session=True,
        confirm=True,
    )

    charge = stripe.PaymentIntent.retrieve(payment_intent.id)['charges']['data'][0]

    assert charge['payment_method'] == payment_method.id
    assert charge['payment_method_details']['card'].to_dict() == \
        payment_method['card'].to_dict()
