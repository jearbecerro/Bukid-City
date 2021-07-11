from flask import Flask, request, session, render_template, redirect, url_for, jsonify, json
import re, os, secrets, pathlib
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from PIL import Image
from datetime import date, datetime

from bson.objectid import ObjectId
from database import mlm_db as db
from database import ecommerce_db as d
from mlm import app
from mlm import utilities as u

from pprint import pprint

#Admin Login Template
@app.route('/admin/login')
def admin_login():
	#db.mlm_users.update({ 'designation': 'Distributor' },{"$set": {'dist_id': '5f547277914d1e34e81498bb'} })
	if u.is_admin_login() == True:
		return redirect(url_for('admin'))
	else:
		return render_template('admin/login.html', whos_loging_in = 'Admin')
#Distributor Login Template
@app.route('/distributor/login')
def distributor_login():
	if u.is_distributor_login() == True:
		return redirect('/distributor/profile')
	else:
		return render_template('admin/login.html', whos_loging_in = 'Distributor')
#Member Login Template
@app.route('/member/login')
def member_login():
	if u.is_member_login() == True:
		return redirect(url_for('profile'))
	else:
		return render_template('admin/login.html', whos_loging_in = 'Member')

#Logout Process
@app.route('/mlm_logout')
def mlm_logout():
	session.pop('order_id_single_view',None)
	session.pop('member_login', None)
	session.pop('distributor_login', None)
	session.pop('admin_login', None)
	session.pop('product_id', None)
	session.pop('dist_id', None)
	return redirect(url_for('member_login'))

#Login Process
@app.route('/admin_login_process')
def admin_login_process():
	username = request.args.get('username', 0, type=str)
	password = request.args.get('password', 0, type=str)
	remember = request.args.get('remember', 0, type=str)
	who = request.args.get('who', 0, type=str)
	session.pop('member_login', None)
	session.pop('distributor_login', None)
	session.pop('admin_login', None)
	x = login_process(username, password, remember, who)
	if x[0] == 'modified':
		return jsonify(value_modified = 'True')
	if x[1] == 0:
		session.permanent = False
		if remember == 'true':
			session.permanent = True

		session['user'] = [x[3],x[4]]
		session['admin_login'] = True
		return jsonify(login = 'Success', user = who)
	else:
		return jsonify(errors = x[2])

@app.route('/dist_login_process')
def dist_login_process():
	username = request.args.get('username', 0, type=str)
	password = request.args.get('password', 0, type=str)
	remember = request.args.get('remember', 0, type=str)
	who = request.args.get('who', 0, type=str)
	session.pop('member_login', None)
	session.pop('distributor_login', None)
	session.pop('admin_login', None)
	session.pop('user', None)
	session.pop('dist_id', None)
	x = login_process(username, password, remember, who)
	if x[0] == 'modified':
		return jsonify(value_modified = 'True')
	if x[1] == 0:
		session.permanent = False
		if remember == 'true':
			session.permanent = True

		session['user'] = [x[3],x[4]]
		session['distributor_login'] = True
		session['dist_id'] = x[5]
		print(x[5])
		return jsonify(login = 'Success', user = who)
	else:
		return jsonify(errors = x[2])

@app.route('/member_login_process')
def member_login_process():
	username = request.args.get('username', 0, type=str)
	password = request.args.get('password', 0, type=str)
	remember = request.args.get('remember', 0, type=str)
	who = request.args.get('who', 0, type=str)
	session.pop('member_login', None)
	session.pop('distributor_login', None)
	session.pop('admin_login', None)
	session.pop('user', None)
	x = login_process(username, password, remember, who)
	if x[0] == 'modified':
		return jsonify(value_modified = 'True')
	if x[1] == 0:
		session.permanent = False
		if remember == 'true':
			session.permanent = True

		session['user'] = [x[3],x[4]]
		session['member_login'] = True
		return jsonify(login = 'Success', user = who)
	else:
		return jsonify(errors = x[2])

def login_process(username, password, remember, who):
	errors = []
	if who == 'Admin' or who == 'Member' or 'Distributor':
		user_exists = db.mlm_users.find_one({ 'username': username, 'designation': who })
		db_password = ''
		name = ''
		_id = ''
		distributor_id = ''
		if len(username) == 0:
			errors.append('<br>&nbspPlease enter your username')
		if len(password) == 0:
			errors.append('<br>&nbspPlease enter your password')

		if user_exists is None and len(username) != 0:
			errors.append('<br>&nbspUsername "{}" not found as {}'.format(username, who))
		if user_exists:
			db_password = user_exists['password']
			name = user_exists['name']
			_id = user_exists['_id']
			distributor_id = user_exists['dist_id']

		if not check_password_hash(db_password, password) and user_exists and len(username) !=0:
			errors.append('<br>&nbspIncorrect password for username "{}"'.format(username))
	
		return ['',len(errors), errors,str(_id),name,distributor_id]
	else:
		return ['modified']