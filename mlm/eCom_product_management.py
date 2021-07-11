from flask import Flask, request, session, render_template, redirect, url_for, jsonify, json, send_from_directory
import re, os, secrets, pathlib
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from PIL import Image
from datetime import date, datetime

from bson.objectid import ObjectId
import bson
from database import ecommerce_db as db
from mlm import utilities as u

from mlm import app

html = 'admin/product_management/ecommerce/'
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg'])

def allowed_file(filename):
	return '.' in filename and \
		   filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

#Distributor's Product Management -> Ecommerce Products Landing Page
@app.route('/distributor/products', methods=['GET'])
@u.distributor_required
def dist_products():
	categories = db.product_category.find().sort('category', db.pymongo.ASCENDING)
	products = db.products.find({ 'distributor_id': session['dist_id'] }).sort('name', db.pymongo.ASCENDING)

	if 'ecom_img_path1' in session:
		ecom_img_path1 = session['ecom_img_path1']
	else:
		ecom_img_path1 = 'ecommerce/img/product/add_product.png'

	if 'ecom_img_path2' in session:
		ecom_img_path2 = session['ecom_img_path1']
	else:
		ecom_img_path2 = 'ecommerce/img/product/add_product.png'
	return render_template(html+'ecommerce-products.html', 
		title = 'Product Management', main_page = '/product-management/ecommerce-products',
		member_name = 'Je Ar Becerro',
		page = 'eCommerce Products', product_management = 'open', ecommerce_products = 'active',
		categories = categories, products = products,
		ecom_img_path1 = ecom_img_path1, ecom_img_path2 = ecom_img_path2, 
		is_admin_login = u.is_admin_login(), is_member_login = u.is_member_login(), is_distributor_login = u.is_distributor_login(),
		dist_id = session['dist_id']
		)

#Product Management -> Ecommerce Products Landing Page
@app.route('/product-management/ecommerce-products', methods=['GET'])
@u.admin_required
def ecommerce_products():
	categories = db.product_category.find().sort('category', db.pymongo.ASCENDING)
	distributors = db.distributors.find().sort('branch_name', db.pymongo.ASCENDING)

	prod = db.products.find().sort('name', db.pymongo.ASCENDING)
	products = []
	for i in prod:
		d = db.distributors.find_one({ '_id': ObjectId(str(i['distributor_id'])) })
		if d:
			dist = "{}, {}, {}, {}".format(d['branch_name'],d['brgy'],d['city'],d['province'])
			products.append({ '_id': i['_id'], 'distributor_id': i['distributor_id'],'distributor': dist,'name': i['name'], 'price': i['price'],'undiscounted_price': i['undiscounted_price'], 'long_desc': i['long_desc'], 'image1': i['image1'], 'category': i['category'], 'stock': i['stock'], 'update_date': i['update_date']})
		else:
			products.append({ '_id': i['_id'],'distributor_id': i['distributor_id'],'distributor':'Inactive', 'name': i['name'], 'price': i['price'],'undiscounted_price': i['undiscounted_price'], 'long_desc': i['long_desc'], 'image1': i['image1'], 'category': i['category'], 'stock': i['stock'], 'update_date': i['update_date']})
	
	if 'ecom_img_path1' in session:
		ecom_img_path1 = session['ecom_img_path1']
	else:
		ecom_img_path1 = 'ecommerce/img/product/add_product.png'

	if 'ecom_img_path2' in session:
		ecom_img_path2 = session['ecom_img_path1']
	else:
		ecom_img_path2 = 'ecommerce/img/product/add_product.png'
	return render_template(html+'ecommerce-products.html', 
		title = 'Product Management', main_page = '/product-management/ecommerce-products',
		member_name = 'Je Ar Becerro',
		page = 'eCommerce Products', product_management = 'open', ecommerce_products = 'active',
		distributors = distributors, categories = categories, products = products,
		ecom_img_path1 = ecom_img_path1, ecom_img_path2 = ecom_img_path2, 
		is_admin_login = u.is_admin_login(), is_member_login = u.is_member_login(), is_distributor_login = u.is_distributor_login()
		)

@app.route('/redirect_single_view_product')
def redirect_single_view():
	try:
		product_id = request.args.get('product_id', 0, type=str)
		product = db.products.find_one({ '_id': ObjectId(str(product_id)) } , {'_id': 1})
		if product:
			if 'product_id' in session:
				session.pop('product_id',None)
				session['product_id'] = product_id
			else:
				session['product_id'] = product_id

			return jsonify(redirect = 'OK')
	except bson.errors.InvalidId:
		return redirect(url_for(u.error_handlers()))
	else:
		return redirect(url_for(u.error_handlers()))
	

#View Single Product
@app.route('/distributor/products/single-view')
@app.route('/product_management/ecommerce_products/view-edit-delete')
def product_id():
	categories = db.product_category.find().sort('category', db.pymongo.ASCENDING)
	distributors = db.distributors.find().sort('branch_name', db.pymongo.ASCENDING)
	if u.is_distributor_login == True or u.is_admin_login == True or u.is_member_login() == True:
		return redirect(url_for(u.error_handlers()))
	else:
		if 'product_id' in session:
			product = db.products.find_one({ '_id': ObjectId(str(session['product_id'])) })
			if 'ecom_img_path1' in session:
				ecom_img_path1 = session['ecom_img_path1']
			else:
				ecom_img_path1 = 'ecommerce/img/product/'+product['image1'] #db img

			if 'ecom_img_path2' in session:
				ecom_img_path2 = session['ecom_img_path1']
			else:
				ecom_img_path2 = 'ecommerce/img/product/'+product['image2'] #db img	
			return render_template(html+'ecommerce-single-product.html', 
			title = 'Product Management', main_page = '/product-management/ecommerce-products',
			member_name = 'Je Ar Becerro',
			page = 'Single Product', product_management = 'open', ecommerce_products = 'active',
			distributors = distributors, categories = categories, product = product, product_id = session['product_id'],
			ecom_img_path1 = ecom_img_path1, ecom_img_path2 = ecom_img_path2, 
			is_admin_login = u.is_admin_login(), is_member_login = u.is_member_login(), is_distributor_login = u.is_distributor_login(),
			dist_id = session['dist_id']
			)
		else:
			return redirect(url_for(u.error_handlers()))

#Add Ecommerce Product
@app.route('/add_ecom_product')
def add_eProduct():
	try:
		product_name = request.args.get('product_name', 0, type=str)
		price = request.args.get('price', 0, type=str)
		undiscounted_price = request.args.get('undiscounted_price', 0, type=str)
		description = request.args.get('description', 0, type=str)
		category = request.args.get('category', 0, type=str)
		stock = request.args.get('stock', 0, type=str)
		distributor = 'init'
		if u.is_admin_login() == True:
			distributor = request.args.get('distributor', 0, type=str)
		if u.is_distributor_login() == True:
			distributor = session['dist_id']

		print(distributor)
		errors = []
		if 'img1_filename' not in session:
			errors.append('<br>Please upload a picture of Image 1.')
			errors_in_text = ""
		if 'img2_filename' not in session:
			errors.append('<br>Please upload a picture of Image 2.')
		if len(product_name) == 0:
			errors.append('<br>&nbspProduct Name field is empty')
		if len(price) == 0:
			errors.append('<br>&nbspPrice field is empty')
		if price.isnumeric() == False and len(price) != 0:
			errors.append('<br>&nbspPrice must be digit')
		if len(undiscounted_price) == 0:
			errors.append('<br>&nbspUndiscounted Price field is empty')
		if undiscounted_price.isnumeric() == False and len(undiscounted_price) != 0:
			errors.append('<br>&nbspPrice must be digit')
		if len(stock) == 0:
			errors.append('<br>&nbspStock field is empty')
		if stock.isnumeric() == False and len(stock) != 0:
			errors.append('<br>&nbspStock must be digit')
		if category == 'None':
			errors.append("<br>&nbspPlease select a product's category")
		if distributor == 'None':
			errors.append("<br>&nbspPlease select a distributor")

		if len(errors) == 0:
			product = {
				"sku": "",
				"image1": session['img1_filename'],
				"image2": session['img2_filename'],
				"name": product_name,
				"price": price,
				"undiscounted_price": undiscounted_price,
				"long_desc": description,
				"category": category,
				"update_date": datetime.now().strftime('%B %d, %Y @ %I:%M:%S %p'),
				"stock": stock,
				"distributor_id": distributor,
				"total_sales": 0,
				"total_orders": 0,
				"status":"active"
			}
			db.products.insert_one(product)
			if 'img1_filename' in session and 'img2_filename' in session:
				session.pop('img1_filename',None)
				session.pop('img2_filename',None)
				if 'ecom_img_path1' in session and 'ecom_img_path2' in session:
					session.pop('ecom_img_path1',None)
					session.pop('ecom_img_path2',None)

			img1 = url_for('static', filename='ecommerce/img/product/add_product.png')
			img2 = url_for('static', filename='ecommerce/img/product/add_product.png')
			return jsonify(success = 'Product Added', img1 = img1, img2 = img2)
		return jsonify(errors = errors)
	except TypeError:
		return redirect(url_for(u.error_handlers()))
	else:
		return redirect(url_for(u.error_handlers()))


#Update Ecommerce Product
@app.route('/update_ecom_product')
def update_eProduct():
	try:
		product_name = request.args.get('product_name', 0, type=str)
		price = request.args.get('price', 0, type=str)
		undiscounted_price = request.args.get('undiscounted_price', 0, type=str)
		description = request.args.get('description', 0, type=str)
		category = request.args.get('category', 0, type=str)
		stock = request.args.get('stock', 0, type=str)
		distributor = request.args.get('distributor', 0, type=str)

		errors = []

		if len(product_name) == 0:
			errors.append('<br>&nbspProduct Name field is empty')
		if len(price) == 0:
			errors.append('<br>&nbspPrice field is empty')
		if price.isnumeric() == False and len(price) != 0:
			errors.append('<br>&nbspPrice must be digit')
		if len(undiscounted_price) == 0:
			errors.append('<br>&nbspUndiscounted Price field is empty')
		if undiscounted_price.isnumeric() == False and len(undiscounted_price) != 0:
			errors.append('<br>&nbspPrice must be digit')
		if len(stock) == 0:
			errors.append('<br>&nbspStock field is empty')
		if stock.isnumeric() == False and len(stock) != 0:
			errors.append('<br>&nbspStock must be digit')
		if category == 'None':
			errors.append("<br>&nbspPlease select a product's category")
		if distributor == 'None':
			errors.append("<br>&nbspPlease select a distributor")

		if len(errors) == 0:
			updir = os.path.join(basedir, '../resources/static/ecommerce/img/product')
			if 'img1_filename' in session:
				db.products.update({ '_id': ObjectId(str(session['product_id']))},{"$set": {'image1':session['img1_filename']} })
				session.pop('img1_filename', None)
				if 'ecom_img_path1' in session:
					session.pop('ecom_img_path1',None)
			if 'img2_filename' in session :
				db.products.update({ '_id': ObjectId(str(session['product_id']))},{"$set": {'image2':session['img2_filename']} })
				session.pop('img2_filename', None)
				if 'ecom_img_path2' in session:
					session.pop('ecom_img_path2',None)
			product = {
					"sku": "",
					"name": product_name,
					"price": price,
					"undiscounted_price": undiscounted_price,
					"long_desc": description,
					"category": category,
					"update_date": datetime.now().strftime('%B %d, %Y @ %I:%M:%S %p'),
					"stock": stock,
					"distributor_id": distributor,
					"status":"active"
				}

			db.products.update({ '_id': ObjectId(str(session['product_id']))},{"$set": product })
			return jsonify(success = 'Product Added')
		return jsonify(errors = errors)

	except TypeError:
		return redirect(url_for(u.error_handlers()))
	else:
		return redirect(url_for(u.error_handlers()))
	

@app.route('/delete_ecom_product')
def delete_eProduct():
	try:
		product_id = request.args.get('id', 0, type=str)
		Exist = db.products.find_one({ '_id': ObjectId(str(product_id)) })
		if Exist:
			remove_img_after_delete(Exist['image1'])
			remove_img_after_delete(Exist['image2'])
			db.products.delete_one({ '_id': ObjectId(str(session['product_id'])) })
			session.pop('product_id',None)
			return jsonify(success = 'Product Deleted')
		else:
			return jsonify(error = 'Do not modify the values!')
	except bson.errors.InvalidId:
		if u.is_admin_login() == True:
			return redirect('/product-management/ecommerce-products')
		elif u.is_distributor_login() == True:
			return redirect('/distributor/products')
		elif u.is_member_login() == True:
			return redirect('/profile')
		else:
			return redirect('/member/login')

def remove_img_after_delete(img):
	updir = os.path.join(basedir, '../resources/static/ecommerce/img/product/')
	file_exst = os.path.exists('{}{}'.format(updir, img))
	if file_exst:
		os.remove(os.path.join(updir, img))
	
def upload_classifier(file, files, func):
	if files and allowed_file(files.filename):
		filename = secure_filename(files.filename)
		random_hex = secrets.token_hex(8)
		_, f_ext = os.path.splitext(filename)
		upfilename = random_hex + f_ext
		updir = os.path.join(basedir, '../resources/static/ecommerce/img/product/')
		pathlib.Path(updir).mkdir(exist_ok=True)
		picture_path = os.path.join(updir, upfilename)
		

		if func == 'Add':
			if file == 1:
				if 'img1_filename' in session:
					file_exst = os.path.exists('{}{}'.format(updir,session['img1_filename']))
					if file_exst:
						os.remove(os.path.join(updir, session['img1_filename']))
						session.pop('img1_filename',None)
						session['img1_filename'] = upfilename
						upload_img(files, picture_path)
						if 'ecom_img_path1' in session:
							session.pop('ecom_img_path1',None)
							session['ecom_img_path1'] = 'ecommerce/img/product/'+session['img1_filename']
						else:
							session['ecom_img_path1'] = 'ecommerce/img/product/'+session['img1_filename']
					
						return url_for('static', filename='ecommerce/img/product/'+session['img1_filename'])
					else:
						session.pop('img1_filename',None)
						session['img1_filename'] = upfilename
						upload_img(files, picture_path)
						return url_for('static', filename='ecommerce/img/product/'+session['img1_filename'])

				else:
					session['img1_filename'] = upfilename
					upload_img(files, picture_path)
					if 'ecom_img_path1' in session:
						session.pop('ecom_img_path1',None)
						session['ecom_img_path1'] = 'ecommerce/img/product/'+session['img1_filename']
					else:
						session['ecom_img_path1'] = 'ecommerce/img/product/'+session['img1_filename']
					
					return url_for('static', filename='ecommerce/img/product/'+session['img1_filename'])


			if file == 2:
				if 'img2_filename' in session:
					file_exst = os.path.exists('{}{}'.format(updir,session['img2_filename']))
					if file_exst:
						os.remove(os.path.join(updir, session['img2_filename']))
						session.pop('img2_filename',None)
						session['img2_filename'] = upfilename
						upload_img(files, picture_path)
						if 'ecom_img_path2' in session:
							session.pop('ecom_img_path2',None)
							session['ecom_img_path2'] = 'ecommerce/img/product/'+session['img2_filename']
						else:
							session['ecom_img_path2'] = 'ecommerce/img/product/'+session['img2_filename']
					
						return url_for('static', filename='ecommerce/img/product/'+session['img2_filename'])
					else:
						session.pop('img2_filename',None)
						session['img2_filename'] = upfilename
						upload_img(files, picture_path)
						return url_for('static', filename='ecommerce/img/product/'+session['img2_filename'])

				else:
					session['img2_filename'] = upfilename
					upload_img(files, picture_path)
					if 'ecom_img_path2' in session:
						session.pop('ecom_img_path2',None)
						session['ecom_img_path2'] = 'ecommerce/img/product/'+session['img2_filename']
					else:
						session['ecom_img_path2'] = 'ecommerce/img/product/'+session['img2_filename']
				
					return url_for('static', filename='ecommerce/img/product/'+session['img2_filename'])

		if func == 'Upd':
			if file == 1:
				if 'img1_filename' in session:
					file_exst = os.path.exists('{}{}'.format(updir,session['img1_filename']))
					if file_exst:
						os.remove(os.path.join(updir, session['img1_filename']))
						session.pop('img1_filename',None)
						session['img1_filename'] = upfilename
						upload_img(files, picture_path)
						if 'ecom_img_path1' in session:
							session.pop('ecom_img_path1',None)
							session['ecom_img_path1'] = 'ecommerce/img/product/'+session['img1_filename']
						else:
							session['ecom_img_path1'] = 'ecommerce/img/product/'+session['img1_filename']
					
						return url_for('static', filename='ecommerce/img/product/'+session['img1_filename'])
					else:
						session.pop('img1_filename',None)
						session['img1_filename'] = upfilename
						upload_img(files, picture_path)
						return url_for('static', filename='ecommerce/img/product/'+session['img1_filename'])

				else:
					session['img1_filename'] = upfilename
					upload_img(files, picture_path)
					if 'ecom_img_path1' in session:
						session.pop('ecom_img_path1',None)
						session['ecom_img_path1'] = 'ecommerce/img/product/'+session['img1_filename']
					else:
						session['ecom_img_path1'] = 'ecommerce/img/product/'+session['img1_filename']
					
					return url_for('static', filename='ecommerce/img/product/'+session['img1_filename'])
			if file == 2:
				if 'img2_filename' in session:
					file_exst = os.path.exists('{}{}'.format(updir,session['img2_filename']))
					if file_exst:
						os.remove(os.path.join(updir, session['img2_filename']))
						session.pop('img2_filename',None)
						session['img2_filename'] = upfilename
						upload_img(files, picture_path)
						if 'ecom_img_path2' in session:
							session.pop('ecom_img_path2',None)
							session['ecom_img_path2'] = 'ecommerce/img/product/'+session['img2_filename']
						else:
							session['ecom_img_path2'] = 'ecommerce/img/product/'+session['img2_filename']
					
						return url_for('static', filename='ecommerce/img/product/'+session['img2_filename'])
					else:
						session.pop('img2_filename',None)
						session['img2_filename'] = upfilename
						upload_img(files, picture_path)
						return url_for('static', filename='ecommerce/img/product/'+session['img2_filename'])

				else:
					session['img2_filename'] = upfilename
					upload_img(files, picture_path)
					if 'ecom_img_path2' in session:
						session.pop('ecom_img_path2',None)
						session['ecom_img_path2'] = 'ecommerce/img/product/'+session['img2_filename']
					else:
						session['ecom_img_path2'] = 'ecommerce/img/product/'+session['img2_filename']
					
					return url_for('static', filename='ecommerce/img/product/'+session['img2_filename'])


def upload_img(files, picture_path):
	output_size = (600, 600)
	i = Image.open(files)
	i.thumbnail(output_size)
	i.save(picture_path)

@app.route('/up_ecom_product_img1', methods=['POST'])
def up_ecom_product_img1():
	if request.method == 'POST':
		files = request.files['fileimage1']
		product = db.products.find_one({ '_id' :  ObjectId(str(session['product_id']))}, {'image1': 1})
		updir = os.path.join(basedir, '../resources/static/ecommerce/img/product/')

		file_exist = os.path.exists('{}{}'.format(updir, product['image1']))

		if file_exist:
			os.remove(os.path.join(updir, product['image1']))
		print(allowed_file(files.filename))
		if allowed_file(files.filename) == False:
			return jsonify(error = 'true')
		if allowed_file(files.filename) == True:
			return jsonify(img_path = upload_classifier(1, files, 'Upd'), allowed = 'true')

@app.route('/up_ecom_product_img2', methods=['POST'])
def up_ecom_product_img2():
	if request.method == 'POST':
		files = request.files['fileimage2']
		product = db.products.find_one({ '_id' :  ObjectId(str(session['product_id']))}, {'image2': 1})
		updir = os.path.join(basedir, '../resources/static/ecommerce/img/product/')

		file_exist = os.path.exists('{}{}'.format(updir, product['image2']))

		if file_exist:
			os.remove(os.path.join(updir, product['image2']))

		if allowed_file(files.filename) == False:
			return jsonify(error = 'true')
		if allowed_file(files.filename) == True:
			return jsonify(img_path = upload_classifier(2, files, 'Upd'), allowed = 'true')

@app.route('/add_ecom_product_img1', methods=['POST'])
def add_ecom_product_img1():
	if request.method == 'POST':
		files = request.files['fileimage1']
		if allowed_file(files.filename) == False:
			return jsonify(error = 'true')
		if allowed_file(files.filename) == True:
			return jsonify(img_path = upload_classifier(1, files, 'Add'), allowed = 'true')
		


@app.route('/add_ecom_product_img2', methods=['POST'])
def add_ecom_product_img2():
	if request.method == 'POST':
		files = request.files['fileimage2']
		if allowed_file(files.filename) == False:
			return jsonify(error = 'true')
		if allowed_file(files.filename) == True:
			return jsonify(img_path = upload_classifier(2, files, 'Add'), allowed = 'true')
