def _register_and_token(client, phone='+201000000002'):
    response = client.post(
        '/api/v1/auth/register',
        json={'name': 'Omar', 'phone': phone, 'password': 'secret123'},
    )
    return response.json()['access_token']


def test_trip_requires_auth(client):
    response = client.post('/api/v1/trip/book', json={'option': {'price': 10, 'route': ['metro']}})
    assert response.status_code == 401


def test_trip_plan_book_and_history(client):
    token = _register_and_token(client)
    headers = {'Authorization': f'Bearer {token}'}

    plan_response = client.post(
        '/api/v1/trip/plan',
        json={'origin_label': 'المعادي', 'destination_label': 'وسط البلد', 'budget': 20},
        headers=headers,
    )
    assert plan_response.status_code == 200
    options = plan_response.json()['options']
    assert len(options) == 3

    book_response = client.post(
        '/api/v1/trip/book',
        json={'option': options[0]},
        headers=headers,
    )
    assert book_response.status_code == 200
    trip_id = book_response.json()['trip_id']

    track_response = client.get(f'/api/v1/trip/track/{trip_id}', headers=headers)
    assert track_response.status_code == 200
    assert track_response.json()['found'] is True

    unauthenticated_track = client.get(f'/api/v1/trip/track/{trip_id}')
    assert unauthenticated_track.status_code == 401

    history_response = client.get('/api/v1/trip/history', headers=headers)
    assert history_response.status_code == 200
    assert len(history_response.json()['items']) == 1
