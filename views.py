from __future__ import print_function
import sys
import json
from threading import Thread, Lock
import time
from datetime import datetime


from flask import render_template, redirect, url_for, flash, request, g, jsonify, session
from flask.ext.login import (login_user, logout_user, current_user,
    login_required)
from werkzeug.security import generate_password_hash, \
    check_password_hash
from sqlalchemy import func
from . import app, db
from .models import *
from .forms import LoginForm, CreateGuide, CreateCruise, RegistrationForm, CreateCompany, RegistCruise, mainform
from .utils import get_redirect_target


@app.before_request
def before_request():
    g.user = current_user


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
    cruisecompany = CruiseCompany.query.all()
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
    date = datetime.strptime(date, '%Y-%M-%d').date()
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
    date = datetime.strptime(date, '%Y-%M-%d').date()
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
        g = Guides(guidename=form.guidename.data, phone=form.phonenumber.data,
            email=form.email.data, guidetype=form.guidetype.data)
        try:
            db.session.add(g)
            db.session.commit()
            if form.another.data == True:
                return redirect(url_for('createguide'))
            else:
                return redirect(url_for('main'))
        except:
            flash("Something went wrong")
    return render_template('createguide.html', form=form)


@app.route('/createcuise', methods=['GET', 'POST'])
def createcruise():
    form = CreateCruise()
    cruisecompany = CruiseCompany.query.all()
    if form.validate_on_submit():
        c = Cruises(cruisename=form.cruisename.data, cruisecompany=request.form.get('optradio', type=str), shortname=form.cruiseshort.data)
        try:
            db.session.add(c)
            db.session.commit()
            if form.another.data == True:
                return redirect(url_for('createcruise'))
            else:
                return redirect(url_for('main'))
        except:
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
        except:
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
    guides = Guides.query.all()
    form = ElimGuide()
    if form.validate_on_submit():
        e = Guides.query.filter_by(phone=form.phone.data).first()
        check = GuideCruises.query.all()
        for obj in check:
            if e.phone == obj.phone:
                db.session.delete(obj)
                db.session.commit()
        db.session.delete(e)
        db.session.commit()
        return redirect(url_for('main'))
    return render_template('eliminateguide.html', form=form, guides=guides)


@app.route('/eliminatecruise', methods=['GET', 'POST'])
def eliminatecruise():
    cruises = Cruises.query.all()
    form = ElimCru()
    if form.validate_on_submit():
        e = Cruises.query.filter_by(cruise_id=form.cruise_id.data).first()
        db.session.delete(e)
        db.session.commit()
        return redirect(url_for('main'))
    return render_template('eliminatecruise.html', form=form, cruises=cruises)


@app.route('/eliminatecompany', methods=['GET', 'POST'])
def eliminatecompany():
    cruisecompany = CruiseCompany.query.all()
    form = ElimComp()
    if form.validate_on_submit():
        e = CruiseCompany.query.filter_by(companyname=form.companyname.data).first()
        db.session.delete(e)
        db.session.commit()
        return redirect(url_for('main'))
    return render_template('eliminatecompany.html', form=form, cruisecompany=cruisecompany)


@app.route('/eliminateassign', methods=['GET', 'POST'])
def eliminateassign():
    assign = GuideCruises.query.all()
    form = ElimAss()
    date = datetime.strptime(form.date.data, '%Y-%M-%d').date()
    if form.validate_on_submit():
        e = GuideCruises.query.filter_by(date=date, cruise_id=form.cruise_id.data).all()
        db.session.delete(e)
        db.session.commit()
        return redirect(url_for('main'))
    return render_template('eliminateassign.html', form=form, assign=assign)


@app.route('/guideadmin')
def guideadmin():
    guides = Guides.query.all()
    return render_template('guideadmin.html', guides=guides)


@app.route('/guide/<phone>', methods=['GET', 'POST'])
def guide(phone):
    guidecruises = GuideCruises.query.filter_by(phone=phone).order_by(GuideCruises.date).all()
    guide = Guides.query.filter_by(phone=phone).first_or_404()
    crui = Cruises.query.all()
    cruises = []
    for obj in guidecruises:
        for ship in crui:
            if obj.cruise_id == ship.cruise_id:
                cruises.append(ship)
    return render_template('guide.html', guide=guide, guidecruises=guidecruises, cruises=cruises)


@app.route('/deleteassign', methods=['GET', 'POST'])
def deleteassign():
    date = request.form.get('date')
    date = datetime.strptime(date, '%Y-%M-%d').date()
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
    guide = Guides.query.filter_by(phone=g).first()
    if newname and newname != guide.guidename:
        guide.guidename = newname
    if newemail and newemail != guide.email:
        guide.email = newemail
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
    return redirect(url_for('guide', phone=newphone))

@app.route('/addmultiple', methods=['GET', 'POST'])
def addmultiple():
    phones = request.form.getlist('phones[]')
    date = request.form.get('date', type=str)
    date = datetime.strptime(date, '%Y-%M-%d').date()
    cruise_id = request.form.get('cruise_id', type=int)
    if phones:
        try:
            for p in phones:
                new = GuideCruises(date=date, cruise_id=cruise_id, phone=p)
                db.session.add(new)
                db.session.commit()
            return redirect(url_for('index'))
        except:
            flash("Something went wrong")


@app.route('/delmultiple', methods=['GET', 'POST'])
def delmultiple():
    phones = request.form.getlist('phones[]')
    date = request.form.get('date', type=str)
    date = datetime.strptime(date, '%Y-%M-%d').date()
    cruise_id = request.form.get('cruise_id', type=int)
    if phones:
        try:
            for p in phones:
                old = GuideCruises.query.filter_by(date=date, cruise_id=cruise_id, phone=p).first()
                db.session.delete(old)
                db.session.commit()
            return redirect(url_for('index'))
        except:
            flash("Something went wrong")

@app.route('/copy', methods=['GET', 'POST'])
def copy():
    old_date = request.form.get('old_date', type=str)
    cruise_id = request.form.get('cruise_id', type=int)
    old_date = datetime.strptime(old_date, '%Y-%M-%d').date()
    new_date = request.form.get('new_date', type=str)
    new_date = datetime.strptime(new_date, '%Y-%M-%d').date()
    old = GuideCruises.query.filter_by(date=old_date, cruise_id=cruise_id).all()
    if new_date:
        try:
            for item in old:
                new = GuideCruises(date=new_date, cruise_id=cruise_id, phone=item.phone)
                db.session.add(new)
                db.session.commit()
            return redirect(url_for('main'))
        except:
            flash("Something went wrong")


@app.route('/cruiseadmin/<cruise_id>/<date>', methods=['GET', 'POST'])
def cruiseadmin(cruise_id, date):
    guidecruises = GuideCruises.query.filter_by(cruise_id=cruise_id, date=date).all()
    main = GuideCruises.query.filter_by(cruise_id=cruise_id, date=date).first()
    guides = Guides.query.all()
    cruise = Cruises.query.filter_by(cruise_id=cruise_id).first_or_404()
    employed = []
    form = RegistCruise()
    for phone in guidecruises:
        employed.append(phone.phone)
    return render_template('cruiseadmin.html', form=form, guides=guides, guidecruises=guidecruises, cruise=cruise, date=date, employed=employed, main=main)