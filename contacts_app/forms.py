from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, TelField, RadioField, validators
from wtforms.validators import DataRequired, InputRequired, ValidationError, StopValidation
from werkzeug.security import check_password_hash
import phonenumbers
from contacts_app.db import get_db

########################################################################################################################
# Below are Custom Validators
########################################################################################################################


class CheckUsername(object):
    def __init__(self, message=None):
        if not message:
            message = 'Invalid username.'
        self.message = message

    @staticmethod
    def get_user_from_db(username):
        db = get_db()
        row = db.execute(
            "SELECT username"
            " FROM user"
            " WHERE username = ?",
            (username,)
        ).fetchone()
        try:
            return row['username']
        except TypeError:
            # means that the username
            # does not exist in the db yet
            return None


class AvailableUsername(CheckUsername):
    def __init__(self, message=None):
        if not message:
            message = 'Username not available.'
        super().__init__(message=message)

    def __call__(self, form, field):
        if self.get_user_from_db(username=field.data):
            raise ValidationError(self.message)


class ExistingUsername(CheckUsername):
    def __init__(self, message=None):
        if not message:
            message = 'Username does not exist.'
        super().__init__(message=message)

    def __call__(self, form, field):
        if not self.get_user_from_db(username=field.data):
            raise ValidationError(self.message)


class CheckPassword(object):
    def __init__(self, message=None):
        if not message:
            message = 'Incorrect password.'
        self.message = message

    def __call__(self, form, field):
        correct_pw = self.get_pw_from_db(username=form.username.data)
        if correct_pw:
            # only check the password
            # if there exists one for
            # the given username
            if not check_password_hash(correct_pw, field.data):
                raise ValidationError(self.message)

    @staticmethod
    def get_pw_from_db(username):
        db = get_db()
        row = db.execute(
            "SELECT password"
            " FROM user"
            " WHERE username = ?",
            (username,)
        ).fetchone()
        try:
            return row['password']
        except TypeError:
            return None


class CheckPhone(object):
    def __init__(self, message=None):
        if not message:
            message = 'Incorrect phone number.'
        self.message = message

    def __call__(self, form, field):
        try:
            number = phonenumbers.parse(field.data, "CH")
        except phonenumbers.phonenumberutil.NumberParseException:
            raise ValidationError(self.message)
        finally:
            if (not phonenumbers.is_valid_number(number)) \
                    or (not phonenumbers.is_possible_number(number)):
                raise ValidationError(self.message)
            else:
                field.data = phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)


########################################################################################################################
# Below are FlaskForm subclasses
########################################################################################################################


class ContactsForm(FlaskForm):
    firstname = StringField('Firstname', validators=[InputRequired()])
    lastname = StringField('Lastname', validators=[InputRequired()])
    address = StringField('Address', validators=[InputRequired()])
    email = StringField('Email address', validators=[validators.Email(),
                                                     validators.Length(min=6, max=120),
                                                     InputRequired()])
    phone = TelField('Phone number', validators=[InputRequired(),
                                                 CheckPhone()])


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), AvailableUsername()])
    password = StringField('Password', validators=[InputRequired(),
                                                   validators.EqualTo('confirm_pw', message='Passwords must match'),
                                                   validators.Length(min=8)])
    confirm_pw = StringField('Repeat password', validators=[InputRequired()])


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), ExistingUsername()])
    password = StringField('Password', validators=[InputRequired(), CheckPassword()])


class SkillsForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    level = RadioField('Level', validators=[InputRequired()],
                       choices=['Beginner', 'Intermediate', 'Advanced', 'Expert', 'God'])
