from flask import (
    Blueprint, flash, g, redirect, render_template, session, request, url_for
)
from contacts_app.db import get_db

bp = Blueprint('index', __name__)


@bp.route('/')
def index():
    db = get_db()
    user_id = session.get('user_id')
    contact = db.execute(
        'SELECT c.id, username, firstname, lastname, fullname, address, email, phone'
        ' FROM contacts c JOIN user u ON c.user_id = u.id'
        ' WHERE c.user_id = ?',
        (user_id,)
    ).fetchone()

    skills = db.execute(
        'SELECT s.id, name, level'
        ' FROM skills s JOIN user u ON s.user_id = u.id'
        ' WHERE s.user_id = ?',
        (user_id,)
    ).fetchall()
    return render_template('index/index.html', contact=contact, skills=skills)


@bp.route('/surprise')
def easter_egg():
    return render_template('surprise/easter_egg.html')

