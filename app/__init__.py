from flask import Flask
from app.routes import main_blueprint


def create_app():
    """
    Boostrap file
    :return: flask application
    """
    app = Flask(__name__)

    app.register_blueprint(main_blueprint)
    app.add_url_rule('/', endpoint='index')

    return app
