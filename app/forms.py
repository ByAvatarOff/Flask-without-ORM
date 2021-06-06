from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField, BooleanField, IntegerField, SelectField
from wtforms.validators import DataRequired, EqualTo, ValidationError

import app.db as new_db

from app import routes


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember_me')
    submit = SubmitField('Sign in')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        if new_db.get_db().execute(
                'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            raise ValidationError('Please use a different username')


class AddDepartmentForm(FlaskForm):
    department_name = StringField('Department name', validators=[DataRequired()])
    parent_id = IntegerField('Parent')
    submit = SubmitField('Add department')


class AddPositionForm(FlaskForm):
    position_name = StringField('Position name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    submit = SubmitField('Add position')


class AddEmployeeForm(FlaskForm):
    """
    Class
    """
    pos_choices = new_db.list_position()
    dep_choices = new_db.list_department()

    fio = StringField('FIO', validators=[DataRequired()])
    position_id = SelectField('Position name', choices=pos_choices)
    department_id = SelectField('Department name', choices=dep_choices)
    submit = SubmitField('Add employee')

    # def validate_fio(self, fio: str):
    #     if new_db.get_db().execute(
    #             'SELECT fio FROM employee WHERE fio = ?', (str(fio), )
    #     ).fetchone() is not None:
    #         raise ValidationError('Enter a different fio')


class UpdateEmployeeForm(FlaskForm):
    dep_choices = new_db.list_department()
    pos_choices = new_db.list_position()

    position_id = SelectField('Position name', choices=pos_choices)
    department_id = SelectField('Department name', choices=dep_choices)
    submit = SubmitField('Update employee')
