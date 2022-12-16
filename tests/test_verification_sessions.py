import stripe

def test_create_verification_session(faker):
    session = stripe.identity.VerificationSession.create(type='document')
    assert session.status == 'requires_input'
    assert session.type == 'document'
    assert session.url == 'https://fake/' + session.id
    session = stripe.identity.VerificationSession.retrieve(session.id)
    assert session.status == 'requires_input'
    assert session.type == 'document'
    assert session.url == 'https://fake/' + session.id


def test_cancel_verification_session(faker):
    session: stripe.identity.VerificationSession = stripe.identity.VerificationSession.create(type='document')
    assert session.status == 'requires_input'
    assert session.type == 'document'
    assert session.url == 'https://fake/' + session.id
    session = session.cancel()
    assert session.status == 'canceled'
    assert session.type == 'document'
    assert session.url == 'https://fake/' + session.id