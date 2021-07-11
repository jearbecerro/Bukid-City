from flask import Flask, request, session, render_template, redirect, url_for, jsonify, json, send_from_directory
import re
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
import bson
from datetime import date, datetime

from mlm import app
from mlm import utilities as u
from database import ecommerce_db as db
from pprint import pprint

html = 'admin/order_management/'

@app.route('/orders-management/pending-orders')
def pending_orders():
	if u.is_admin_login() == True or u.is_distributor_login() == True or u.is_member_login() == True:
		if u.is_admin_login() == True:
			pending_orders = db.orders.find({ 'status': 'Processing' })
		if u.is_distributor_login() == True and 'dist_id' in session:
			pending_orders = db.orders.find({ 'status': 'Processing', 'distributor_id': session['dist_id'] })
			print(session['dist_id'])
		if u.is_member_login() == True:
			return redirect('/profile')
		return render_template(html+'pending_orders.html', 
			title = 'Order Management',
			member_name = 'Je Ar Becerro',
			page = 'Pending Orders', orders = 'open', pending = 'active',
			pending_orders = pending_orders, 
			is_admin_login = u.is_admin_login(), is_member_login = u.is_member_login(), is_distributor_login = u.is_distributor_login()
			)
	else:
		return redirect('/admin/login')

@app.route('/orders-management/orders-for-delivery')
def orders_for_delivery():
	if u.is_admin_login() == True or u.is_distributor_login() == True or u.is_member_login() == True:
		if u.is_admin_login() == True:
			transporting_orders = db.orders.find({ 'status': 'Transporting' })
		if u.is_distributor_login() == True and 'dist_id' in session:
			transporting_orders = db.orders.find({ 'status': 'Transporting', 'distributor_id': session['dist_id'] })
		if u.is_member_login() == True:
			return redirect('/profile')
		
		return render_template(html+'orders_for_delivery.html', 
			title = 'Order Management',
			member_name = 'Je Ar Becerro',
			page = 'Orders For Delivery', orders = 'open', for_delivery = 'active',
			transporting_orders = transporting_orders, 
			is_admin_login = u.is_admin_login(), is_member_login = u.is_member_login(), is_distributor_login = u.is_distributor_login()
			)
	else:
		return redirect('/admin/login')

@app.route('/orders-management/delivered-orders')
def delivered_orders():
	if u.is_admin_login() == True or u.is_distributor_login() == True or u.is_member_login() == True:
		if u.is_admin_login() == True:
			delivered_orders = db.orders.find({ 'status': 'Delivered' })
		if u.is_distributor_login() == True and 'dist_id' in session:
			delivered_orders = db.orders.find({ 'status': 'Delivered', 'distributor_id': session['dist_id'] })
		if u.is_member_login() == True:
			return redirect('/profile')
		return render_template(html+'delivered_orders.html', 
			title = 'Order Management',
			member_name = 'Je Ar Becerro',
			page = 'Delivered Orders', orders = 'open', delivered = 'active',
			delivered_orders = delivered_orders, 
			is_admin_login = u.is_admin_login(), is_member_login = u.is_member_login(), is_distributor_login = u.is_distributor_login()
			)
	else:
		return redirect('/admin/login')

@app.route('/cancel_order')
def cancel_order():
	try:
		order_id = request.args.get('order_id', 0, type=str)
		username = request.args.get('username', 0, type=str)
		user = request.args.get('user', 0, type=str)
		admin = request.args.get('admin', 0, type=str)
		if u.is_admin_login() == True:
			Exists = db.orders.find_one({ '_id': ObjectId(str(order_id)), 'username': username, 'status': 'Processing' })
		elif u.is_distributor_login() == True and 'dist_id' in session:
			Exists = db.orders.find_one({ '_id': ObjectId(str(order_id)),'distributor_id': session['dist_id'] , 'username': username, 'status': 'Processing' })
		else:
			Exists = db.orders.find_one({ '_id': ObjectId(str(order_id)), 'username': username, 'status': 'Processing' })
		if Exists:
			if admin == 'admin' and user == '':
				delete_order(order_id, username)
				return jsonify(success = 'True', admin = 'True')
			elif user == 'buyer' and admin == '':
				delete_order(order_id, username)
				return jsonify(success = 'True', admin = 'False')
			else:
				return jsonify(error = 'Do not modify the values! trest')
		else:
			return jsonify(error = 'Do not modify the values!')
	except bson.errors.InvalidId:
		return redirect('/')
	else:
		return redirect('/')

def delete_order(order_id, username):
	db.orders.delete_one({ '_id': ObjectId(str(order_id)), 'username': username, 'status': 'Processing' })
	if 'order_id' in session:
		session.pop('order_id', None)

@app.route('/for_delivery')
def for_delivery():
	try:
		order_id = request.args.get('order_id', 0, type=str)
		username = request.args.get('username', 0, type=str)

		if u.is_admin_login() == True:
			Exists = db.orders.find_one({ '_id': ObjectId(str(order_id)), 'username': username, 'status': 'Processing' })
		if u.is_distributor_login() == True and 'dist_id' in session:
			Exists = db.orders.find_one({ '_id': ObjectId(str(order_id)),'distributor_id': session['dist_id'] , 'username': username, 'status': 'Processing' })
		
		if Exists:
			db.orders.update({ '_id': ObjectId(str(order_id))},{"$set": { 'status': 'Transporting','date_fulfill': datetime.now().strftime('%B %d, %Y')  } })
			return jsonify(success = 'True')
		else:
			return jsonify(error = 'Do not modify the values!')
	except bson.errors.InvalidId:
		return redirect('/')
	else:
		return redirect('/')

@app.route('/delivered')
def delivered():
	try:
		order_id = request.args.get('order_id', 0, type=str)
		username = request.args.get('username', 0, type=str)

		
		if u.is_admin_login() == True:
			Exists = db.orders.find_one({ '_id': ObjectId(str(order_id)), 'username': username, 'status': 'Transporting' })
		if u.is_distributor_login() == True and 'dist_id' in session:
			Exists = db.orders.find_one({ '_id': ObjectId(str(order_id)),'distributor_id': session['dist_id'] , 'username': username, 'status': 'Transporting' })
			
		if Exists:
			sales = db.sales.find_one({ 'date_view': datetime.now().strftime('%B %d, %Y'), 'distributor_id': session['dist_id'] })#add distributor_id dynamically
			orders = []

			if sales:
				for x in sales['orders']:
					orders.append({ 'order_id': str( x['order_id']), 'buyer': x['buyer'] })
				orders.append({ 'order_id': str(Exists['_id']), 'buyer': Exists['buyer'] })#order._id

				total_orders = len(orders)
				total_sales = int(sales['total_sales'] + int(Exists['total']))
				sales_dict = {
					'date':datetime.utcnow(),
					'date_view':datetime.now().strftime('%B %d, %Y'),
					'distributor_id': session['dist_id'],
					'total_sales': int(total_sales),
					'total_orders': int(total_orders),
					'orders': orders #makita ang ge order
					}
				db.orders.update({ '_id': ObjectId(str(order_id))},{"$set": { 'status': 'Delivered', 'date_delivered': datetime.now().strftime('%B %d, %Y') } })
				db.sales.update_one({ 'date_view': datetime.now().strftime('%B %d, %Y'), 'distributor_id': session['dist_id'] },{"$set": sales_dict })
				
				for i in Exists['product_ordered']:
					p = db.products.find_one({ '_id': ObjectId(str(i['product_id'])) }, { 'total_sales': 1, 'total_orders': 1 })
					prev_totalSales = p['total_sales']
					prev_totalOrders = p['total_orders']

					p_totalSales = int(i['total_price']) + int(prev_totalSales)
					p_totalOrders = int(prev_totalOrders) + 1
					
					db.products.update_one({ '_id': ObjectId(str(i['product_id'])) },{"$set": { 'total_sales': p_totalSales, 'total_orders': p_totalOrders } })
				
				return jsonify(success = 'True')
			else:
				orders.append({ 'order_id': str(Exists['_id']), 'buyer': Exists['buyer'] })#order._id
				sales_dict = {
					'date':datetime.utcnow(),
					'date_view':datetime.now().strftime('%B %d, %Y'),
					'distributor_id':session['dist_id'],
					'total_sales': int(Exists['total']),
					'total_orders': 1,
					'orders': orders
					}
				db.orders.update({ '_id': ObjectId(str(order_id))},{"$set": { 'status': 'Delivered' } })
				db.sales.insert_one( sales_dict ) #add distributor_id

				for i in Exists['product_ordered']:
					p = db.products.find_one({ '_id': ObjectId(str(i['product_id'])) }, { 'total_sales': 1, 'total_orders': 1 })
					prev_totalSales = p['total_sales']
					prev_totalOrders = p['total_orders']

					p_totalSales = int(i['total_price']) + int(prev_totalSales)
					p_totalOrders = int(prev_totalOrders) + 1
					
					db.products.update_one({ '_id': ObjectId(str(i['product_id'])) },{"$set": { 'total_sales': p_totalSales, 'total_orders': p_totalOrders } })

				return jsonify(success = 'True')


			
			if Exists['status'] != 'Transporting':
				return jsonify(error = 'This order is not fulfill!')
		else:
			return jsonify(error = 'Do not modify the values!')

	except bson.errors.InvalidId:
		return redirect('/')
	else:
		return redirect('/')

app.config['UPLOAD_FOLDER'] = '../data/'
import os
@app.route("/data/<string:filename>", methods=['GET'])
def get_file(filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER']), filename=filename)