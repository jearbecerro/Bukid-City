from flask import Flask, request, session, render_template, redirect, url_for, jsonify
import re
from werkzeug.security import generate_password_hash, check_password_hash

from ecommerce import app
from ecommerce import utilities as u
from database import ecommerce_db as db

#Display Login & Register
@app.route('/login', methods=["GET"])
def login():
	account = u.login_classifier()
	if account:
		return redirect(url_for('my_account'))
	else:
		return render_template('ecommerce/login.html',title = 'Login Page', account = account, cart_count = u.cart()[0]), 200

@app.route('/register', methods=['GET','POST'])
def register():
	u.set_current_path(['register','/myaccount'])
	account = u.login_classifier()
	if account is not None:
		return redirect(url_for('my_account'))
	else:
		return render_template('ecommerce/register.html',
			title = 'Registration Page',
			account = u.login_classifier(), 
			cart_count = u.cart()[0]
			),200

#Process Login, Register & Logout 
@app.route('/logout')
@u.login_required
def logout():
	session['logged_in'] = False
	session.pop('username', None)
	session.pop('region', None)
	if u.get_current_path()[0] == 'pick_up_center':
		return redirect(url_for('pick_up_center', pick_up_center = session['pick_up_center']))
	return redirect(url_for(u.get_current_path()[0]))
	
@app.route('/6F1F2C56F0BE8D7B11E0A55B5852720F9CCA100A381FDE3CEDA6D790FF91FAC297C4E77433A578836B5D5B7D141B0F7F3CA52B5F93126C34C6C15CC058B9B87B')
def login_process():
	username = request.args.get('username', 0, type=str)
	password = request.args.get('password', 0, type=str)
	remember = request.args.get('remember', 0, type=str)

	user = db.users.find_one({ 'username': username })
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
	elif not check_password_hash(user['password'], password):
		return jsonify(error_msg="Incorrect password for '{}'! Please check your login details and try again.".format(username))
	else:
		session.permanent = False
		if remember == 'true':
			session.permanent = True

		if 'region' in session:
			session.pop('region', None)

		session['username'] = username
		session['region'] = region
		session['logged_in'] = True

		u.set_users_cart_to_cache()

		return jsonify(error_msg='None', path = u.get_current_path()[1])

@app.route('/DD2107DB783DCF998A03B9D59FA7B352326B6543BDBBEADC04449FBEB744C10B72F13048EB8086F58C0364AA07003924BC5D7C43F3B02A915F6E336CEE8C539B')
def register_process():
	username = request.args.get('username', 0, type=str)
	password = request.args.get('password', 0, type=str)
	email = request.args.get('email', 0, type=str)
	
	userExists = db.users.find_one({ 'username': username })
	emailExists = db.users.find_one({ 'email': email })

	regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]') 

	if len(username) < 4 or len(username) >= 30:
		return jsonify(reg_error_msg="Username must be between 4 up to 30 characters long.")
	elif not (re.search("^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$",email)):    
		return jsonify(reg_error_msg="Email is invalid. Please check your email and try again.")
	elif ( regex.search(password) == None or not any(x.isupper() for x in password) or not any(x.islower() for x in password) or not any(x.isdigit() for x in password) or len(password) <= 8):
		return jsonify(reg_error_msg="Password is weak.")
	elif userExists: 
		return jsonify(reg_error_msg="Username already taken. Please try another one.")
	elif emailExists:
		return jsonify(reg_error_msg="Email already exist. Please try again")
	#email verification
	else:
		db.add_user(username, generate_password_hash(password, method='sha256'), email)
		session['username'] = username
		session['logged_in'] = True
		return jsonify(reg_success="success")
