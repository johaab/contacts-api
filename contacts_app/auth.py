import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from contacts_app.db import get_db
from contacts_app.forms import AuthForm

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    form = AuthForm()
    error = None
    if request.method == 'POST':
        if form.validate_on_submit():
            db = get_db()
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (form.username.data, generate_password_hash(form.password.data)),
                )  # also checks for SQL injection attack
                # format of hash string is: method$salt$hash
                db.commit()  # save changes
            except db.IntegrityError:
                error = 'User already registered.'
            else:
                return redirect(url_for("auth.login"))

        flash(error)
    return render_template('auth/register.html', form=form)


def register_old():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )  # also checks for SQL injection attack
                # format of hash string is: method$salt$hash
                db.commit()  # save changes
            except db.IntegrityError:
                error = 'User already registered.'
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    form = AuthForm()
    error = None
    if request.method == 'POST':
        db = get_db()
        user = db.execute(
            'SELECT * FROM user '
            ' WHERE username = ?',
            (form.username.data,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], form.password.data):
            error = 'Incorrect password.'

        if error is None:
            # session is a dict that stores data across requests
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html', form=form)


def login_old():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user '
            ' WHERE username = ?',
            (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            # session is a dict that stores data across requests
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * '
            ' FROM user '
            ' WHERE id = ?',
            (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# decorator to make sure
# user is logged in
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

