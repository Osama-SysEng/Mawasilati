from uuid import uuid4


def _register(client, role):
    phone = f'+202{uuid4().int % 10**9:09d}'
    response = client.post('/api/v1/auth/register', json={'name': role.title(), 'phone': phone, 'password': 'secret123', 'role': role})
    assert response.status_code == 200
    return response.json()


def test_admin_assigns_driver_and_blocks_unassigned_location(client):
    passenger = _register(client, 'passenger')
    driver = _register(client, 'driver')
    admin = _register(client, 'admin')
    client.headers['Authorization'] = f"Bearer {passenger['access_token']}"
    option = {'route': ['مترو'], 'price': 20}
    booked = client.post('/api/v1/trip/book', json={'option': option, 'idempotency_key': 'dispatch-book-0001'})
    assert booked.status_code == 200
    trip_id = booked.json()['trip_id']

    client.headers['Authorization'] = f"Bearer {driver['access_token']}"
    blocked = client.post('/api/v1/driver/location', json={'latitude': 30.1, 'longitude': 31.2, 'trip_id': trip_id})
    assert blocked.status_code == 403

    client.headers['Authorization'] = f"Bearer {admin['access_token']}"
    assigned = client.post(f"/api/v1/dispatch/trips/{trip_id}/assign/{driver['user']['id']}")
    assert assigned.status_code == 200
    assert assigned.json()['driver_id'] == driver['user']['id']

    client.headers['Authorization'] = f"Bearer {driver['access_token']}"
    accepted = client.post('/api/v1/driver/location', json={'latitude': 30.1, 'longitude': 31.2, 'trip_id': trip_id})
    assert accepted.status_code == 200
