def test_register_and_login(client):
    register_response = client.post(
        '/api/v1/auth/register',
        json={'name': 'Sara', 'phone': '+201000000001', 'password': 'secret123', 'role': 'passenger'},
    )
    assert register_response.status_code == 200
    body = register_response.json()
    assert body['user']['phone'] == '+201000000001'
    assert body['access_token']

    duplicate_response = client.post(
        '/api/v1/auth/register',
        json={'name': 'Sara', 'phone': '+201000000001', 'password': 'secret123'},
    )
    assert duplicate_response.status_code == 409

    login_response = client.post(
        '/api/v1/auth/login',
        json={'phone': '+201000000001', 'password': 'secret123'},
    )
    assert login_response.status_code == 200
    token = login_response.json()['access_token']

    wrong_password = client.post(
        '/api/v1/auth/login',
        json={'phone': '+201000000001', 'password': 'wrong-password'},
    )
    assert wrong_password.status_code == 401

    me_response = client.get('/api/v1/auth/me', headers={'Authorization': f'Bearer {token}'})
    assert me_response.status_code == 200
    assert me_response.json()['phone'] == '+201000000001'

    unauthenticated = client.get('/api/v1/auth/me')
    assert unauthenticated.status_code == 401
