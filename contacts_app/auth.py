import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from contacts_app.db import get_db
from contacts_app.forms import RegisterForm, LoginForm

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    form = RegisterForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            db = get_db()
            db.execute(
                "INSERT INTO user (username, password) VALUES (?, ?)",
                (form.username.data, generate_password_hash(form.password.data)),
            )  # also checks for SQL injection attack
            # format of hash string is: method$salt$hash
            db.commit()  # save changes
            return redirect(url_for("auth.login"))

    return render_template('auth/register.html', form=form)


@bp.route('/login', methods=('GET', 'POST'))
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            db = get_db()
            user = db.execute(
                'SELECT * FROM user '
                ' WHERE username = ?',
                (form.username.data,)
            ).fetchone()
            # session is a dict that stores data across requests
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

    return render_template('auth/login.html', form=form)


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

