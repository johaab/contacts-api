from flask import (
    Blueprint, flash, g, redirect, render_template, session, request, url_for
)
from contacts_app.db import get_db

bp = Blueprint('index', __name__)


@bp.route('/')
def index():
    db = get_db()
    contacts = db.execute(
        'SELECT firstname, lastname, address, email, phone, u.id'
        ' FROM contacts c'
        ' JOIN user u'
        ' ON c.user_id = u.id'
    ).fetchall()

    skills = db.execute(
        'SELECT t.name, t.level, fullname, t.id'
        ' FROM (SELECT u.id, s.name, level '
        '       FROM skills s'
        '       JOIN user u'
        '       ON s.user_id = u.id ) t'
        ' JOIN contacts c'
        ' ON c.user_id = t.id'
    ).fetchall()

    contacts_columns = ['First Name', 'Last Name', 'Address', 'Email', 'Phone', 'Profile']
    skills_columns = ['Skill', 'Level', 'Name', 'Profile']
    return render_template('index/index.html',
                           contacts_columns=contacts_columns, contacts=contacts,
                           skills_columns=skills_columns, skills=skills)


@bp.route('/<int:id>/profile')
def profile(id):
    db = get_db()
    contact = db.execute(
        'SELECT c.id, username, firstname, lastname, fullname, address, email, phone'
        ' FROM contacts c'
        ' JOIN user u'
        ' ON c.user_id = u.id'
        ' WHERE c.user_id = ?',
        (id,)
    ).fetchone()

    skills = db.execute(
        'SELECT s.id, name, level'
        ' FROM skills s'
        ' JOIN user u'
        ' ON s.user_id = u.id'
        ' WHERE s.user_id = ?',
        (id,)
    ).fetchall()
    return render_template('index/profile.html',
                           profileid=id,
                           contact=contact,
                           skills=skills)


@bp.route('/surprise')
def easter_egg():
    return render_template('surprise/easter_egg.html')

