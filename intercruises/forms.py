from flask_wtf import Form
from wtforms import StringField, PasswordField, RadioField, validators, IntegerField, BooleanField, DateField, HiddenField, SubmitField

class LoginForm(Form):
    username = StringField('Username', validators=[validators.DataRequired()])
    password = PasswordField('Password')
    submit = SubmitField('Connect')


class RegistrationForm(Form):
    username = StringField('Username')
    password = PasswordField('Password')
    submit = SubmitField('Sign Up')


class CreateCruise(Form):
    cruisename = StringField('Cruise Name', validators=[validators.DataRequired()])
    cruiseshort = StringField('Short Name')
    another = BooleanField('Another', default=False)
    submit = SubmitField('Create')


class CreateGuide(Form):
    guidename = StringField('Name', validators=[validators.DataRequired()])
    phonenumber = IntegerField('Phone', validators=[validators.DataRequired()])
    email = StringField('Email')
    guidetype = RadioField('Type', choices=[('se', 'Self-Employed'),('dcl', 'Declared')])
    another = BooleanField('Another', default=False)
    submit = SubmitField('Create')


class CreateCompany(Form):
    companyname = StringField('Company Name', validators=[validators.DataRequired()])
    companyshort = StringField('Short Name')
    another = BooleanField('Another', default=False)
    submit = SubmitField('Create')

class RegistCruise(Form):
    companyname = StringField('Company', validators=[validators.DataRequired])
    date = DateField('Date', format='%Y-%M-%d', validators=[validators.DataRequired])

class mainform(Form):
    hidde = HiddenField('hidde', validators=[validators.DataRequired])
    date = DateField('Date', format='%Y-%m-%d', validators=[validators.DataRequired])