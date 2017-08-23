from . import db, app

from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(255))


class CruiseCompany(db.Model):
    __tablename__ = 'Company'
    companyname = db.Column(db.String(255), primary_key=True)
    cruises = db.relationship('Cruises', backref='company', lazy='dynamic')
    shortname = db.Column(db.String(10))


class GuideCruises(db.Model):
    __tablename__ = 'guide_cruise_table'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    phone = db.Column(db.Integer, db.ForeignKey('Guides.phone'), nullable=True)
    date = db.Column(db.Date)
    cruise_id = db.Column(db.Integer, db.ForeignKey('Cruises.cruise_id'))
    guides = db.relationship('Guides')


class Cruises(db.Model):
    __tablename__ = 'Cruises'
    cruise_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cruisename = db.Column(db.String(64), unique=True)
    cruisecompany = db.Column('CruiseCompany', db.String(255), db.ForeignKey('Company.companyname'))
    shortname = db.Column(db.String(10))
    guides = db.relationship('GuideCruises')


class Guides(db.Model):
    __tablename__ = 'Guides'
    guidename = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(255), index=True, unique=True)
    guidetype = db.Column(db.String(64), index=True)
    phone = db.Column(db.Integer, primary_key=True)
    applies = db.relationship('Cruises', secondary='guide_cruise_table',
        backref=db.backref('Cruises', lazy='dynamic'))


"""
guide_cruise_table = db.Table('GuideCruises',
    db.column('id', db.Integer, autoincrement=True),
    db.column('phone', db.Integer, db.ForeignKey('Guides.phone')),
    db.column('date', db.DateTime),
    db.column('hour', db.Time),
    db.column('cruise_id', db.Integer, db.ForeignKey('Cruises.cruise_id')))
"""