api_key = "sk_test_dummy"
api_base = "http://localhost:12111"

import localstripe.resources

Customer = localstripe.resources.Customer
Token = localstripe.resources.Token
PaymentMethod = localstripe.resources.PaymentMethod
store = localstripe.resources.store


def test_get_payment_methods_after_creating_card(faker):
    # Create a customer manually and add to store
    customer = Customer(email=faker.email())
    store['customer:' + customer.id] = customer

    # Create a card token manually and add to store
    card_token = Token(card={
        'number': '4242424242424242',
        'exp_month': 12,
        'exp_year': 2030,
        'cvc': '123',
    })
    store['token:' + card_token.id] = card_token

    # Attach the card to the customer using the internal API method
    Customer._api_add_source(customer.id, source=card_token.id)

    # Directly list payment methods for the customer and type 'card'
    pm_list = PaymentMethod._api_list_all(
        url=None, customer=customer.id, type='card', limit=None, starting_after=None
    )._list

    assert len(pm_list) >= 1
    # Assert at least one payment method has a card
    assert any(hasattr(pm, 'card') and pm.card for pm in pm_list), 'No card found in payment methods list'

    # Check that at least one card has last4 == '4242'
    assert any(getattr(pm, 'card', {}).get('last4') == '4242' for pm in pm_list), 'No card with last4 == 4242 found in payment methods list'

    # Check that at least one card matches all details
    assert any(
        getattr(pm, 'card', {}).get('last4') == '4242' and
        getattr(pm, 'card', {}).get('exp_month') == 12 and
        getattr(pm, 'card', {}).get('exp_year') == 2030
        for pm in pm_list
    ), 'No card with expected last4, exp_month, and exp_year found in payment methods list'

    # Check that at least one card has correct brand, fingerprint, and tokenization_method
    assert any(
        getattr(pm, 'card', {}).get('brand') == 'Visa' for pm in pm_list
    ), 'No card with brand Visa found in payment methods list'

    # The test card number is always 4242424242424242, so fingerprint should match
    expected_fingerprint = localstripe.resources.fingerprint('4242424242424242')
    assert any(
        getattr(pm, 'card', {}).get('fingerprint') == expected_fingerprint for pm in pm_list
    ), f'No card with expected fingerprint {expected_fingerprint} found in payment methods list'

    # tokenization_method is None by default for these test cards
    assert any(
        'tokenization_method' in getattr(pm, 'card', {}) for pm in pm_list
    ), 'No card with tokenization_method field found in payment methods list'
