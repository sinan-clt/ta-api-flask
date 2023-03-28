import json, pytest
from app import app, db, TA



@pytest.fixture(scope='module')
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        db.drop_all()


def test_login_success(client):

    response = client.post('/login', json={'username': 'admin', 'password': 'password'})
    assert response.status_code == 200
    assert 'access_token' in json.loads(response.data)


def test_login_failure(client):

    response = client.post('/login', json={'username': 'admin', 'password': 'wrongpassword'})
    assert response.status_code == 401
    assert 'Invalid credentials' in json.loads(response.data)['message']


def test_add_ta(client):

    new_ta = {'native_english_speaker': True,
              'course_instructor': 'Dr. Smith',
              'course': 'CS101',
              'semester': True,
              'class_size': 30,
              'performance_score': 90}
    response = client.post('/ta', json=new_ta)
    assert response.status_code == 201
    assert 'New TA added successfully' in json.loads(response.data)['message']
    assert TA.query.filter_by(course='CS101').first() is not None


def test_add_duplicate_ta(client):

    new_ta = {'id': 1,
              'native_english_speaker': True,
              'course_instructor': 'Dr. Smith',
              'course': 'CS101',
              'semester': True,
              'class_size': 30,
              'performance_score': 90}
    response = client.post('/ta', json=new_ta)
    assert response.status_code == 201
    assert 'New TA added successfully' in json.loads(response.data)['message']
    response = client.post('/ta', json=new_ta)
    assert response.status_code == 400
    assert 'Error: Duplicate ID' in json.loads(response.data)['message']


def test_get_all_ta(client):

    response = client.get('/ta')
    assert response.status_code == 200
    assert len(json.loads(response.data)) == TA.query.count()


def test_get_ta_by_id(client):

    new_ta = {'native_english_speaker': True,
              'course_instructor': 'Dr. Smith',
              'course': 'CS101',
              'semester': True,
              'class_size': 30,
              'performance_score': 90}
    response = client.post('/ta', json=new_ta)
    assert response.status_code == 201
    assert 'New TA added successfully' in json.loads(response.data)['message']
    ta_id = json.loads(response.data).get('id')
    response = client.get(f'/ta/{ta_id}')
    assert response.status_code == 200
    assert json.loads(response.data).get('course') == 'CS101'


