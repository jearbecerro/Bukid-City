from flask import Flask, request, session, render_template, redirect, url_for, jsonify, json, send_from_directory
import re, os, secrets, pathlib
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from PIL import Image
from datetime import date, datetime

from bson.objectid import ObjectId
import bson
from database import mlm_db as db
from mlm import utilities as u

from mlm import app

mlm_db = db.cluster["mlm"] #MLM database separate into ecommerce database
db_products = mlm_db['products']


html = 'admin/product_management/mlm/'
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg'])

def allowed_file(filename):
	return '.' in filename and \
		   filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.route('/product-management/mlm-products')
@u.admin_required
def mlm_products():
	products = db_products.find().sort('price', db.pymongo.ASCENDING)
	if 'mlm_img_path' in session:
		mlm_img_path = session['mlm_img_path']
	else:
		mlm_img_path = 'ecommerce/img/product/add_product.png'

	return render_template(html+'mlm-products.html', 
		title = 'Product Management', main_page = '/product-management/mlm-products',
		member_name = 'Je Ar Becerro',
		page = 'MLM Products', product_management = 'open', mlm_products = 'active',
		products = products, mlm_img_path = mlm_img_path, 
		is_admin_login = u.is_admin_login(), is_member_login = u.is_member_login(), is_distributor_login = u.is_distributor_login()
		)

@app.route('/redirect_single_view_mlm_product')
@u.admin_required
def redirect_single_view_mlm():
	try:
		product_id = request.args.get('product_id', 0, type=str)
		product = db_products.find_one({ '_id': ObjectId(str(product_id)) } , {'_id': 1})
		if product:
			if 'mlm_product_id' in session:
				session.pop('mlm_product_id',None)
				session['mlm_product_id'] = product_id
			else:
				session['mlm_product_id'] = product_id
			return jsonify(redirect = 'OK')
	except bson.errors.InvalidId:
		return redirect(url_for(u.error_handlers()))
	else:
		return redirect(url_for(u.error_handlers()))
	

#View Single Product
@app.route('/product_management/mlm_products/view-edit-delete')
@u.admin_required
def mlm_product_id():
	if 'mlm_product_id' in session:
		product = db_products.find_one({ '_id': ObjectId(str(session['mlm_product_id'])) })

		inc = str(product['inclussions']).replace("[", "").replace("]", "").replace("',", "\n").replace("'", "").replace("", "")
		desc = str(product['description']).replace("[", "").replace("]", "").replace("',", "\n").replace("'", "").replace("", "")

		if 'mlm_img_path' in session:
			mlm_img_path = session['mlm_img_path']
		else:
			mlm_img_path = product['image']

		return render_template(html+'mlm-single-product.html', 
		title = 'Product Management', main_page = '/product-management/mlm-products',
		member_name = 'Je Ar Becerro', mlm_img_path = mlm_img_path,
		page = 'Single Product', product_management = 'open', mlm_products = 'active',
		product = product, inc = inc, desc =desc, 
		is_admin_login = u.is_admin_login(), is_member_login = u.is_member_login(), is_distributor_login = u.is_distributor_login()
		)
	else:
		return redirect(url_for('mlm_products'))

@app.route('/add_mlm_product')
@u.admin_required
def add_mlm_product():
	try:
		product_name = request.args.get('product_name', 0, type=str)
		price = request.args.get('price', 0, type=str)
		inclussions = request.args.get('inclussions', 0, type=str)
		description = request.args.get('description', 0, type=str)
		errors = []

		if 'mlm_img_filename' not in session:
			errors.append("<br>&nbspPlease upload a product image.")
		if len(product_name) == 0:
			errors.append('<br>&nbspProduct Name field is empty')
		if len(price) == 0:
			errors.append('<br>&nbspPrice field is empty')
		if price.isnumeric() == False and len(price) != 0:
			errors.append('<br>&nbspPrice must be digit')
		if len(inclussions) == 0:
			errors.append("<br>&nbspInclussions' textarea is empty")
		if len(description) == 0:
			errors.append("<br>&nbspDistributor's textarea is empty")

		if len(errors) == 0:
			list_of_incl = inclussions.splitlines()
			list_of_desc = description.splitlines()
			product = {
				"date_entry": datetime.now().strftime('%B %d, %Y @ %I:%M:%S %p'),
				"image": session['mlm_img_filename'],
				"name": product_name,
				"price": price,
				"inclussions": list_of_incl,
				"description": list_of_desc,
				"status":"active"
			}
			db_products.insert_one(product)
			session.pop('mlm_img_filename',None)
			session.pop('mlm_img_path',None)
			img = url_for('static', filename='ecommerce/img/product/add_product.png')
			return jsonify(success = 'Product Added', img = img)

		return jsonify(errors = errors)
	except TypeError:
		return redirect(url_for(u.error_handlers()))
	else:
		return redirect(url_for(u.error_handlers()))
	

@app.route('/update_mlm_product')
@u.admin_required
def update_mlm_product():
	try:
		product_name = request.args.get('product_name', 0, type=str)
		price = request.args.get('price', 0, type=str)
		inclussions = request.args.get('inclussions', 0, type=str)
		description = request.args.get('description', 0, type=str)
		errors = []

		if len(product_name) == 0:
			errors.append('<br>&nbspProduct Name field is empty')
		if len(price) == 0:
			errors.append('<br>&nbspPrice field is empty')
		if price.isnumeric() == False and len(price) != 0:
			errors.append('<br>&nbspPrice must be digit')
		if len(inclussions) == 1:
			errors.append("<br>&nbspInclussions' textarea is empty")
		if len(description) == 1:
			errors.append("<br>&nbspDistributor's textarea is empty")

		if len(errors) == 0:
			list_of_incl = inclussions.splitlines()
			list_of_desc = description.splitlines()

			if 'mlm_img_filename' in session:
				db_products.update({ '_id': ObjectId(str(session['mlm_product_id']))},{"$set": {'image':session['mlm_img_filename']} })
				session.pop('mlm_img_filename', None)

			product = {
				"date_entry": datetime.now().strftime('%B %d, %Y @ %I:%M:%S %p'),
				"name": product_name,
				"price": price,
				"inclussions": list_of_incl,
				"description": list_of_desc,
				"status":"active"
			}
			db_products.update({ '_id': ObjectId(str(session['mlm_product_id']))},{"$set": product })

			session.pop('mlm_img_filename',None)
			session.pop('mlm_img_path',None)
			img = url_for('static', filename='admin/imgs/product/add_product.png')
			return jsonify(success = 'Product Added', img = img)
		return jsonify(errors = errors)
	except TypeError:
		return redirect(url_for(u.error_handlers()))
	else:
		return redirect(url_for(u.error_handlers()))

@app.route('/add_mlm_product_img', methods=['POST'])
@u.admin_required
def add_mlm_product_img():
	if request.method == 'POST':
		files = request.files['fileimage']
		if allowed_file(files.filename) == False:
			return jsonify(error = 'true')
		if allowed_file(files.filename) == True:
			return jsonify(img_path = upload_classifier(files, 'Add'), allowed = 'true')

@app.route('/up_mlm_product_img', methods=['POST'])
@u.admin_required
def up_mlm_product_img():
	if request.method == 'POST':
		files = request.files['fileimage']
		product = db_products.find_one({ '_id' :  ObjectId(str(session['mlm_product_id']))}, {'image': 1})
		updir = os.path.join(basedir, '../resources/static/admin/imgs/product/')

		file_exist = os.path.exists('{}{}'.format(updir, product['image']))

		if file_exist:
			os.remove(os.path.join(updir, product['image']))

		if allowed_file(files.filename) == False:
			return jsonify(error = 'true')
		if allowed_file(files.filename) == True:
			return jsonify(img_path = upload_classifier(files, 'Upd'), allowed = 'true')

def upload_classifier(files, func):
	if files and allowed_file(files.filename):#kinda redundunt but its work :)
		filename = secure_filename(files.filename)
		random_hex = secrets.token_hex(8)
		_, f_ext = os.path.splitext(filename)
		upfilename = random_hex + f_ext
		updir = os.path.join(basedir, '../resources/static/admin/imgs/product/')
		pathlib.Path(updir).mkdir(exist_ok=True)
		picture_path = os.path.join(updir, upfilename)
		
		if func == 'Add':
			if 'mlm_img_filename' in session:
				file_exst = os.path.exists('{}{}'.format(updir,session['mlm_img_filename']))
				if file_exst:
					os.remove(os.path.join(updir, session['mlm_img_filename']))
					session.pop('mlm_img_filename',None)
					session['mlm_img_filename'] = upfilename
					upload_img(files, picture_path)
					if 'mlm_img_path' in session:
						session.pop('mlm_img_path',None)
						session['mlm_img_path'] = 'admin/imgs/product/'+session['mlm_img_filename']
					else:
						session['mlm_img_path'] = 'admin/imgs/product/'+session['mlm_img_filename']

					return url_for('static', filename='admin/imgs/product/'+session['mlm_img_filename'])
				else:
					session.pop('mlm_img_filename',None)
					session['mlm_img_filename'] = upfilename
					upload_img(files, picture_path)

					return url_for('static', filename='admin/imgs/product/'+session['mlm_img_filename'])
			else:
				session['mlm_img_filename'] = upfilename
				upload_img(files, picture_path)
				if 'mlm_img_path' in session:
					session.pop('mlm_img_path',None)
					session['mlm_img_path'] = 'admin/imgs/product/'+session['mlm_img_filename']
				else:
					session['mlm_img_path'] = 'admin/imgs/product/'+session['mlm_img_filename']
				return url_for('static', filename='admin/imgs/product/'+session['mlm_img_filename'])

		if func == 'Upd':
			if 'mlm_img_filename' in session:
				file_exst = os.path.exists('{}{}'.format(updir,session['mlm_img_filename']))
				if file_exst:
					os.remove(os.path.join(updir, session['mlm_img_filename']))
					session.pop('mlm_img_filename',None)
					session['mlm_img_filename'] = upfilename
					upload_img(files, picture_path)
					if 'mlm_img_path' in session:
						session.pop('mlm_img_path',None)
						session['mlm_img_path'] = 'admin/imgs/product/'+session['mlm_img_filename']
					else:
						session['mlm_img_path'] = 'admin/imgs/product/'+session['mlm_img_filename']
					return url_for('static', filename='admin/imgs/product/'+session['mlm_img_filename'])
				else:
					session.pop('mlm_img_filename',None)
					session['mlm_img_filename'] = upfilename
					upload_img(files, picture_path)
					return url_for('static', filename='admin/imgs/product/'+session['mlm_img_filename'])

			else:
				session['mlm_img_filename'] = upfilename
				upload_img(files, picture_path)
				if 'mlm_img_path' in session:
					session.pop('mlm_img_path',None)
					session['mlm_img_path'] = 'admin/imgs/product/'+session['mlm_img_filename']
				else:
					session['mlm_img_path'] = 'admin/imgs/product/'+session['mlm_img_filename']
				return url_for('static', filename='admin/imgs/product/'+session['mlm_img_filename'])

			

def upload_img(files, picture_path):
	output_size = (600, 600)
	i = Image.open(files)
	i.thumbnail(output_size)
	i.save(picture_path)