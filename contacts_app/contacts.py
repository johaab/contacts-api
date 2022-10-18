from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from contacts_app.auth import login_required
from contacts_app.db import get_db

from contacts_app.forms import ContactsForm

bp = Blueprint('contacts', __name__, url_prefix='/contacts')


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    form = ContactsForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            fullname = ' '.join([str(form.firstname.data), str(form.lastname.data)])
            db = get_db()
            db.execute(
                'INSERT INTO contacts (firstname, lastname, fullname, address, email, phone, user_id)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?)',
                (form.firstname.data, form.lastname.data, fullname, form.address.data, form.email.data, form.phone.data, g.user['id'])
            )
            db.commit()
            return redirect(url_for('index'))

    return render_template('contacts/create.html', form=form)


def read(id, check_author=True):
    # input id is the contact id
    contact_info = get_db().execute(
        'SELECT c.id, username, firstname, lastname, fullname, address, email, phone, user_id'
        ' FROM contacts c'
        ' JOIN user u'
        ' ON user_id = u.id'
        ' WHERE c.id = ?',
        (id,)
    ).fetchone()

    if contact_info is None:
        abort(404, f"Contact id {id} does not exist.")

    if check_author and contact_info['user_id'] != g.user['id']:
        abort(403)

    return contact_info


@bp.route('contacts/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    form = ContactsForm()
    contact_info = read(id)

    if request.method == 'POST':
        if form.validate_on_submit():
            fullname = ' '.join([form.firstname.data, form.lastname.data])
            db = get_db()
            db.execute(
                'UPDATE contacts'
                ' SET firstname = ?, lastname = ?, fullname = ?, address = ?, email = ?, phone = ?'
                ' WHERE id = ?',
                (form.firstname.data, form.lastname.data, fullname, form.address.data, form.email.data, form.phone.data, id)
            )
            db.commit()
            return redirect(url_for('index'))

    return render_template('contacts/update.html', contact=contact_info, form=form)


@bp.route('contacts/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    read(id)
    db = get_db()
    db.execute('DELETE FROM contacts'
               ' WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('index'))
