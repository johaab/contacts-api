from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from flask.json import jsonify
from werkzeug.exceptions import abort

from contacts_app.auth import login_required
from contacts_app.db import get_db

bp = Blueprint('skills', __name__, url_prefix='/skills')


@bp.route('/<int:id>', methods=('POST',))
@login_required
def create(id):
    name = request.form['name']
    level = request.form['level']
    error = []

    skill_levels = ['Beginner', 'Intermediate', 'Advanced', 'Expert']
    if not name:
        error.append('Skill name is required.')
    if not level:
        error.append('Skill level is required.')
    elif level.capitalize() not in skill_levels:
        error.append("Expected skill levels are: " + ', '.join(skill_levels))
    name = name.capitalize()
    level = level.capitalize()

    if error:
        return jsonify(dict(zip([f'error_{i}' for i, _ in enumerate(error)], error)))
    else:
        db = get_db()
        db.execute(
            'INSERT INTO skills (name, level, id)'
            ' VALUES (?, ?, ?)',
            (name, level, id)
        )
        db.commit()
        message = "New skill created successfully"
        return jsonify({'message': message}), 200


@bp.route('', methods=('GET',))
def read():
    """Get the whole skills db"""
    skill_info = get_db().execute(
        'SELECT s.id, name, level, user_id'
        ' FROM skills s JOIN user u ON s.user_id = u.id'
    ).fetchall()

    if skill_info:
        return jsonify([dict(row) for row in skill_info]), 200
    else:
        return None, 204


@bp.route('/<int:user_id>', methods=('GET',))
def read_single(user_id):
    """Get all the skills of a single user"""
    skill_info = get_db().execute(
        'SELECT s.id, name, level, user_id'
        ' FROM skills s JOIN user u ON s.user_id = u.id'
        ' WHERE user_id = ?',
        (user_id,)
    ).fetchall()

    if skill_info:
        return jsonify([dict(row) for row in skill_info]), 200
    else:
        return None, 204


@login_required
def get_skill_info(id, check_author=True):
    # input id is the skill id
    skill_info = get_db().execute(
        'SELECT s.id, name, level, user_id'
        ' FROM skills s JOIN user u ON s.user_id = u.id'
        ' WHERE s.id = ?',
        (id,)
    ).fetchone()

    if skill_info is None:
        abort(404, f"Skill id {id} does not exist.")

    if check_author and skill_info['user_id'] != g.user['id']:
        abort(403)

    return skill_info


@bp.route('/<int:id>', methods=('PUT',))
@login_required
def update(id):
    skill_info = get_skill_info(id)

    level = request.form['level']
    error = []

    skill_levels = ['Beginner', 'Intermediate', 'Advanced', 'Expert']
    if not level:
        error.append('Skill level is required.')
    elif level.capitalize() not in skill_levels:
        error.append("Expected skill levels are: " + ', '.join(skill_levels))
    level = level.capitalize()

    if error:
        return jsonify(dict(zip([f'error_{i}' for i, _ in enumerate(error)], error)))
    else:
        db = get_db()
        db.execute(
            'UPDATE skills SET level = ?, user_id = ?'
            ' WHERE id = ?',
            (level, g.user['id'], id)
        )
        db.commit()
        message = "Skill successfully updated"
        return jsonify({'message': message})


@bp.route('/<int:user_id>/<int:skill_id>', methods=('DELETE',))
@login_required
def delete(user_id, skill_id):
    """Deletes a single skill of a single user"""
    read(skill_id)
    db = get_db()
    db.execute('DELETE FROM skills '
               ' WHERE user_id = ? '
               ' AND id = ?',
               (user_id, skill_id))
    db.commit()
    message = "Skill successfully deleted"
    return jsonify({'message': message})

