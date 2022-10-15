from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from contacts_app.auth import login_required
from contacts_app.db import get_db

bp = Blueprint('contacts', __name__, url_prefix='/contacts')


@bp.route('/create', methods='POST')
@login_required
def create():
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    address = request.form['address']
    email = request.form['email']
    phone = request.form['phone']
    fullname = ' '.join([str(firstname), str(lastname)])
    error = None

    if not firstname:
        error = 'First name is required.'
    if not lastname:
        error = 'Last name is required.'
    if not address:
        error = 'Address is required.'
    if not email:
        error = 'Email address is required.'
    if not phone:
        error = 'Phone number is required.'
    elif not phone.isdecimal():
        error = 'Unexpected phone number format'

    if error is not None:
        flash(error)
    else:
        db = get_db()
        db.execute(
            'INSERT INTO contacts (firstname, lastname, fullname, address, email, phone, user_id)'
            ' VALUES (?, ?, ?, ?, ?, ?, ?)',
            (firstname, lastname, fullname, address, email, phone, g.user['id'])
        )
        db.commit()
        return redirect(url_for('index'))


@bp.route('/read', methods='GET')
@login_required
def read(id, check_author=True):
    # input id is the contact id
    contact_info = get_db().execute(
        'SELECT c.id, username, firstname, lastname, fullname, address, email, phone,'
        ' FROM contacts c JOIN user u ON c.user_id = u.id'
        ' WHERE c.id = ?',
        (id,)
    ).fetchone()

    if contact_info is None:
        abort(404, f"Contact id {id} does not exist.")

    if check_author and contact_info['user_id'] != g.user['id']:
        abort(403)

    return contact_info


@bp.route('contacts/<int:id>/update', methods='POST')
@login_required
def update(id):
    contact_info = read(id)

        firstname = request.form['firstname']
        lastname = request.form['lastname']
        fullname = ' '.join([firstname, lastname])
        address = request.form['address']
        email = request.form('email')
        phone = request.form('phone')
        error = None

        if not firstname:
            error = 'First name is required.'
        if not lastname:
            error = 'Last name is required.'
        if not address:
            error = 'Address is required.'
        if not email:
            error = 'Email address is required.'
        if not phone:
            error = 'Phone number is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET firstname = ?, lastname = ?, fullname = ?, address = ?, email = ?, phone = ?, user_id = ?'
                ' WHERE id = ?',
                (firstname, lastname, fullname, address, email, phone, g.user['id'], id)
            )
            db.commit()
            return redirect(url_for('index'))

    return render_template('contacts/update.html', post=contact_info)


@bp.route('contacts/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    read(id)
    db = get_db()
    db.execute('DELETE FROM contacts WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('index'))

