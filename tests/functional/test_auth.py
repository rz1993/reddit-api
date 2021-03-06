"""Test for authentication API (i.e. registration and logging in)"""

def test_login(test_client, test_database, test_data):
    user1 = test_data['users'][0]
    user_data = {
        'username': user1.username,
        'password': 'password'
    }
    resp = test_client.post('/api/v1/auth/login', json=user_data)
    assert resp.status_code == 200
    resp = resp.get_json()
    assert 'token' in resp['data'] and resp['data']['token']


def test_login_bad_user(test_client, test_database):
    user_data = {
        'username': 'not_a_user',
        'password': 'password'
    }
    resp = test_client.post('/api/v1/auth/login', json=user_data)
    assert resp.status_code == 401


def test_register(test_client, test_database):
    new_user = {
        'username': 'new_user',
        'email': 'new_user@gmail.com',
        'password': 'password'
    }
    resp = test_client.post('/api/v1/auth/register', json=new_user)
    assert resp.status_code == 201
    payload = resp.get_json()
    assert 'token' in payload['data'] and payload['data']['token']

    login_data = {
        'username': new_user['username'],
        'password': new_user['password']
    }
    resp = test_client.post('api/v1/auth/login', json=login_data)
    assert resp.status_code == 200
