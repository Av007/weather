import os
import click
from flask import Flask
from flask_caching import Cache

from weather.cities import City, Cities


def create_app():
    """
    Boostrap file
    :return: flask application
    """
    config = {
        "DEBUG": os.getenv('debug'),
        "CACHE_TYPE": "SimpleCache",
        "CACHE_DEFAULT_TIMEOUT": os.getenv('cache_timeout') or 3600
    }

    app = Flask(__name__)

    from .routes import main_blueprint
    app.register_blueprint(main_blueprint)

    app.config.from_mapping(config)
    cache = Cache(app)
    cache.init_app(app)

    @app.cli.command('cache-init')
    def cache_init():
        cities_service = Cities(['Paris'])
        cities_service.get_cities_coord()
        click.secho('Successfully writing cache', fg='green', bold=True)

    return app
