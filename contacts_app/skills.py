from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from contacts_app.auth import login_required
from contacts_app.db import get_db

bp = Blueprint('skills', __name__, url_prefix='/skills')


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        name = request.form['name']
        level = request.form['level']
        error = None

        skill_levels = ['Beginner', 'Intermediate', 'Advanced', 'Expert']
        if not name:
            error = 'Skill name is required.'
        if not level:
            error = 'Skill level is required.'
        elif level.capitalize() not in skill_levels:
            error = "Expected skill levels are: " + ', '.join(skill_levels)
        name = name.capitalize()
        level = level.capitalize()

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO skills (name, level, user_id)'
                ' VALUES (?, ?, ?)',
                (name, level, g.user['id'])
            )
            db.commit()
            return redirect(url_for('index'))

    return render_template('skills/create.html')


def read(id, check_author=True):
    # input id is the skill id
    skill_info = get_db().execute(
        'SELECT id, name, level, user_id'
        ' FROM skills'
        ' WHERE id = ?',
        (id,)
    ).fetchone()

    if skill_info is None:
        abort(404, f"Skill id {id} does not exist.")

    if check_author and skill_info['user_id'] != g.user['id']:
        abort(403)

    return skill_info


def read_all(id, check_author=True):
    # input id is the user id
    skills_info = get_db().execute(
        'SELECT id, name, level'
        ' FROM skills'
        ' WHERE user_id = ?',
        (id,)
    ).fetchall()

    if check_author and skills_info['user_id'] != g.user['id']:
        abort(403)

    if skills_info is None:
        abort(404, f"No registered skills for {g.user['username']}")

    return skills_info


@bp.route('skills/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    skill_info = read(id)

    if request.method == 'POST':
        level = request.form['level']
        error = None

        skill_levels = ['Beginner', 'Intermediate', 'Advanced', 'Expert']
        if not level:
            error = 'Skill level is required.'
        elif level.capitalize() not in skill_levels:
            error = "Expected skill levels are: " + ', '.join(skill_levels)
        level = level.capitalize()

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE skills SET level = ?'
                ' WHERE id = ?',
                (level, id)
            )
            db.commit()
            return redirect(url_for('index'))

    return render_template('skills/update.html', skill=skill_info)


@bp.route('skills/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    read(id)
    db = get_db()
    db.execute('DELETE FROM skills WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('index'))

