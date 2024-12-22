import pytest
from flask import Flask
from flask_caching import Cache


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['CACHE_TYPE'] = 'SimpleCache'
    cache = Cache(app)
    cache.init_app(app)

    with app.app_context():
        yield app
