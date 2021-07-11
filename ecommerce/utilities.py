from functools import wraps
from flask import session, redirect

from database import ecommerce_db as db

def login_required(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			if session['logged_in'] == True:
				return f(*args, **kwargs)
			return redirect('/login')
		else:
			return redirect('/login')
	return wrap

def login_classifier():
	if 'username' in session:
		return session['username']
	else:
		return None

def cart():#count of cart and total of cart
	if login_classifier():
		if 'cart_items' in session:
			cart_count = 0
			cart_total = 0
			for x in session['cart_items']:
				if login_classifier() == x['username']:
					cart_count += 1 
					cart_total += int(x['total_price'])
			return [cart_count, cart_total]
		return [0, 0]
	else:
		return [0, 0]

def cart_classifier():#get user's cart
	current_cart = []
	if login_classifier():
		if 'cart_items' in session:
			for items in session['cart_items']:
				if login_classifier() == items['username']:
					current_cart.append({ 'distributor_id':items['distributor_id'],'username': login_classifier(), 'product_id': items['product_id'], 'product_name' : items['product_name'], 'price': items['price'], 'total_price': items['total_price'], 'qty': items['qty'], 'img': items['img'] },)
			return current_cart
		return None
	return None

#if user login/logout it will redirect to the current brower/url
def set_current_path(path):
	if 'current_path' in session:
		session['current_path'] = path
		session.modified = True
	else:
		session['current_path'] = path

def get_current_path():
	if 'current_path' in session:
		return session['current_path']
	else:
		return 'index'

#set the region selection in the places/shop page
def set_get_region():
	region = ''
	if 'region' in session:
		region = session['region']
	r1=''
	r2=''
	r3=''
	r4=''
	r5=''
	r6=''
	r7=''
	r8=''
	r9=''
	r10=''
	r11=''
	r12=''
	r13=''
	r14=''
	r15=''
	r16=''
	if region == 'REGION I (ILOCOS REGION)':
		r1 = 'active'
	if region == 'REGION II (CAGAYAN VALLEY)':
		r2 = 'active'
	if region == 'REGION III (CENTRAL LUZON)':
		r3 = 'active'
	if region == 'REGION IV-A (CALABARZON)':
		r4a = 'active'
	if region == 'REGION IV-B (MIMAROPA)':
		r4b = 'active'
	if region == 'REGION V (BICOL REGION)':
		r5 = 'active'	
	if region == 'REGION VI (WESTERN VISAYAS)':
		r6 = 'active'	
	if region == 'REGION VII (CENTRAL VISAYAS)':
		r7 = 'active'	
	if region == 'REGION VIII (EASTERN VISAYAS)':
		r8 = 'active'
	if region == 'REGION IX (ZAMBOANGA PENINSULA)':
		r9 = 'active'
	if region == 'REGION X (NORTHERN MINDANAO)':
		r10 = 'active'
	if region == 'REGION XI (DAVAO REGION)':
		r11 = 'active'
	if region == 'REGION XII (SOCCSKSARGEN)':
		r12 = 'active'
	if region == 'NATIONAL CAPITAL REGION (NCR)':
		r13 = 'active'
	if region == 'CORDILLERA ADMINISTRATIVE REGION (CAR)':
		r14 = 'active'
	if region == 'BANGSAMORO AUTONOMOUS REGION IN MUSLIM MINDANAO (BARMM)':
		r15 = 'active'
	if region == 'REGION XIII (Caraga)' :
		r16 = 'active'
	return [r1,r2,r3,r4,r5,r6,r7,r8,r9,r10,r11,r12,r13,r14,r15,r16]

def get_user_address(user_info):
	if user_info:
		address = user_info['address']
		if len(address) > 0:
			adrs = list(address.split("|"))
			return adrs
		else:
			return ['','','','','']

def set_users_cart_to_cache():
	users_cart = db.cart.find({ 'username': login_classifier() })
	users_cart_list = []
	if users_cart:
		for items in users_cart:
			users_cart_list.append({ 'username': login_classifier(), 'product_id': items['product_id'], 'product_name': items['product_name'] , 'price': items['price'] , 'qty': items['qty'], 'total_price' : items['total_price'], 'img': items['img'], 'distributor_id': items['distributor_id']})
			if 'cart_items' in session:
				session.pop('cart_items', None)
				session['cart_items'] = users_cart_list
			else:
				session['cart_items'] = users_cart_list
				
