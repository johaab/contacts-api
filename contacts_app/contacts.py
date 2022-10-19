from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from flask.json import jsonify
from werkzeug.exceptions import abort

from contacts_app.auth import login_required
from contacts_app.db import get_db

bp = Blueprint('contacts', __name__, url_prefix='/contacts')


@bp.route('', methods=('POST',))
@login_required
def create():
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    address = request.form['address']
    email = request.form['email']
    phone = request.form['phone']
    fullname = ' '.join([str(firstname), str(lastname)])
    error = []

    # TODO: more validation
    if not firstname:
        error.append('First name is required.')
    if not lastname:
        error.append('Last name is required.')
    if not address:
        error.append('Address is required.')
    if not email:
        error.append('Email address is required.')
    if not phone:
        error.append('Phone number is required.')
    elif not phone.isdecimal():
        error.append('Unexpected phone number format')

    if error:
        return jsonify(dict(zip([f'error_{i}' for i, _ in enumerate(error)], error)))
    else:
        db = get_db()
        db.execute(
            'INSERT INTO contacts (firstname, lastname, fullname, address, email, phone, user_id)'
            ' VALUES (?, ?, ?, ?, ?, ?, ?)',
            (firstname, lastname, fullname, address, email, phone, g.user['id'])
        )
        db.commit()
        message = "New contact information successfully added"
        return jsonify({'message': message}), 201


@bp.route('', methods=('GET',))
def read():
    contact_info = get_db().execute(
        'SELECT c.id, username, firstname, lastname, fullname, address, email, phone'
        ' FROM contacts c JOIN user u ON c.user_id = u.id'
    ).fetchall()
    if contact_info:
        return jsonify([dict(row) for row in contact_info]), 200
    else:
        return None, 204


@bp.route('/<int:id>', methods=('GET',))
def read_single(id):
    # input id is the contact id
    contact_info = get_db().execute(
        'SELECT c.id, username, firstname, lastname, fullname, address, email, phone'
        ' FROM contacts c JOIN user u ON c.user_id = u.id'
        ' WHERE c.id = ?',
        (id,)
    ).fetchone()
    if contact_info:
        return jsonify(dict(contact_info)), 200
    else:
        return None, 204


@bp.route('/<int:id>', methods=('PUT',))
@login_required
def update(id):
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    fullname = ' '.join([firstname, lastname])
    address = request.form['address']
    email = request.form('email')
    phone = request.form('phone')
    error = []

    if not firstname:
        error.append('First name is required.')
    if not lastname:
        error.append('Last name is required.')
    if not address:
        error.append('Address is required.')
    if not email:
        error.append('Email address is required.')
    if not phone:
        error.append('Phone number is required.')

    if error:
        return jsonify(dict(zip([f'error_{i}' for i, _ in enumerate(error)], error))), 400
    else:
        db = get_db()
        db.execute(
            'UPDATE post SET firstname = ?, lastname = ?, fullname = ?, address = ?, email = ?, phone = ?'
            ' WHERE id = ?',
            (firstname, lastname, fullname, address, email, phone, id)
        )
        db.commit()
        message = "Contact information successfully updated"
        return jsonify({'message': message}), 201


@login_required
def get_contact_info(id, check_author=True):
    # input id is the contact id
    contact_info = get_db().execute(
        'SELECT c.id, username, firstname, lastname, fullname, address, email, phone'
        ' FROM contacts c JOIN user u ON c.user_id = u.id'
        ' WHERE id = ?',
        (id,)
    ).fetchone()

    if contact_info is None:
        abort(404, f"Contact id {id} does not exist.")

    if check_author and contact_info['user_id'] != g.user['id']:
        abort(403)

    return contact_info


@bp.route('/<int:id>', methods=('DELETE',))
@login_required
def delete(id):
    get_contact_info(id)
    db = get_db()
    db.execute('DELETE FROM contacts WHERE id = ?', (id,))
    db.commit()
    message = "Contact information successfully deleted"
    return jsonify({'message': message}), 200

