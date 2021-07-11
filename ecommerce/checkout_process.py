from flask import Flask, request,session, render_template, redirect, url_for, jsonify, json
import re
from datetime import date, datetime
from werkzeug.security import generate_password_hash, check_password_hash

from ecommerce import app
from ecommerce import utilities as u
from database import ecommerce_db as db

@app.route('/place_order')
@u.login_required
def place_order():
	username = u.login_classifier()
	order_note = request.args.get('order_note', 0, type=str)
	check_user = db.users.find_one({ 'username': username })
	distributor_id = ''
	if check_user:
		if len(check_user['name']) == 0:
			return jsonify (place_order_error_msg = 'Please fill in your Personal Profile.')
		elif len(check_user['phone']) == 0:
			return jsonify (place_order_error_msg = 'Please fill in your Personal Profile.')
		elif len(check_user['address']) == 0:
			return jsonify (place_order_error_msg = 'Please fill in your Delivery Address.')
		else: 
			order_items = []
			for items in session['cart_items']:
				if username == items['username']:
					order_items.append({'product_id': items['product_id'], 'product_name' : items['product_name'], 'price': int(items['price']), 'total_price': int(items['total_price']), 'qty': int(items['qty']), 'img': items['img'], 'distributor_id': items['distributor_id'] },)
					distributor_id = items['distributor_id']
			user = db.users.find_one({ 'username': username })
			a = list(user['address'].split("|"))
			address = "{}, {}, {}, {}".format(a[0],a[1],a[2],a[3])
			order = {
				'username': username,
				'mlm_id': user['mlm_id'],
				'buyer': user['name'],
				'delivery_address': address,
				'contact_number': user['phone'],
				'date': datetime.now().strftime('%B %d, %Y @ %I:%M:%S %p'),
				'status':'Processing',
				'product_ordered':order_items,
				'order_note': order_note,
				'total': int(u.cart()[1]),
				'distributor_id': distributor_id
			}

			o = db.orders.insert_one(order)
			x = db.cart.delete_many({ 'username': username })
			#delete all cart items with session.pop
			session.pop('cart_items', None)
			#delete certain users cart items with updating username into '' but others data still remains which cause cache lagging
			'''for items in session['cart_items']:
				if u.login_classifier() == items['username']:
					items['username'] = ''
					session.modified = True
			'''
			if 'order_id' in session:
				session['order_id'] = str(o.inserted_id)
				session.modified = True
			else:
				session['order_id'] =  str(o.inserted_id)

			return jsonify (place_order_error_msg = '')
	else:
		return jsonify (username = 'modified')

@app.route('/save_personal_profile')
@u.login_required
def save_personal_profile():
	name = request.args.get('name', 0, type=str)
	number = request.args.get('number', 0, type=str)
	email = request.args.get('email', 0, type=str)
	username = request.args.get('username', 0, type=str)

	check_user = db.users.find_one({ 'username': username })
	if check_user:
		if len(name) == 0:
			return jsonify (profile_error_msg = 'Please fill in your full name.')
		elif name.replace(" ", "").replace(".","").isalpha() == False:
			return jsonify(profile_error_msg = 'Numbers and special characters are not allowed. Please fill in your proper name.')
		elif len(number) > 11 or len(number) < 11 or number.isnumeric() == False or number[:2] != '09':
			return jsonify(profile_error_msg='Invalid format. Please enter your valid number. Ex. 09123456789')
		elif len(number) == 0:
			return jsonify (profile_error_msg = 'Please fill in your mobile number.')
		else: 
			db.users.update({ 'username': username },{"$set":{"name": name,"phone": number }})
			return jsonify (profile_success_msg ='Successfully Save', name = name, number = number, email = email)
	else:
		return jsonify (username = 'modified')

@app.route('/save_address')
@u.login_required
def save_address():
	street = request.args.get('street', 0, type=str)
	provCode = request.args.get('province', 0, type=str)
	citymunCode = request.args.get('citymun', 0, type=str)
	brgyCode = request.args.get('barangay', 0, type=str)
	with open('./resources/static/ecommerce/js/address-dropdown/regions.json') as r:
		regions = json.load(r)
	with open('./resources/static/ecommerce/js/address-dropdown/provinces.json') as p:
		provinces = json.load(p)
	with open('./resources/static/ecommerce/js/address-dropdown/citymun.json') as c:
		citymun = json.load(c)
	with open('./resources/static/ecommerce/js/address-dropdown/barangay.json') as b:
		barangays = json.load(b)
	if len(street) == 0:
		return jsonify(address_error_msg='Please fill in your specific address.')
	elif provCode == 'Choose Province':
		return jsonify(address_error_msg='Please select your City/Municipality')
	elif citymunCode == 'Choose City/Municipality':
		return jsonify(address_error_msg='Please select your City/Municipality')
	elif brgyCode == 'Choose Barangay':
		return jsonify(address_error_msg='Please select your Barangay')
	else:
		for province in provinces:
			if province['provCode'] == provCode:
				regCode = province["regCode"]
				provDesc = province['provDesc']
		for region in regions:
			if region['regCode'] == regCode:
				regDesc = region['regDesc']
		for city in citymun:
			if city['citymunCode'] == citymunCode:
				citymunDesc = city['citymunDesc']
		for brgy in barangays:
			if brgy['brgyCode'] == brgyCode:
				brgyDesc = brgy['brgyDesc']
		address = "{}|{}|{}|{}|{}".format(street,brgyDesc,citymunDesc,provDesc,regDesc)
		adrs = "{}, {}, {}, {}".format(street,brgyDesc,citymunDesc,provDesc)
		print(adrs)
		if 'region' in session:
			session.pop('region', None)
		session['region'] = regDesc
		db.add_update_address(session['username'], address)
		return jsonify(address_success_msg='Your address is successfully save!', address = adrs.upper())
