from flask_wtf import Form
from wtforms import *

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
    dni = StringField('DNI')
    guidetype = RadioField('Type', choices=[('se', 'Self-Employed'),('dcl', 'Declared')])
    guidecontract = RadioField('Contract', choices=[('of', 'Official'),('nof', 'Non-Official')])
    language = SelectMultipleField(u'Language', choices=[('esp', 'Spanish'), ('ger', 'German'), ('eng', 'English'),
        ('ita', 'Italian'), ('ext', 'Other')])
    spanish = BooleanField('ESP')
    german = BooleanField('GER')
    english = BooleanField('ENG')
    italian = BooleanField('ITA')
    other = BooleanField('EXT')
    another = BooleanField('Another', default=False)
    submit = SubmitField('Create')


class CreateCompany(Form):
    companyname = StringField('Company Name', validators=[validators.DataRequired()])
    companyshort = StringField('Short Name')
    another = BooleanField('Another', default=False)
    submit = SubmitField('Create')

class RegistCruise(Form):
    companyname = StringField('Company', validators=[validators.DataRequired])
    date = DateField('Date', format='%d/%M/%Y', validators=[validators.DataRequired])

class mainform(Form):
    hidde = HiddenField('hidde', validators=[validators.DataRequired])
    date = DateField('Date', format='%d/%M/%Y', validators=[validators.DataRequired])

class ElimCru(Form):
    hidden = HiddenField('hidden', validators=[validators.DataRequired])
    cruisename = StringField('Cruise Name', validators=[validators.DataRequired])
    check = BooleanField('Sure', default=False)
    submit = SubmitField('X')

class ElimComp(Form):
    companyname = StringField('Company Name', validators=[validators.DataRequired])
    check = BooleanField('Sure', default=False)
    submit = SubmitField('X')