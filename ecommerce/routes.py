from flask import Flask, request,session, render_template, redirect, url_for, jsonify, json
from bson.objectid import ObjectId

from ecommerce import app
from ecommerce import utilities as u
from database import ecommerce_db as db

#Landing Page
@app.route('/', methods=['GET','POST'])
def index():
	u.set_current_path(['index','/'])
	return render_template('ecommerce/index.html',title = 'Home Page', account = u.login_classifier(),
	cart_count = u.cart()[0], cart = u.cart_classifier(), subtotal = u.cart()[1]), 200

from pprint import pprint

@app.route('/search-product', methods=['POST'])
def search_product():
	try:
		x = request.form.get('search_product')
		p = db.products.find({ 'name': {'$regex': str(x)} })
		y = []
		for i in p:
			d = db.distributors.find_one({ '_id': ObjectId(str(i['distributor_id'])) })
			dist = "{}, {}".format(d['branch_name'], d['city'])
			y.append({ 'dist': dist, 'distributor_id': i['distributor_id'], 'update_date': i['update_date'],'total_sales': i['total_sales'],'total_orders': i['total_orders'],'undiscounted_price': i['undiscounted_price'],'stock': i['stock'],'status': i['status'],'sku': i['sku'],'long_desc': i['long_desc'],'image2': i['image2'],'image1': i['image1'],'name': i['name'], 'price': i['price'], '_id': str(i['_id']) })
		
		return jsonify( products = y)
	except Exception as e:
		return redirect(url_for(u.get_current_path()[0]))
	
@app.route('/about')
def about():
	return render_template('ecommerce/about.html',title = 'About', account = u.login_classifier(), 
	cart_count = u.cart()[0], cart = u.cart_classifier(), subtotal = u.cart()[1]), 200

@app.route('/faq')
def faq():
	return render_template('ecommerce/faq.html',title = "FAQ's", 
	cart_count = u.cart()[0], cart = u.cart_classifier(), subtotal = u.cart()[1]), 200

#Cart Page
@app.route('/mycart', methods=["GET"])
@u.login_required
def my_cart():
	u.set_current_path(['index','/mycart'])
	cart_per_dist = []
	if 'cart_items' in session:
		for items in session['cart_items']:
			if login_classifier() == items['username']:
				d = db.distributors.find_one({ '_id': ObjectId(str(items['distributor_id'])) })
				dist = "{}, {}".format(d['branch_name'],d['city'])
				cart_per_dist.append({ 'distributor_id':items['distributor_id'],'username': login_classifier(), 'product_id': items['product_id'], 'product_name' : items['product_name'], 'price': items['price'], 'total_price': items['total_price'], 'qty': items['qty'], 'img': items['img'] },)
	
	return render_template('ecommerce/cart.html', title = 'My Cart', username = "{}'s".format(session['username']), 
	cart = u.cart_classifier(), subtotal = u.cart()[1]
	),200
	
#import add to cart process and remove from cart process
from ecommerce import cart_process

#Check Out Page
@app.route('/checkout', methods=["GET"])
@u.login_required
def checkout():
	u.set_current_path(['index','/checkout'])
	if 'cart_items' in session:
		for items in session['cart_items']:
			if u.login_classifier() != items['username']:
				return redirect(url_for('my_cart'))
		with open('./resources/static/ecommerce/js/address-dropdown/provinces.json') as x:
			provinces = json.load(x)
		user_info = db.users.find_one({ 'username': u.login_classifier() })
		a = u.get_user_address(user_info)
		return render_template('ecommerce/checkout.html', title = 'Check Out', provinces = provinces, 
			username = session['username'],  
			name = user_info['name'], phone = user_info['phone'], email = user_info['email'],
			users_street = a[0].upper(), users_province = a[3].upper(), users_citymun = a[2].upper(), users_barangay =  a[1].upper(),
			cart_count = u.cart()[0], cart = u.cart_classifier(), subtotal = u.cart()[1]
			),200
	else:
		return redirect(url_for('index'))
	
#import checkout process (add/change profile & add/change address)
from ecommerce import checkout_process

#My Orders Page
@app.route('/myorders', methods=["GET"])
@u.login_required
def my_orders():
	u.set_current_path(['index','/myorders'])
	
	if 'order_id' in session:
		order_id = session['order_id']
	else:
		return redirect(url_for(u.get_current_path()[0]))

	orders = db.orders.find({ 'username': u.login_classifier() }).sort('date', db.pymongo.DESCENDING)
	specific_order = db.orders.find({ 'username': u.login_classifier(), '_id':ObjectId(str(order_id)) })
	return render_template('ecommerce/my_orders.html', title = 'My Orders',
		username = session['username'], 
		orders = orders, order_id = order_id, 
		order_count = orders.count(),
		specific_order = specific_order,
		cart_count = u.cart()[0], cart = u.cart_classifier(), subtotal = u.cart()[1]
		),200

#View Specific Order
@app.route('/view_order')
def view_order():
	order_id = request.args.get('order_id', 0, type=str)
	if 'order_id' in session:
		session['order_id'] = order_id
		session.modified = True
	else:
		session['order_id'] = order_id

	return jsonify(redirect = 'ok')

#Dashboard
#import dashboard process
from ecommerce import dashboard_process
@app.route('/myaccount', methods=["GET"])
@u.login_required
def my_account():
	u.set_current_path(['index','/index'])
	user_info = db.users.find_one({ 'username': u.login_classifier() })
	a = u.get_user_address(user_info)
	if request.method == 'GET':
		with open('./resources/static/ecommerce/js/address-dropdown/provinces.json') as x:
			provinces = json.load(x)

		orders = db.orders.find({ 'username': u.login_classifier() }).sort('date', db.pymongo.DESCENDING)
		print(orders)
		return render_template('ecommerce/my-account.html',
				title = 'My Account', 
				orders = orders, order_count = orders.count(),
				cart_count = u.cart()[0], cart = u.cart_classifier(), subtotal = u.cart()[1],
				provinces = provinces,
				account = u.login_classifier(), username = u.login_classifier(),
				name = user_info['name'], birthdate = user_info['birthdate'], phone = user_info['phone'], email = user_info['email'],
				users_street = a[0], users_province = a[3], users_citymun = a[2], users_barangay =  a[1]
				),200

#Shop/Places Page
@app.route('/shop', methods=['GET','POST'])
@app.route('/places', methods=['GET','POST'])
def places():
	u.set_current_path(['index','/places'])
	r = u.set_get_region()
	return render_template('ecommerce/shop-landing-page.html',
		title = 'Places Page', 
		account = u.login_classifier(), 
		cart_count = u.cart()[0], cart = u.cart_classifier(), subtotal = u.cart()[1],
		region1 = db.fp('REGION I (ILOCOS REGION)'), car = db.fp('NATIONAL CAPITAL REGION (NCR)'), 
		region2 = db.fp('REGION II (CAGAYAN VALLEY)'), region3 = db.fp('REGION II (CAGAYAN VALLEY)'),
		ncr = db.fp('NATIONAL CAPITAL REGION (NCR)'), region4a = db.fp('REGION IV-A (CALABARZON)'),
		region5 = db.fp('REGION V (BICOL REGION)'), mimaropa = db.fp('REGION IV-B (MIMAROPA)'),
		region6 = db.fp('REGION VI (WESTERN VISAYAS)'), region7 = db.fp('REGION VII (CENTRAL VISAYAS)'),
		region8 = db.fp('REGION VIII (EASTERN VISAYAS)'), region9 = db.fp('REGION IX (ZAMBOANGA PENINSULA)'),
		region10 = db.fp('REGION X (NORTHERN MINDANAO)'), region11 = db.fp('REGION XI (DAVAO REGION)'),
		region12 = db.fp('REGION XII (SOCCSKSARGEN)'), caraga = db.fp('REGION XIII (Caraga)'),
		barmm = db.fp('BANGSAMORO AUTONOMOUS REGION IN MUSLIM MINDANAO (BARMM)'),
		r1=r[0],r2=r[1],r3=r[2],r4=r[3],r5=r[4],r6=r[5],r7=r[6],r8=r[7],r9=r[8],
		r10=r[9],r11=r[10],r12=r[11],r13=r[12],r14=r[13],r15=r[14],r16=r[15]
		),200

#Shop/Places Pick Up Center Page (Specific Store)
@app.route('/places/<pick_up_center>')
def pick_up_center(pick_up_center):
	try:
		lst = list(pick_up_center.split(","))
		branch_name = lst[0]
		city = lst[1]
		path = '{},{}'.format(branch_name,city)
		if 'pick_up_center' in session:
			session['pick_up_center'] = path
			session.modified = True
		else:
			session['pick_up_center'] = path
		u.set_current_path(['pick_up_center', '/places/'+path])
		#
		dist = db.fsp(branch_name, city)
		if dist:
			dist_id = dist['_id']
			about = dist['about']
			bldg = dist['bldg']
			brgy = dist['brgy']
			province = dist['province']
			facebook = dist['facebook_page']
			policies = dist['policies']
			db_products = db.fapc(dist_id)
			products_to_cache = []
			for items in db_products:
				products_to_cache.append({ '_id': str(items['_id']), 'sku': items['sku'], 'name': items['name'], 'price': items['price'], 'undiscounted_price' : items['undiscounted_price'], 'image1': items['image1'], 'image2': items['image2'], 'category':items['category'], 'update_date': items['update_date'], 'long_desc': items['long_desc'], 'stock':items['stock'], 'distributor_id':items['distributor_id'], 'status': items['status'] })
				
			if 'products' in session:
				session.pop('products', None)
				session['products'] = products_to_cache
			else:
				session['products'] = products_to_cache
			
			return render_template('ecommerce/shop-pick-up-center.html', account = u.login_classifier(), 
				cart_count = u.cart()[0], cart = u.cart_classifier(), subtotal = u.cart()[1],
				about = about, bldg = bldg, brgy = brgy, province = province, 
				facebook = facebook, policies = policies, page = 'pick-up-center',
				title = '{}-{}'.format(branch_name,city), branch_name = branch_name, city = city, products = session['products'][0:8], products_pagination = session['products']), 200
		
	except IndexError:
		return redirect(url_for('error_handler'))
