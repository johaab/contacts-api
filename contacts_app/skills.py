from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from contacts_app.auth import login_required
from contacts_app.db import get_db
from contacts_app.forms import SkillsForm

bp = Blueprint('skills', __name__, url_prefix='/skills')


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    form = SkillsForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            db = get_db()
            db.execute(
                'INSERT INTO skills (name, level, user_id)'
                ' VALUES (?, ?, ?)',
                (form.name.data.capitalize(), form.level.data, g.user['id'])
            )
            db.commit()
            return redirect(url_for('index'))

    return render_template('skills/create.html', form=form)


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


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    skill_info = read(id)
    form = SkillsForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            db = get_db()
            db.execute(
                'UPDATE skills SET level = ?'
                ' WHERE id = ?',
                (form.level.data.capitalize(), id)
            )
            db.commit()
            return redirect(url_for('index.profile', id=g.user['id']))

    return render_template('skills/update.html', skill=skill_info, form=form)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    read(id)
    db = get_db()
    db.execute('DELETE FROM skills'
               ' WHERE id = ?',
               (id,))
    db.commit()
    return redirect(url_for('index'))

