def _register(client, phone, role='passenger'):
    response = client.post(
        '/api/v1/auth/register',
        json={'name': 'Test', 'phone': phone, 'password': 'secret123', 'role': role},
    )
    return response.json()['access_token']


def test_only_drivers_can_report_location(client):
    passenger_token = _register(client, '+201111111111', role='passenger')
    response = client.post(
        '/api/v1/driver/location',
        json={'latitude': 30.0, 'longitude': 31.0},
        headers={'Authorization': f'Bearer {passenger_token}'},
    )
    assert response.status_code == 403

    driver_token = _register(client, '+201111111112', role='driver')
    response = client.post(
        '/api/v1/driver/location',
        json={'latitude': 30.0, 'longitude': 31.0},
        headers={'Authorization': f'Bearer {driver_token}'},
    )
    assert response.status_code == 200
    assert response.json()['driver_id']


def test_payment_confirm_requires_ownership(client):
    owner_token = _register(client, '+201111111113')
    other_token = _register(client, '+201111111114')
    owner_headers = {'Authorization': f'Bearer {owner_token}'}
    other_headers = {'Authorization': f'Bearer {other_token}'}

    book_response = client.post(
        '/api/v1/trip/book',
        json={'option': {'price': 10, 'route': ['metro']}},
        headers=owner_headers,
    )
    trip_id = book_response.json()['trip_id']

    initiate_response = client.post(
        '/api/v1/payment/initiate',
        json={'trip_id': trip_id, 'method': 'wallet', 'amount': 10},
        headers=owner_headers,
    )
    payment_id = initiate_response.json()['payment_id']

    other_confirm = client.post(
        '/api/v1/payment/confirm',
        json={'payment_id': payment_id},
        headers=other_headers,
    )
    assert other_confirm.json()['status'] == 'not_found'

    owner_confirm = client.post(
        '/api/v1/payment/confirm',
        json={'payment_id': payment_id},
        headers=owner_headers,
    )
    assert owner_confirm.json()['status'] == 'confirmed'
