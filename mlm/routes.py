from flask import Flask, request, session, render_template, redirect, url_for, jsonify, json
import re
from werkzeug.security import generate_password_hash, check_password_hash

from mlm import app
#from ecommerce import utilities as u
from database import ecommerce_db as db
from mlm import utilities as u


@app.route('/admin')
@u.admin_required
def admin():
	return render_template('admin/admin.html', 
		title = 'Dashboard',
		member_name = 'Je Ar Becerro',
		page = 'Dashboard', dashboard = 'active', 
		is_admin_login = u.is_admin_login(), is_member_login = u.is_member_login(), is_distributor_login = u.is_distributor_login()
		)

'''
@app.route('/mlm_login_process')
def mlm_login_process():
	username = request.args.get('username', 0, type=str)
	password = request.args.get('password', 0, type=str)
	remember = request.args.get('remember', 0, type=str)

	user = db.users.find_one({ 'username': username})
	region = ''

	if user:
		address = user['address']
		if len(address) !=0:
			adrs = list(address.split("|"))
			region = adrs[4]

	if len(username) == 0:
		return jsonify(error_msg='Username is empty.')
	elif user is None:
		return jsonify(error_msg='Username not found. Please check your login details and try again.')
	elif user['mlm_id'] == '':
		return jsonify(error_msg='User is not a Farmers Club Member.')
	elif not check_password_hash(user['password'], password):
		return jsonify(error_msg="Incorrect password for '{}'! Please check your login details and try again.".format(username))
	else:
		session.permanent = False
		if remember == 'true':
			session.permanent = True


		session['username'] = username
		session['region'] = region
		session['logged_in'] = True

		u.set_users_cart_to_cache()

		return jsonify(error_msg='None')
'''