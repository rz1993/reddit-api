"""Test for authentication API (i.e. registration and logging in)"""


def test_login(test_client, test_database):
    test_data = test_database[1]
    user1 = test_data['users'][0]
    user_data = {
        'username': user1.username,
        'password': 'password'
    }
    resp = test_client.post('/api/v1/auth/login', json=user_data)
    assert resp.status_code == 200


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
    assert payload['data']['user']['username'] == new_user['username']
    assert payload['data']['user']['email'] == new_user['email']

    login_data = {
        'username': new_user['username'],
        'password': new_user['password']
    }
    resp = test_client.post('api/v1/auth/login', json=login_data)
    assert resp.status_code == 200
