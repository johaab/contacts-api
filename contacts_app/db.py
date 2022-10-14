import sqlite3

import click
from flask import current_app, g
# g: stores data that might be accessed by multiple functions during the request
# current_app: points to the flask application handling the request


def get_db():
    if 'db' not in g:
        # establish connection to the file pointed by DATABASE
        # (the file does not have to exist yet)
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # return rows that behave like dicts
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    """Register functions with the application instance"""
    # use close_db to clean up after returning the response
    app.teardown_appcontext(close_db)
    # add new command to be called with flask
    app.cli.add_command(init_db_command)
