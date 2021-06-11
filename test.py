import os
import tempfile

import pytest
from flask import current_app, g, session

from app import app
from app.db import get_db


@pytest.fixture
def client():
    with app.app_context():
        db_fd, current_app.config['DATABASE'] = tempfile.mkstemp()
        current_app.config['TESTING'] = True

        with current_app.test_client() as client:
            with app.app_context():
                get_db()
            yield client

        os.close(db_fd)
        os.unlink(current_app.config['DATABASE'])


def test_redirection(client):
    rv = client.get('/index')
    assert rv.status_code == 302


def login(client):
    user = client.post('/login', data=dict(
        username='admin',
        password='admin'
    ), follow_redirects=True)
    return user


def test_login(client):
    rv = login(client)
    assert rv.status_code == 200


def test_logout(client):
    rv = client.get('/logout')
    assert rv.status_code == 302


def test_add_position():
    with app.app_context():
        with current_app.test_client() as client:
            user = login(client)
            headers = user.headers
            rv = client.post('/position/add', data=dict(
                position_name='pos_test1234',
                description='pos_test'
            ), headers=headers)
            assert rv.status_code == 200
