from flask import request, session, jsonify
from bson.objectid import ObjectId

from ecommerce import app
from ecommerce import utilities as u
from database import ecommerce_db as db

#Add to Cart Process
@app.route('/DF2056981F6FA6D9DBAB5C9AA6AA1D8B6EE89D10E37A076EAA4D5225BC3D11A2A9CCD9242A67B9C022D181F959A2A45668AE3D39C3388BC007920B82024992D9')
def add_to_cart():
	product_id = request.args.get('product_id', 0, type=str)
	product = db.products.find_one({ '_id': ObjectId(str(product_id)) })
	minicart = ''
	current_cart = []
	if product:
		product_name = product['name']
		price = product['price']
		img = product['image1']
		distributor_id = product['distributor_id']
		qty = '1'

		if u.login_classifier():
			#Add to cart DB Process
			find_users_cart = db.cart.find_one({ 'username': u.login_classifier(), 'product_id': product_id })
			total_price = 0
			if find_users_cart:
				qty = find_users_cart['qty']
				total_qty = int(qty) + 1
				total_price = int(price) * total_qty
				
				db.cart.update({ 'username': u.login_classifier(), 'product_id': product_id },{"$set": { 'qty':  total_qty, 'total_price': total_price } })
				u.set_users_cart_to_cache()
			else:
				cart = {
					'username': u.login_classifier(),
					'product_id': product_id,
					'distributor_id': distributor_id,
					'product_name': product_name,
					'price': int(price),
					'qty': int(qty),
					'total_price': int(price),
					'img': img
				}
				db.cart.insert_one(cart)

				u.set_users_cart_to_cache()

			return jsonify(cart_total = u.cart()[1], cart_count = u.cart()[0], cart = u.cart_classifier())
		else:
			pass
	return jsonify(cart_success = 'Invalid')

#Remove from Cart Process
@app.route('/remove_from_cart')
def remove_from_cart():
	product_id = request.args.get('product_id', 0, type=str)
	cart_id = request.args.get('cart_id', 0, type=str)

	db.cart.delete_one({ "username": u.login_classifier(), "product_id": product_id })
	count = db.cart.find({ "username": u.login_classifier() }).count()
	u.set_users_cart_to_cache()
	if count == 0:
		session.pop('cart_items', None)
		
	return jsonify(cart_id = cart_id, count = str(count), cart_subtotal = u.cart()[1], cart_total = u.cart()[1])
	
#Change Quantity and Total Price
@app.route('/change_qty_total_price')
def change_qty_total_price():
	product_id = request.args.get('product_id', 0, type=str)
	qty_value = request.args.get('qty_value', 0, type=str)
	price = request.args.get('price', 0, type=str)
	total_price = int(price) * int(qty_value)

	db.cart.update({ 'username': u.login_classifier(), 'product_id': product_id },{"$set": { 'qty':  qty_value, 'total_price': total_price } })
	
	if u.login_classifier():
		if 'cart_items' in session:
			for items in session['cart_items']:
				if product_id == items['product_id'] and u.login_classifier() == items['username']:
					items['qty'] = qty_value
					items['total_price'] = str(total_price)
					session.modified = True

	return jsonify(total_price = total_price, cart_subtotal = u.cart()[1], cart_total = u.cart()[1])
