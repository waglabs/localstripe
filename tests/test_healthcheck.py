import requests
import stripe


def test_healthcheck_endpoint_returns_200(faker):
    response = requests.get('{}/healthcheck'.format(stripe.api_base))
    assert response.status_code == 200
    assert response.text == 'api.stripe.com at your service! What can I do for you today? (Up)'
