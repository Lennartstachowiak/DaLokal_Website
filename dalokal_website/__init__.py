from flask import Flask


def create_app():
    app = Flask(__name__)
    app.secret_key = "hello"

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .app import app as app_blueprint
    app.register_blueprint(app_blueprint)

    return app

""" Command line to run local
export FLASK_APP=dalokal_website
export FLASK_DEBUG=1
flask run"""