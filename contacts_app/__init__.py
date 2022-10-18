import os
from flask import Flask
from . import db, auth, contacts, skills, index


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',  # switch to random value before deployment
        DATABASE=os.path.join(app.instance_path, 'contacts_app.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello world!'

    # register database
    db.init_app(app)

    # register blueprints
    app.register_blueprint(auth.bp)
    app.register_blueprint(contacts.bp)
    app.register_blueprint(skills.bp)
    app.register_blueprint(index.bp)

    # blog is the main index
    app.add_url_rule('/', endpoint='index')

    return app
