from flask import Flask, request,session, render_template, redirect, url_for, jsonify, json
import re
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash

from ecommerce import app
from ecommerce import utilities as u
from database import ecommerce_db as db

'''  Account Details Process '''
#Edit email or password
@app.route('/3DD0E37A2FEBF24C5481EE39D54C7E078A5AE11C578FF02202A874829E37C3E97DCFAA226F7FAE8BC2C635DAD84DF9AD1EDE294D883DAEA4EE60BFF4C012ECB6')
@u.login_required
def edit_email_password():
	email = request.args.get('email', 0, type=str)
	old_password = request.args.get('old_password', 0, type=str)
	new_password = request.args.get('new_password', 0, type=str)

	user = db.users.find_one({ 'username': session['username'] })
	#email verification SOON
	#email validation
	emailExists = db.users.find_one({ 'email': email })
		
	#password validation
	regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]') 
	if emailExists and email != user['email']:
		return jsonify(login_error_msg='Email already exist. Please try another one.')
	elif not (re.search("^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$",email)):    
		return jsonify(login_error_msg="Email is invalid. Please check your email and try again.")
	elif user['email'] != email:
		db.users.update({ 'username': session['username'] },{"$set":{"email": email }})
		return jsonify(login_success_msg='Your email has been changed successfully!')
	#old_password authentication
	elif len(old_password) != 0 and len(new_password) !=0:
		if not check_password_hash(user['password'], old_password):
			return jsonify(login_error_msg="Incorrect password for '{}'! Please try again.".format(session['username']))
		elif ( regex.search(new_password) == None or not any(x.isupper() for x in new_password) or not any(x.islower() for x in new_password) or not any(x.isdigit() for x in new_password) or len(new_password) <= 8):
			return jsonify(login_error_msg="New password is weak. Please try another one.")
		else:
			new_password =  generate_password_hash(new_password, method='sha256')
			db.users.update({ 'username': session['username'] },{"$set":{"password": new_password }})
			return jsonify(login_success_msg='Your password has been changed successfully!')
	else:
		return jsonify(nothing='')

#Add personal details
@app.route('/6C62554D7D7D642C55E28C6FCAB668A984ED784C1199E5CE12B769F298F8BEB0E9FBFEA46056A150582C5E332FA272C56EB31FBE2D8BFB263796B59EDA22B227')
@u.login_required
def add_personal_details():
	name = request.args.get('name', 0, type=str)
	number = request.args.get('number', 0, type=str)
	birthday = request.args.get('birthday', 0, type=str)
	age = None
	if len(birthday) != 0:
		bdate = list(birthday.split("-"))
		bday = int(bdate[2])
		bmonth = int(bdate[1])
		byear = int(bdate[0])
		today = date.today()
		age = today.year - byear - ((today.month, today.day) < (bmonth, bday)) 
	if len(name) == 0:
		return jsonify(personal_error_msg='Name field is empty!')
	elif name.replace(" ", "").replace(".","").isalpha() == False:
		return jsonify(personal_error_msg='Numbers and special characters are not allowed. Please fill in your proper name.')
	#number validation
	elif len(number) == 0:
		return jsonify(personal_error_msg='Mobile Number field is empty!')
	elif len(number) > 11 or len(number) < 11 or number.isnumeric() == False or number[:2] != '09':
		return jsonify(personal_error_msg='Invalid format. Please enter your valid number. Ex. 09123456789')
	#number authentication Soon
	#birthdate validation
	elif birthday == '':
		return jsonify(personal_error_msg='Please fill in your birthdate.')
	elif age is not None and age >= 100 or age <= 5:
		return jsonify(personal_error_msg='Birthdate Error: Age is Invalid')
	else:
		db.add_update_personal(session['username'], name, number, birthday)
		return jsonify(personal_success_msg = 'Successfully Save')
'''  End Account Details Process '''

''' Add Address '''
#Set province get city/municipality for selection
@app.route('/8A1E349E01BF6920F5508F2B89CB6C3E94D8C9975F12A9F9602699108AFD55111BB6372DBFD92FE6244E54B81DA23801B12C4715C713F14FBB014388E84621F1', methods=["POST"])
def province_get_city():
	provCode = request.data.decode('UTF-8')
	cities_to_json = []
	with open('./resources/static/ecommerce/js/address-dropdown/citymun.json') as x:
		cities = json.load(x)
	for city in cities:
		if city['provCode'] == provCode:
			cities_to_json.append( { 'citymunCode' : city['citymunCode'], 'citymunDesc' : city['citymunDesc'] }, )
	return jsonify(cities = cities_to_json)

#Set barangay get city/municipality for selection base from citymun Code/ID
@app.route('/E5F2C1589E6E036E7708D7D8C75BDB9F91B54E97A7C5C50AA4F0E1408A091556D34A0AEE2D3F1FF3596DDD3C2186B09F163753AC1095D8420FD4CB476569AB67', methods=["POST"])
def city_get_brgy():
	citymunCode = request.data.decode('UTF-8')
	brgy_to_json = []
	#barangays = db.barangays.find({ 'citymunCode': citymunCode },{ "_id": 0, "id": 0, "citymunCode": 0, 'citymunDesc': 0 })
	with open('./resources/static/ecommerce/js/address-dropdown/barangay.json') as x:
		barangays = json.load(x)
	for brgy in barangays:
		if brgy['citymunCode'] == citymunCode:
			brgy_to_json.append( { 'brgyCode' : brgy['brgyCode'], 'brgyDesc' : brgy['brgyDesc'] }, )
	return jsonify(brgy = brgy_to_json)

#Save address 
@app.route('/B7A95B4216A66DC660150E6D409CA5FAB7649B2183A74917777B4B75AA89C7082B25466DCB7FADDE0B657EC67AF1D131AE029E651E14012912DAEEB1053AE43C')
@u.login_required
def save_address_details():
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
	elif len(citymunCode) == 0:
		return jsonify(address_error_msg='Please select your City/Municipality')
	elif len(brgyCode) == 0:
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
		if 'region' in session:
			session.pop('region', None)
		session['region'] = regDesc
		db.add_update_address(session['username'], address)
		return jsonify(address_success_msg='Your address is successfully save!')
''' End Add Address '''