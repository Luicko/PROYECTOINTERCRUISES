from __future__ import print_function
import sys
import json
from threading import Thread, Lock
import time
from datetime import datetime


from flask import render_template, redirect, url_for, flash, request, g, jsonify, session
from flask.ext.login import (login_user, logout_user, current_user,
    login_required)
from sqlalchemy import exc
from werkzeug.security import generate_password_hash, \
    check_password_hash
from sqlalchemy import func
from . import app, db
from .models import *
from .forms import *
from .utils import get_redirect_target


@app.before_request
def before_request():
    g.user = current_user

def converter(date):
  if type(date) == str:
    date = datetime.strptime(date, '%d-%m-%Y').date()
    return date
  else:
    date = datetime.strftime(date, '%d-%m-%Y')
    return date


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    form = LoginForm()
    if form.validate_on_submit():
        u = User.query.filter_by(username=form.username.data).first()
        if not u:
            flash('There was an error while trying to log you in')
            return redirect(url_for('index'))
        elif check_password_hash(u.password, form.password.data):
            login_user(u)
            return redirect(url_for('main'))
    return render_template('index.html', form=form)


@app.route('/main')
def main():
    guides = Guides.query.all()
    cruises = Cruises.query.all()
    cruisecompany = CruiseCompany.query.order_by(CruiseCompany.companyname).all()
    guidecruises = GuideCruises.query.group_by(GuideCruises.date, GuideCruises.cruise_id).order_by(GuideCruises.date).all()
    return render_template('main.html', guides=guides, cruises=cruises, cruisecompany=cruisecompany, guidecruises=guidecruises)


@app.route('/assigncruise/<companyname>', methods=['GET', 'POST'])
def assigncruise(companyname): 
    cruises = Cruises.query.filter_by(cruisecompany=companyname).all()
    form = RegistCruise()
    guides = Guides.query.all()
    return render_template('assigncruise.html', form=form, cruises=cruises, cruisecompany=companyname, guides=guides)


@app.route('/finalassign', methods=['POST', 'GET'])
def finalassign():
    cruise = request.form.get('optradio', type=int)
    phones = request.form.getlist('phones[]')
    date = request.form.get('date', type=str)
    date = converter(date)
    if phones and not GuideCruises.query.filter_by(cruise_id=cruise, date=date).all():
        for phone in phones:
            entry = GuideCruises(cruise_id=cruise, date=date, phone=phone)
            db.session.add(entry)
            db.session.commit()
    else:
        flash('Something went wrong!')
    return redirect(url_for('main'))


@app.route('/assignguide', methods=['GET', 'POST'])
def assignguide():
    pho = request.form.get('phone', type=int)
    x = request.form.get('iddate', type=str)
    shi,date = x.split(",")
    shi = int(shi)
    date = converter(date)
    guidecruise = GuideCruises.query.filter_by(cruise_id=shi, date=date).first()
    guide = Guides.query.filter_by(phone=pho).first_or_404()
    newassign = guidecruise
    newassign.phone = guide.phone
    db.session.add(newassign)
    db.session.commit()
    return jsonify({"result": "OK"})


@app.route('/createguide', methods=['GET', 'POST'])
def createguide():
    form = CreateGuide()
    if form.validate_on_submit():
        language = form.language.data
        res = ""
        for x in language:
            res = res + x + "-"
        res[0:len(res)-1]
        g = Guides(guidename=form.guidename.data, phone=form.phonenumber.data,
            email=form.email.data, guidetype=form.guidetype.data, guidecontract=form.guidecontract.data, 
            dni=form.dni.data, language=res)
        try:
            db.session.add(g)
            db.session.commit()
            if form.another.data == True:
                return redirect(url_for('createguide'))
            else:
                return redirect(url_for('main'))
        except exc.SQLAlchemyError:
            flash("Something went wrong")
    return render_template('createguide.html', form=form)


@app.route('/createcuise', methods=['GET', 'POST'])
def createcruise():
    form = CreateCruise()
    cruisecompany = CruiseCompany.query.all()
    if form.validate_on_submit():
        c = Cruises(cruisename=form.cruisename.data, cruisecompany=request.form.get('optradio', type=str), shortname=form.cruiseshort.data)
        if c.cruisecompany == None:
            flash('Something went wrong!')
        try:
            db.session.add(c)
            db.session.commit()
            if form.another.data == True:
                return redirect(url_for('createcruise'))
            else:
                return redirect(url_for('main'))
        except exc.SQLAlchemyError:
            flash("Something went wrong!")
    return render_template('createcruise.html', form=form, cruisecompany=cruisecompany)


@app.route('/createcompany', methods=['GET', 'POST'])
def createcompany():
    form = CreateCompany()
    if form.validate_on_submit():
        c = CruiseCompany(companyname=form.companyname.data, shortname=form.companyshort.data)
        try:
            db.session.add(c)
            db.session.commit()
            if form.another.data == True:
                return redirect(url_for('createcompany'))
            else:
                return redirect(url_for('main'))
        except exc.SQLAlchemyError:
            flash('Something went wrong!')
    return render_template('createcompany.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('index'))


@app.route('/regist', methods=['GET', 'POST'])
def regist():
    form = RegistrationForm()
    if form.validate_on_submit():
        u = User(username=form.username.data, password=generate_password_hash(form.password.data))
        db.session.add(u)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('regist.html', form=form)


@app.route('/eliminateguide', methods=['GET', 'POST'])
def eliminateguide():
    p = request.form.get('phone', type=int)
    guide = Guides.query.filter_by(phone=p).first()
    check = GuideCruises.query.filter_by(phone=guide.phone).all()
    for obj in check:
        db.session.delete(obj)
        db.session.commit()
    db.session.delete(guide)
    db.session.commit()
    return redirect(url_for('main'))


@app.route('/eliminatecruise', methods=['GET', 'POST'])
def eliminatecruise():
    cruises = Cruises.query.all()
    form = ElimCru()
    cruise = request.form.get('id', type=int)
    if cruise:
        e = Cruises.query.filter_by(cruise_id=cruise).first()
        check = GuideCruises.query.filter_by(cruise_id=e.cruise_id).all()
        if check:
            for obj in check:
                db.session.delete(obj)
                db.session.commit()
        db.session.delete(e)
        db.session.commit()
        return redirect(url_for('main'))
    return render_template('eliminatecruise.html', form=form, cruises=cruises)


@app.route('/delcruise', methods=['GET', 'POST'])
def delcruise():
    cruise_id = request.form.get('cruise_id', type=int)
    cruise = Cruises.query.filter_by(cruise_id=cruise_id).first()
    check = GuideCruises.query.filter_by(cruise_id=cruise.cruise_id).all()
    if check:
        for obj in check:
            db.session.delete(obj)
            db.session.commit()
    db.session.delete(cruise)
    db.session.commit()
    return redirect(url_for('main'))


@app.route('/eliminatecompany', methods=['GET', 'POST'])
def eliminatecompany():
    cruisecompany = CruiseCompany.query.all()
    return render_template('eliminatecompany.html', cruisecompany=cruisecompany)


@app.route('/delcompany/<companyname>', methods=['GET', 'POST'])
def delcompany(companyname):
    company = CruiseCompany.query.filter_by(companyname=companyname).first()
    form = ElimComp()
    if form.validate_on_submit():
        if form.check.data:
            e = CruiseCompany.query.filter_by(companyname=form.companyname.data).first()
            first = Cruises.query.filter_by(cruisecompany=form.companyname.data).all()
            for obj in first:
                check = GuideCruises.query.filter_by(cruise_id=obj.cruise_id).all()
                if check:
                    for cru in check:
                        db.session.delete(cru)
                        db.session.commit()
                db.session.delete(obj)
                db.session.commit()
            db.session.delete(e)
            db.session.commit()
            return redirect(url_for('main'))
    return render_template('delcompany.html', form=form, company=company)


@app.route('/eliminateassign/<cruise_id>/<date>', methods=['GET', 'POST'])
def eliminateassign(cruise_id, date):
    date = datetime.strptime(date, '%d-%m-%Y').date()
    assign = GuideCruises.query.filter_by(cruise_id=cruise_id, date=date).all()
    cruise = Cruises.query.filter_by(cruise_id=cruise_id).first_or_404()
    form = ElimAss()
    if form.validate_on_submit():
        e = GuideCruises.query.filter_by(date=form.date.data, cruise_id=cruise.cruise_id).all()
        for obj in e:
            db.session.delete(obj)
            db.session.commit()
        return redirect(url_for('main'))
    return render_template('eliminateassign.html', form=form, assign=assign, cruise=cruise, date=date)


@app.route('/guideadmin')
def guideadmin():
    guides = Guides.query.all()
    return render_template('guideadmin.html', guides=guides)


@app.route('/guide/<phone>', methods=['GET', 'POST'])
def guide(phone):
    guidecruises = GuideCruises.query.filter_by(phone=phone).order_by(GuideCruises.date).all()
    guide = Guides.query.filter_by(phone=phone).first_or_404()
    language = guide.language.split("-")
    crui = Cruises.query.all()
    cruises = []
    for obj in guidecruises:
        for ship in crui:
            if obj.cruise_id == ship.cruise_id:
                cruises.append(ship)
    return render_template('guide.html', guide=guide, guidecruises=guidecruises, cruises=cruises, language=language)


@app.route('/deleteassign', methods=['GET', 'POST'])
def deleteassign():
    date = request.form.get('date')
    date = converter(date)
    guide = request.form.get('phone', type=int)
    e = GuideCruises.query.filter_by(date=date, phone=guide).first()
    db.session.delete(e)
    db.session.commit()
    return redirect(url_for('guide', phone=guide))
    

@app.route('/editguide', methods=['GET', 'POST'])
def editguide():
    g = request.form.get('g', type=int)
    newname = request.form.get('newname', type=str)
    newemail = request.form.get('newemail', type=str)
    newphone = request.form.get('newphone', type=int)
    newdni = request.form.get('newdni', type=str)
    guide = Guides.query.filter_by(phone=g).first()
    if newname and newname != guide.guidename:
        guide.guidename = newname
    if newemail and newemail != guide.email:
        guide.email = newemail
    if newdni and newdni != guide.dni:
        guide.dni = newdni
    if newphone and newphone != guide.phone:
        check = GuideCruises.query.all()
        for obj in check:
            if guide.phone == obj.phone:
                obj.phone = newphone
                db.session.add(obj)
                db.session.commit()
        guide.phone = newphone
    db.session.add(guide)
    db.session.commit()
    return redirect(url_for('guideadmin'))

@app.route('/addmultiple', methods=['GET', 'POST'])
def addmultiple():
    phones = request.form.getlist('phones[]')
    date = request.form.get('date', type=str)
    date = converter(date)
    cruise_id = request.form.get('cruise_id', type=int)
    if phones:
        try:
            for p in phones:
                new = GuideCruises(date=date, cruise_id=cruise_id, phone=p)
                if not GuideCruises.query.filter_by(date=date, cruise_id=cruise_id, phone=p).first():
                    db.session.add(new)
                    db.session.commit()
            return redirect(url_for('index'))
        except exc.SQLAlchemyError:
            flash("Something went wrong")


@app.route('/delmultiple', methods=['GET', 'POST'])
def delmultiple():
    phones = request.form.getlist('phones[]')
    date = request.form.get('date', type=str)
    date = converter(date)
    cruise_id = request.form.get('cruise_id', type=int)
    if phones:
        try:
            for p in phones:
                old = GuideCruises.query.filter_by(date=date, cruise_id=cruise_id, phone=p).first()
                db.session.delete(old)
                db.session.commit()
            return redirect(url_for('index'))
        except exc.SQLAlchemyError:
            flash("Something went wrong")

@app.route('/copy', methods=['GET', 'POST'])
def copy():
    old_date = request.form.get('old_date', type=str)
    cruise_id = request.form.get('cruise_id', type=int)
    old_date = converter(old_date)
    new_date = request.form.get('new_date', type=str)
    new_date = converter(new_date)
    old = GuideCruises.query.filter_by(date=old_date, cruise_id=cruise_id).all()
    if new_date:
        try:
            for item in old:
                new = GuideCruises(date=new_date, cruise_id=cruise_id, phone=item.phone)
                db.session.add(new)
                db.session.commit()
            return redirect(url_for('main'))
        except exc.SQLAlchemyError:
            flash("Something went wrong")


@app.route('/cruiseadmin/<cruise_id>/<date>', methods=['GET', 'POST'])
def cruiseadmin(cruise_id, date):
    date = datetime.strptime(date, '%d-%m-%Y').date()
    guidecruises = GuideCruises.query.filter_by(cruise_id=cruise_id, date=date).all()
    main = GuideCruises.query.filter_by(cruise_id=cruise_id, date=date).first()
    guides = Guides.query.all()
    cruise = Cruises.query.filter_by(cruise_id=cruise_id).first_or_404()
    employed = []
    form = RegistCruise()
    for phone in guidecruises:
        employed.append(phone.phone)
    date = converter(date)
    return render_template('cruiseadmin.html', form=form, guides=guides, guidecruises=guidecruises, cruise=cruise, date=date, employed=employed, main=main)
