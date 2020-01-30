"""Tests for Subreddit API"""

FAKE_SUB = {
    'name': 'test_sub3',
    'description': 'A subreddit for testing.'
}

def get_access_token(client, user):
    resp = client.post('/api/v1/auth/login', json={
        'username': user.username,
        'password': 'password'
    })
    if resp.status_code != 200:
        raise ValueError('Could not authenticate')

    payload = resp.get_json()
    if 'data' not in payload or 'token' not in payload['data']:
        raise ValueError('Could not authenticate')

    return payload['data']['token']


def test_create_subreddit(test_client, test_database, test_data):
    #test_data = test_database[1]
    user1 = test_data['users'][0]

    access_token = get_access_token(test_client, user1)

    sub_data = FAKE_SUB

    resp = test_client.post(
        '/api/v1/subreddits',
        json=sub_data,
        headers={'Authorization': f'Bearer {access_token}'}
    )
    assert resp.status_code == 201
    payload = resp.get_json()
    assert payload['data']['subreddit']['name'] == sub_data['name']
    assert payload['data']['subreddit']['description'] == sub_data['description']
    assert payload['data']['subreddit']['subscriber_count'] == 1


def test_create_subreddit_no_auth(test_client, test_database):
    sub_data = FAKE_SUB

    resp = test_client.post(
        '/api/v1/subreddits',
        json=sub_data
    )
    assert resp.status_code == 401
