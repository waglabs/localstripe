import requests
import stripe
stripe.api_key = 'sk_test_12345'
import pprint


def test_get_payment_methods_returns_collection(faker):
    # Ensure at least one payment method exists for a customer
    customer = stripe.Customer.create(email=faker.email())
    card_token = 'tok_visa'
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

    # Call the endpoint directly
    headers = {"Authorization": f"Bearer {stripe.api_key}"}
    response = requests.get(
        f'{stripe.api_base}/v1/payment_methods',
        params={'customer': customer.id, 'type': 'card'},
        headers=headers
    )

    data = response.json()
    assert response.status_code == 200
    assert isinstance(data, dict)
    assert 'data' in data
    assert isinstance(data['data'], list)
    assert len(data['data']) >= 1
    # Assert at least one payment method has a card
    assert any('card' in pm and pm['card'] for pm in data['data']), 'No card found in payment methods data'

    # Check that card info is present
    found = any(pm['id'] == payment_method.id and pm['card'] for pm in data['data'])
    assert found, 'Created payment method not found in response'

    # Check that at least one card has last4 == '4242'
    assert any(pm.get('card', {}).get('last4') == '4242' for pm in data['data']), 'No card with last4 == 4242 found in payment methods data'

    # Check that at least one card matches all details
    assert any(
        pm.get('card', {}).get('last4') == '4242' and
        pm.get('card', {}).get('exp_month') == 12 and
        pm.get('card', {}).get('exp_year') == 2030
        for pm in data['data']
    ), 'No card with expected last4, exp_month, and exp_year found in payment methods data'
