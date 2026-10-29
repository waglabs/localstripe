import os

import requests
import stripe


def call(method, path, version=None, **data):
    headers = {'Stripe-Version': version} if version is not None else {}
    base = os.environ.get('STRIPE_BASE_URL') or 'http://localhost:8420'
    params = data if method == 'GET' else None
    body = data if method != 'GET' else None
    return requests.request(method, base + path, params=params, data=body,
                            headers=headers, auth=(stripe.api_key, ''))


def create_customer_with_card(version=None):
    customer = call('POST', '/v1/customers', version).json()
    call('POST', '/v1/customers/%s/sources' % customer['id'], version,
         source='tok_visa')
    return customer['id']


def create_manual_payment_intent(customer, version):
    return call('POST', '/v1/payment_intents', version, amount=5000,
                currency='usd', customer=customer, capture_method='manual',
                confirm='true', off_session='true').json()


def test_a_request_without_a_version_gets_2018_11_08():
    customer = create_customer_with_card()
    payment_intent = call('POST', '/v1/payment_intents', amount=1000,
                          currency='usd', customer=customer).json()

    assert payment_intent['capture_method'] == 'automatic'
    assert 'charges' in payment_intent
    assert 'sources' in call('GET', '/v1/customers/' + customer).json()


def test_customer_balance_is_renamed_on_2019_10_17():
    customer = create_customer_with_card()

    before = call('GET', '/v1/customers/' + customer, '2019-10-08').json()
    after = call('GET', '/v1/customers/' + customer, '2019-10-17').json()

    assert 'account_balance' in before and 'balance' not in before
    assert 'balance' in after and 'account_balance' not in after


def test_customer_lists_need_expand_from_2020_08_27():
    customer = create_customer_with_card()

    before = call('GET', '/v1/customers/' + customer, '2020-03-02').json()
    after = call('GET', '/v1/customers/' + customer, '2020-08-27').json()
    expanded = call('GET', '/v1/customers/' + customer, '2020-08-27',
                    **{'expand[]': ['sources']}).json()

    for key in ('sources', 'subscriptions', 'tax_ids'):
        assert key in before
        assert key not in after
    assert expanded['sources']['data'][0]['id'].startswith('card_')
    assert 'subscriptions' not in expanded


def test_latest_charge_is_an_id_on_every_version():
    customer = create_customer_with_card()

    for version in ('2018-11-08', '2026-09-30.endive'):
        payment_intent = create_manual_payment_intent(customer, version)
        expanded = call('GET', '/v1/payment_intents/' + payment_intent['id'],
                        version, **{'expand[]': ['latest_charge']}).json()

        assert payment_intent['latest_charge'].startswith('ch_')
        assert expanded['latest_charge']['id'] == \
            payment_intent['latest_charge']


def test_payment_intent_charges_are_removed_on_2022_11_15():
    customer = create_customer_with_card()
    payment_intent = create_manual_payment_intent(customer, '2022-08-01')
    path = '/v1/payment_intents/' + payment_intent['id']

    before = call('GET', path, '2022-08-01').json()
    after = call('GET', path, '2022-11-15').json()

    assert before['charges']['data'][0]['id'] == before['latest_charge']
    assert 'charges' not in after


def test_charge_refunds_need_expand_from_2022_11_15():
    customer = create_customer_with_card()
    payment_intent = create_manual_payment_intent(customer, '2022-08-01')
    path = '/v1/charges/' + payment_intent['latest_charge']

    before = call('GET', path, '2022-08-01').json()
    after = call('GET', path, '2022-11-15').json()
    expanded = call('GET', path, '2022-11-15',
                    **{'expand[]': ['refunds']}).json()
    nested = call('GET', '/v1/payment_intents/' + payment_intent['id'],
                  '2022-11-15',
                  **{'expand[]': ['latest_charge.refunds']}).json()

    assert before['refunds']['object'] == 'list'
    assert 'refunds' not in after
    assert expanded['refunds']['object'] == 'list'
    assert nested['latest_charge']['refunds']['object'] == 'list'


def test_capture_method_defaults_to_automatic_async_from_2024_04_10():
    customer = create_customer_with_card()

    before = call('POST', '/v1/payment_intents', '2023-10-16', amount=1000,
                  currency='usd', customer=customer).json()
    after = call('POST', '/v1/payment_intents', '2024-04-10', amount=1000,
                 currency='usd', customer=customer).json()

    assert before['capture_method'] == 'automatic'
    assert after['capture_method'] == 'automatic_async'


def partially_capture(version):
    customer = create_customer_with_card(version)
    payment_intent = create_manual_payment_intent(customer, version)
    call('POST', '/v1/payment_intents/%s/capture' % payment_intent['id'],
         version, amount_to_capture=3000)
    return call('GET', '/v1/charges/' + payment_intent['latest_charge'],
                version, **{'expand[]': ['refunds']}).json()


def test_partial_capture_refunds_the_rest_before_2025_03_31():
    charge = partially_capture('2025-02-24.acacia')

    assert charge['amount_captured'] == 3000
    assert charge['amount_refunded'] == 2000
    assert [r['amount'] for r in charge['refunds']['data']] == [2000]


def test_partial_capture_creates_no_refund_from_2025_03_31():
    charge = partially_capture('2025-03-31.basil')

    assert charge['amount_captured'] == 3000
    assert charge['amount_refunded'] == 0
    assert charge['refunds']['data'] == []
    assert charge['refunded'] is False


def test_refunding_a_basil_partial_capture_marks_the_charge_refunded():
    charge = partially_capture('2025-03-31.basil')

    call('POST', '/v1/refunds', '2025-03-31.basil', charge=charge['id'],
         amount=3000)
    refunded = call('GET', '/v1/charges/' + charge['id'],
                    '2025-03-31.basil').json()

    assert refunded['amount_refunded'] == 3000
    assert refunded['refunded'] is True


def test_payment_method_types_is_rejected_from_2026_09_30():
    customer = create_customer_with_card()
    types = {'payment_method_types[]': ['card']}

    accepted = call('POST', '/v1/setup_intents', '2026-08-26.dahlia',
                    customer=customer, **types)
    rejected = [
        call('POST', '/v1/payment_intents', '2026-09-30.endive', amount=1000,
             currency='usd', customer=customer, **types),
        call('POST', '/v1/setup_intents', '2026-09-30.endive',
             customer=customer, **types),
        call('POST', '/v1/setup_intents/' + accepted.json()['id'],
             '2026-09-30.endive', **types),
    ]

    assert accepted.status_code == 200
    for response in rejected:
        assert response.status_code == 400
        assert response.json()['error']['code'] == \
            'payment_method_types_no_longer_supported'


def test_a_setup_intent_still_returns_payment_method_types_on_2026_09_30():
    customer = create_customer_with_card()

    setup_intent = call('POST', '/v1/setup_intents', '2026-09-30.endive',
                        customer=customer).json()

    assert setup_intent['payment_method_types'] == ['card']


def test_an_event_carries_the_version_of_the_request_that_caused_it():
    customer = call('POST', '/v1/customers', '2024-06-20').json()

    events = call('GET', '/v1/events', type='customer.created', limit=100,
                  **{'created[gte]': customer['created']}).json()['data']
    event = [e for e in events if e['data']['object']['id'] == customer['id']]

    assert event[0]['api_version'] == '2024-06-20'
    assert 'balance' in event[0]['data']['object']
