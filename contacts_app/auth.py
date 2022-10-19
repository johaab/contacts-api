import functools
import datetime

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from flask.json import jsonify

from werkzeug.security import check_password_hash, generate_password_hash
from contacts_app.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('POST',))
def register():
    username = request.form['username']
    password = request.form['password']
    db = get_db()
    error = []

    if not username:
        error.append('Username is required.')
    elif not password:
        error.append('Password is required.')

    if not error:
        try:
            db.execute(
                "INSERT INTO user (username, password) VALUES (?, ?)",
                (username, generate_password_hash(password)),
            )  # also checks for SQL injection attack
            # format of hash string is: method$salt$hash
            db.commit()  # save changes
        except db.IntegrityError:
            error.append(f"User {username} is already registered.")
        else:
            return "Successfully registered"

    return jsonify(dict(zip([f'error_{i}' for i, _ in enumerate(error)], error))), 400


@bp.route('/login', methods=('POST',))
def login():
    username = request.form['username']
    password = request.form['password']
    db = get_db()
    error = []
    user = db.execute(
        'SELECT * FROM user WHERE username = ?', (username,)
    ).fetchone()

    if user is None:
        error.append('Incorrect username.')
    elif not check_password_hash(user['password'], password):
        error.append('Incorrect password.')

    if not error:
        # session is a dict that stores data across requests
        session.clear()
        session['user_id'] = user['id']
        message = "Successfully logged in"
        return jsonify({'message': message, 'username': username, 'user_id': session['user_id']}), 200

    return jsonify(dict(zip([f'error_{i}' for i, _ in enumerate(error)], error))), 400


@bp.route('/whoisloggedin', methods=('GET',))
def read():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

    if g.user is not None:
        return jsonify({'username': g.user['username'], 'user_id': user_id})
    else:
        return jsonify({'message': 'Nobody'})


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    message = "Successfully logged out"
    return jsonify({'message': message}), 200


# decorator to make sure
# user is logged in
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            message = "Please log in"
            return jsonify({'message': message}), 401

        return view(**kwargs)

    return wrapped_view

