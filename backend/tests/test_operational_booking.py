from uuid import uuid4


def _register(client, role='passenger'):
    phone = f'+201{uuid4().int % 10**9:09d}'
    response = client.post('/api/v1/auth/register', json={'name': 'Operational User', 'phone': phone, 'password': 'secret123', 'role': role})
    assert response.status_code == 200
    return response.json()


def test_refresh_rotation_replay_and_logout_revoke_session(client):
    tokens = _register(client)
    refreshed = client.post('/api/v1/auth/refresh', json={'refresh_token': tokens['refresh_token']})
    assert refreshed.status_code == 200
    replay = client.post('/api/v1/auth/refresh', json={'refresh_token': tokens['refresh_token']})
    assert replay.status_code == 401
    client.headers['Authorization'] = f"Bearer {refreshed.json()['access_token']}"
    assert client.get('/api/v1/auth/me').status_code == 401


def test_quote_booking_and_payment_are_idempotent(client):
    tokens = _register(client)
    client.headers['Authorization'] = f"Bearer {tokens['access_token']}"
    plan = client.post('/api/v1/trip/plan', json={'origin_lat': 30.04, 'origin_lng': 31.23, 'dest_lat': 30.12, 'dest_lng': 31.31})
    assert plan.status_code == 200
    quote = plan.json()
    booking_payload = {'option': {}, 'quote_id': quote['quote_id'], 'option_id': quote['options'][0]['id'], 'idempotency_key': 'booking-key-0001'}
    booked = client.post('/api/v1/trip/book', json=booking_payload)
    assert booked.status_code == 200
    replay = client.post('/api/v1/trip/book', json=booking_payload)
    assert replay.status_code == 200
    assert replay.json()['trip_id'] == booked.json()['trip_id']
    assert replay.json()['idempotent_replay'] is True

    wrong_amount = client.post('/api/v1/payment/initiate', json={'trip_id': booked.json()['trip_id'], 'method': 'wallet', 'amount': 1, 'idempotency_key': 'payment-key-0001'})
    assert wrong_amount.status_code == 409
    amount = booked.json()['total_price']
    payment = client.post('/api/v1/payment/initiate', json={'trip_id': booked.json()['trip_id'], 'method': 'wallet', 'amount': amount, 'idempotency_key': 'payment-key-0001'})
    assert payment.status_code == 200
    payment_replay = client.post('/api/v1/payment/initiate', json={'trip_id': booked.json()['trip_id'], 'method': 'wallet', 'amount': amount, 'idempotency_key': 'payment-key-0001'})
    assert payment_replay.status_code == 200
    assert payment_replay.json()['payment_id'] == payment.json()['payment_id']
    assert payment_replay.json()['idempotent_replay'] is True
