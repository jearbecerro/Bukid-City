import pymongo
from pymongo import MongoClient
from pprint import pprint
from bson.objectid import ObjectId
from flask import session

cluster = MongoClient("mongodb://localhost:27017/")
#cluster = MongoClient("mongodb+srv://bukidcity:bukidcity@cluster0.er1qn.mongodb.net/bctest?retryWrites=true&w=majority")
db = cluster["bctest"]

product_category = db["product_category"]
sales = db["sales"]
categories = [
			{
			'date_entry': '',
			'category': 'Vegetables',
			'desc': ''
			},
			{
			'date_entry': '',
			'category': 'Spices',
			'desc': ''
			},
			{
			'date_entry': '',
			'category': 'Eggs',
			'desc': ''
			},
			{
			'date_entry': '',
			'category': 'Fruits',
			'desc': ''
			},
			{
			'date_entry': '',
			'category': 'Dry Goods',
			'desc': ''
			},
			{
			'date_entry': '',
			'category': 'Frozen Foods',
			'desc': ''
			},
			{
			'date_entry': '',
			'category': 'Fresh Meat',
			'desc': ''
			},
			{
			'date_entry': '',
			'category': 'Seafoods',
			'desc': ''
			}
	]

def insert_cat():
	product_category.insert_many(categories)

users = db["users"]

products = db["products"]

product_category = db["product_category"]

distributors = db["distributors"]

orders = db["orders"]

cart = db['cart']

#Add to cart DB Process
def add_to_cart(username, product_id, product_name, price, qty, img):
	find_users_cart = db.cart.find_one({ 'username': username, 'product_id': product_id })
	total_price = 0
	if find_users_cart:
		qty = find_users_cart['qty']
		total_qty = int(qty) + 1
		total_price = int(price) * total_qty
		db.cart.update({ 'username': username, 'product_id': product_id },{"$set": { 'qty':  total_qty, 'total_price': total_price } })
	else:
		cart = {
			'username': username,
			'product_id': product_id,
			'product_name': product_name,
			'price': price,
			'qty': qty,
			'total_price': price,
			'img': img
		}
		db.cart.insert_one(cart)

#Get the users cart Process
def set_users_cart_to_cache(username):
	users_cart = db.cart.find({ 'username': username })
	users_cart_list = []
	if users_cart:
		for items in users_cart:
			print(items['total_price'])
			users_cart_list.append({ 'username': username, 'product_id': items['product_id'], 'product_name': items['product_name'] , 'price': items['price'] , 'qty': items['qty'], 'total_price' : items['total_price'], 'img': items['img']})
		if 'cart_items' in session:
			session.pop('cart_items', None)
			session['cart_items'] = users_cart_list
			return session['cart_items']
		else:
			session['cart_items'] = users_cart_list
			return session['cart_items']
	return None

#Users Collection Process
def add_user(username, password, email):
	add_user = {
		'username': username,
		'password':password,
		'name':'',
		'birthdate': '',
		'phone':'',
		'email':email,
		'address':'',
		'mlm_id':''
	}
	users.insert(add_user)
    
def add_update_address(username, address):
	users.update({ 'username': username },{"$set":{"address": address }})

def add_update_personal(username, name, number, birthdate):
	personal_info = {
		'name':name,
		'birthdate': birthdate,
		'phone': number
	}
	users.update({ 'username': username },{"$set": personal_info})
def fp(region):
	return distributors.find( { 'region': region } )
	
def fsp(branch_name, city):	
	return distributors.find_one({ 'branch_name':branch_name, 'city':city })

def fapc(distributor_id):
	return products.find({ 'distributor_id': str(distributor_id) } )

