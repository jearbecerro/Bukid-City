from flask import request, session, render_template, redirect, url_for, jsonify, json
import re, os, secrets, pathlib
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from PIL import Image
from datetime import date, datetime

from bson.objectid import ObjectId
import bson
from database import ecommerce_db as db
from mlm import utilities as u

from pprint import pprint
from mlm import app

html = 'admin/distributor_profile/'
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg'])

def allowed_file(filename):
	return '.' in filename and \
		   filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.route('/add-distributor')
@u.admin_required
def add_distributor():
	with open('./resources/static/ecommerce/js/address-dropdown/provinces.json') as x:
		provinces = json.load(x)
	if 'dist_img_path' in session:
		path = session['dist_img_path']
	else:
		path = 'ecommerce/img/distributor/add_distributor.png'
	return render_template(html+'add-distributor.html', 
		title = 'Distributor Profile',
		member_name = 'Je Ar Becerro', main_page = '/add-distributor',
		page = 'Add Distributor', distributor = 'open', add_distributor = 'active',
		default_img = path, provinces = provinces, 
		is_admin_login = u.is_admin_login(), is_member_login = u.is_member_login(), is_distributor_login = u.is_distributor_login()
		)
@app.route('/distributor')
@app.route('/distributor-list')
@u.admin_required
def distributor_list():
	distributors = db.distributors.find()
	
	return render_template(html+'distributor-list.html', 
		title = 'Distributor',
		member_name = 'Je Ar Becerro', main_page = '/distributor-list',
		page = 'Distributor List', distributor = 'open', distributor_list = 'active',
		distributors = distributors, default_img = 'ecommerce/img/distributor/add_distributor.png', 
		is_admin_login = u.is_admin_login(), is_member_login = u.is_member_login(), is_distributor_login = u.is_distributor_login()
		)

@app.route('/view_sales_by_date')
def view_sales_by_date():
	try:
		start = request.args.get('start', 0, type=str)
		end = request.args.get('end', 0, type=str)
		result = []
		orders_id = []

		startdate = datetime.strptime(start,'%Y-%m-%d')
		enddate = datetime.strptime(end,'%Y-%m-%d')
		db_result = db.sales.find({'distributor_id': session['dist_id'] ,'date': {'$gte':startdate,'$lt':enddate }})
		if db_result:
			for x in db_result:
				result.append({ '_id': str(x['_id']), 'date': x['date'],'date_view': x['date_view'], 'distributor_id': x['distributor_id'], 'total_sales':x['total_sales'], 'total_orders': x['total_orders'], 'orders': x['orders'], })
			if 'datetime_sales_result' in session:
				session.pop('datetime_sales_result',None)
				session['datetime_sales_result'] = result
				return jsonify(ok = 'ok')
			else:
				session['datetime_sales_result'] = result
				return jsonify(ok = 'ok')
		session.pop('datetime_sales_result',None)		
		return jsonify(ok = 'ok')
	except TypeError:
		return redirect(url_for(u.error_handlers()))


@app.route('/redirect_dist')
def redirect_dist():
	try:
		dist_id = request.args.get('dist_id', 0, type=str)
		dist = db.distributors.find_one({ '_id': ObjectId(str(dist_id)) } , {'_id': 1})
		if dist:
			if 'dist_id' in session:
				session.pop('dist_id',None)
				session['dist_id'] = dist_id
			else:
				session['dist_id'] = dist_id
			return jsonify(redirect = 'OK')
	except bson.errors.InvalidId:
		return redirect(url_for(u.error_handlers()))
	else:
		return redirect(url_for(u.error_handlers()))

@app.route('/redirect_sales_selected')
def redirect_dist_sales():
	try:
		order_id = request.args.get('order_id', 0, type=str)
		if 'dist_id' in session:
			if 'order_id_single_view' in session:
				session.pop('order_id_single_view', None)
				session['order_id_single_view'] = order_id
				return jsonify(redirect = 'OK')
			else:
				session['order_id_single_view'] = order_id
				return jsonify(redirect = 'OK')
		else:
			return redirect(url_for(u.error_handlers()))
	except Exception as e:
		return redirect(url_for(u.error_handlers()))
	
	
	

@app.route('/distributor/view/sales')
def view_sales():
	if 'order_id_single_view' in session:
		delivered_orders = db.orders.find_one({ '_id': ObjectId(str(session['order_id_single_view'])) })
		if delivered_orders:
			return  render_template(html+'view-distributor-sales.html', 
				title = 'Distributor Profile',
				member_name = 'Je Ar Becerro', main_page = '/distributor/view-edit-delete', page = 'Distributor Sales', 
				order = delivered_orders, 
				is_admin_login = u.is_admin_login(), is_member_login = u.is_member_login(), is_distributor_login = u.is_distributor_login()
			)
		else:
			return redirect(url_for('view_dist'))
	else:
		return redirect(url_for('view_dist'))

@app.route('/distributor/profile')
@app.route('/distributor/view-edit-delete')
def view_dist():	
	if 'dist_id' in session:
		with open('./resources/static/ecommerce/js/address-dropdown/provinces.json') as x:
			provinces = json.load(x)
		global total_sales, total_orders, total_products
		total_sales = 0
		total_orders = 0
		total_products = 0
		#compute all total orders of the distributor
		t_o = db.sales.aggregate([ { '$match': { 'distributor_id': session['dist_id'] } },{ '$group': { '_id': None, "TotalOrders": { '$sum': '$total_orders' }}} ] )
		for x in t_o:
			total_orders = x['TotalOrders']
		#compute all total sales of the distributor
		t_s = db.sales.aggregate([ { '$match': { 'distributor_id': session['dist_id'] } },{ '$group': { '_id': None, "TotalSales": { '$sum': '$total_sales' }}} ] ) 
		for x in t_s:
			total_sales = x['TotalSales']
		total_products = db.products.find({'distributor_id': session['dist_id']}).count()#find all total sales
		
		sales_list = []
		if 'datetime_sales_result' in session:
			sales_list = session['datetime_sales_result']
			session.pop('datetime_sales_result',None)
		else:
			sales_list = db.sales.find({ 'distributor_id': session['dist_id'] })
			'''
			for x in s:
				d = db.distributors.find_one({ '_id': ObjectId(str(x['distributor_id'])) })
				if d:
					dist = "{}, {}, {}, {}".format(d['branch_name'],d['brgy'],d['city'],d['province'])
				else:
					d = db.distributors.find_one({ '_id': ObjectId(str(session['dist_id'])) })
					dist = "{}, {}, {}, {}".format(d['branch_name'],d['brgy'],d['city'],d['province'])
				#dre dapit naay error
				sales_list.append({ 'orders':x['orders'],'total_orders': x['total_orders'], 'total_sales':x['total_sales'] ,'distributor': dist,'date_view': x['date_view'] })
			'''
		products = db.products.find({ 'distributor_id': str(session['dist_id']) })
		distributor = db.distributors.find_one({ '_id': ObjectId(str(session['dist_id'])) })
		policies = distributor['policies']
		policies_lst = []
		for pol in policies:
			policies_lst.append('"{}"{}'.format(pol['title'],pol['desc']))

		policies_str = str(policies_lst).replace("',", "\n").replace("[","").replace("]","").replace("'","")
		return  render_template(html+'view-distributor.html', 
			title = 'Distributor Profile',
			member_name = 'Je Ar Becerro', main_page = '/add-distributor',
			policies = policies_str, page = 'Distributor Profile', 
			total_sales = total_sales, total_orders = total_orders, total_products = total_products,
			products = products, sales = sales_list,
			distributor = distributor, provinces = provinces, 
			is_admin_login = u.is_admin_login(), is_member_login = u.is_member_login(), is_distributor_login = u.is_distributor_login()
			)
	else:
		return redirect(url_for(u.error_handlers()))

@app.route('/add_dist')
def add_dist():
	try:
		branch_name = request.args.get('branch_name', 0, type=str)
		about = request.args.get('about', 0, type=str)
		fb_url = request.args.get('fb_url', 0, type=str)
		bldg = request.args.get('bldg', 0, type=str)
		prov = request.args.get('province', 0, type=str)
		citymun = request.args.get('citymun', 0, type=str)
		barangay = request.args.get('barangay', 0, type=str)
		policies = request.args.get('policies', 0, type=str)
		default_img = request.args.get('default_img', 0, type=str)
		business_partner = request.args.get('business_partner', 0, type=str)

		with open('./resources/static/ecommerce/js/address-dropdown/regions.json') as r:
			regions = json.load(r)
		with open('./resources/static/ecommerce/js/address-dropdown/provinces.json') as p:
			provinces = json.load(p)
		with open('./resources/static/ecommerce/js/address-dropdown/citymun.json') as c:
			citymuns = json.load(c)
		with open('./resources/static/ecommerce/js/address-dropdown/barangay.json') as b:
			barangays = json.load(b)
		errors = []
		dict_of_policies = []
		title_classifier = 0
		allowed_fb_url = ["https://web.facebook.com/", "https://www.facebook.com/", "https://mobile.facebook.com/", "https://free.facebook.com/"]
		global dist_fb_page
		dist_fb_page = ''
		if 'dist_img_filename' not in session:
			if default_img == '':
				errors.append("<br>&nbspPlease upload a product image")

		if len(branch_name) == 0:
			errors.append('<br>&nbspBranch Name field is empty')
		branch_exist = db.distributors.find({ 'branch_name': branch_name }, {'_id': 1})
		if branch_exist:
			errors.append('<br>&nbspBranch Name already exists. Please enter a different name.')
		if len(about) == 0:
			errors.append('<br>&nbspAbout field is empty')
		if len(fb_url) == 0:
			errors.append('<br>&nbspFacebook URL field is empty')
		else:
			for pattern in allowed_fb_url:
				x = re.findall(pattern, fb_url)
				if x:
					i = str(x).replace("[","").replace("]","").replace("'","")
					dist_fb_page = fb_url.replace(i,"")
					if dist_fb_page == "":
						errors.append('<br>&nbspInvalid Facebook URL')
						break

		if len(bldg) == 0:
			errors.append('<br>&nbspStreet field is empty')
		if len(policies) == 0:
			errors.append("<br>&nbspPolicies textarea is empty")
		else:
			list_of_policies = policies.splitlines()
			for lst in list_of_policies:
				t = re.findall(r'"([^"]*)"', lst)
				title_classifier = len(t) 
				pol_titles = str(t).replace('""', "").replace("[", "").replace("]", "").replace("'", "")
				desc = lst.replace(pol_titles,"").replace("[", "").replace("]", "").replace("',", "\n").replace("'", "").replace("", "")
				dict_of_policies.append({ 'title': pol_titles, 'desc': desc.replace('""', "") })
		
		if title_classifier == 0:
			errors.append("<br>&nbspPlease add title to the policies!")
		if prov== 'None' or prov == '':
			errors.append('<br>&nbspPlease select a Province')
		if citymun== 'None' or citymun == '':
			errors.append('<br>&nbspPlease select a City/Muncipality')
		if barangay == 'None' or barangay == '':
			errors.append('<br>&nbspPlease select a barangay')
		if len(business_partner) == 0:
			errors.append('<br>&nbspBusiness Partner field is empty')

		if len(errors) == 0:
			image = ''
			if default_img != '':
				image = default_img
			if default_img == '' and 'dist_img_filename' in session:
				image = session['dist_img_filename']
			regDesc = ''
			provDesc = ''
			citymunDesc = ''
			brgyDesc = ''
			for province in provinces:
				if province['provCode'] == prov:
					regCode = province["regCode"]
					provDesc = province['provDesc']
			for region in regions:
				if region['regCode'] == regCode:
					regDesc = region['regDesc']
			for city in citymuns:
				if city['citymunCode'] == citymun:
					citymunDesc = city['citymunDesc']
			for brgy in barangays:
				if brgy['brgyCode'] == barangay:
					brgyDesc = brgy['brgyDesc']

			distributor = {
				"date_entry": datetime.now().strftime('%B %d, %Y @ %I:%M:%S %p'),
				"banner_image": image,
				"branch_name": branch_name,
				"about": about,
				"region": regDesc,
				"province": provDesc,
				"city": citymunDesc,
				"brgy": brgyDesc,
				"bldg": bldg,
				"facebook_page": dist_fb_page,
				"policies": dict_of_policies,
				"business_partner": business_partner,
				"status":"active"
			}
			db.distributors.insert_one(distributor)
			session.pop('dist_img_filename',None)
			session.pop('dist_img_path',None)
			img = url_for('static', filename='ecommerce/img/distributor/add_distributor.png')
			return jsonify(success = 'Product Added', img = img)

		return jsonify(errors = errors)
	except TypeError:
		return redirect(url_for(u.error_handlers()))
	

@app.route('/update_dist')
def update_dist():
	try:
		branch_name = request.args.get('branch_name', 0, type=str)
		about = request.args.get('about', 0, type=str)
		fb_url = request.args.get('fb_url', 0, type=str)
		bldg = request.args.get('bldg', 0, type=str)
		prov = request.args.get('province', 0, type=str)
		citymun = request.args.get('citymun', 0, type=str)
		barangay = request.args.get('barangay', 0, type=str)
		policies = request.args.get('policies', 0, type=str)
		default_img = request.args.get('default_img', 0, type=str)	
		business_partner = request.args.get('business_partner', 0, type=str)

		with open('./resources/static/ecommerce/js/address-dropdown/regions.json') as r:
			regions = json.load(r)
		with open('./resources/static/ecommerce/js/address-dropdown/provinces.json') as p:
			provinces = json.load(p)
		with open('./resources/static/ecommerce/js/address-dropdown/citymun.json') as c:
			citymuns = json.load(c)
		with open('./resources/static/ecommerce/js/address-dropdown/barangay.json') as b:
			barangays = json.load(b)
		errors = []
		dict_of_policies = []
		title_classifier = 0
		allowed_fb_url = ["https://www.facebook.com/", "https://web.facebook.com/", "https://mobile.facebook.com/", "https://free.facebook.com/"]
		global dist_fb_page
		dist_fb_page = ''

		if len(branch_name) == 0:
			errors.append('<br>&nbspBranch Name field is empty')
		branch_exist = db.distributors.find({ 'branch_name': branch_name })#, {'_id': 1}
		if branch_exist:
			b_ids = []
			for x in branch_exist:
				b_ids.append(x['_id'])
			for ids in b_ids:
				x = re.findall(str(ids), session['dist_id'])
				if x:
					if x[0] != session['dist_id']:
						errors.append('<br>&nbspBranch Name already exists. Please enter another branch name.')

		if len(about) == 0:
			errors.append('<br>&nbspAbout field is empty')
		if len(fb_url) == 0:
			errors.append('<br>&nbspFacebook URL field is empty')
		else:
			for pattern in allowed_fb_url:
				x = re.findall(pattern, fb_url)
				if x:
					i = str(x).replace("[","").replace("]","").replace("'","")
					dist_fb_page = fb_url.replace(i,"")
					if dist_fb_page == "":
						errors.append('<br>&nbspInvalid Facebook URL')
						break
		if len(bldg) == 0:
			errors.append('<br>&nbspStreet field is empty')
		if len(policies) == 0:
			errors.append("<br>&nbspPolicies textarea is empty")
		else:
			list_of_policies = policies.splitlines()
			for lst in list_of_policies:
				t = re.findall(r'"([^"]*)"', lst)
				title_classifier = len(t) 
				pol_titles = str(t).replace('""', "").replace("[", "").replace("]", "").replace("'", "")
				desc = lst.replace(pol_titles,"").replace("[", "").replace("]", "").replace("',", "\n").replace("'", "").replace("", "")
				dict_of_policies.append({ 'title': pol_titles, 'desc': desc.replace('""', "") })
		
		if title_classifier == 0:
			errors.append("<br>&nbspPlease add title to the policies!")
		if prov== 'None' or prov == '':
			errors.append('<br>&nbspPlease select a Province')
		if citymun== 'None' or citymun == '':
			errors.append('<br>&nbspPlease select a City/Muncipality')
		if barangay == 'None' or barangay == '':
			errors.append('<br>&nbspPlease select a barangay')
		if len(business_partner) == 0:
			errors.append('<br>&nbspBusiness Partner field is empty')

		if len(errors) == 0:
			image = 'test'
			if default_img != '':
				image = default_img
				updir = os.path.join(basedir, '../resources/static/ecommerce/img/distributor/')
				if 'dist_img_filename' in session:
					os.remove(os.path.join(updir, session['dist_img_filename']))
					session.pop('dist_img_filename',None)

				if 'dist_img_filename' not in session:
					x = db.distributors.find_one({ '_id': ObjectId(str(session['dist_id'])) }, { 'banner_image': 1 })
					if x['banner_image'] != default_img:
						os.remove(os.path.join(updir, x['banner_image']))

				db.distributors.update_one({ '_id': ObjectId(str(session['dist_id']))},{"$set": { 'banner_image': image } })
			if default_img == '' and 'dist_img_filename' in session:
				image = session['dist_img_filename']
				if 'dist_img_filename' in session:
					db.distributors.update_one({ '_id': ObjectId(str(session['dist_id']))},{"$set": { 'banner_image': image } })

			image = ''
			regDesc = ''
			provDesc = ''
			citymunDesc = ''
			brgyDesc = ''
			for province in provinces:
				if province['provCode'] == prov:
					regCode = province["regCode"]
					provDesc = province['provDesc']
			for region in regions:
				if region['regCode'] == regCode:
					regDesc = region['regDesc']
			for city in citymuns:
				if city['citymunCode'] == citymun:
					citymunDesc = city['citymunDesc']
			for brgy in barangays:
				if brgy['brgyCode'] == barangay:
					brgyDesc = brgy['brgyDesc']
			d = db.distributors.find_one({ '_id': ObjectId(str(session['dist_id']))})

			if d['city'] == citymun:
				citymunDesc = citymun
			if d['brgy'] == barangay:
				brgyDesc = barangay

			distributor = {
				"date_entry": datetime.now().strftime('%B %d, %Y @ %I:%M:%S %p'),
				"branch_name": branch_name,
				"about": about,
				"region": regDesc,
				"province": provDesc,
				"city": citymunDesc,
				"brgy": brgyDesc,
				"bldg": bldg,
				"facebook_page": dist_fb_page,
				"policies": dict_of_policies,
				"business_partner": business_partner,
				"status":"active"
			}
			db.distributors.update_one({ '_id': ObjectId(str(session['dist_id']))},{"$set": distributor })
			session.pop('dist_img_filename',None)
			session.pop('dist_img_path',None)
			img = url_for('static', filename='ecommerce/img/distributor/add_distributor.png')
			return jsonify(success = 'Product Added', img = img)

		return jsonify(errors = errors)
	except TypeError:
		return redirect(url_for(u.error_handlers()))
	

@app.route('/up_dist_product_img', methods=['POST'])
def up_dist_product_img():
	if request.method == 'POST':
		files = request.files['fileimage']
		dist = db.distributors.find_one({ '_id' :  ObjectId(str(session['dist_id']))}, {'banner_image': 1})
		updir = os.path.join(basedir, '../resources/static/ecommerce/img/distributor/')

		file_exist = os.path.exists('{}{}'.format(updir, dist['banner_image']))

		if file_exist:
			if dist['banner_image'] != 'default.jpg':
				os.remove(os.path.join(updir, dist['banner_image']))

		if allowed_file(files.filename) == False:
			return jsonify(error = 'true')
		if allowed_file(files.filename) == True:
			return jsonify(img_path = upload_classifier(files, 'Upd'), allowed = 'true')

@app.route('/add_dist_product_img', methods=['POST'])
def add_dist_product_img():
	if request.method == 'POST':
		files = request.files['fileimage']
		if allowed_file(files.filename) == False:
			return jsonify(error = 'true')
		if allowed_file(files.filename) == True:
			return jsonify(img_path = upload_classifier(files, 'Add'), allowed = 'true')

def upload_classifier(files, func):
	if files and allowed_file(files.filename):
		filename = secure_filename(files.filename)
		random_hex = secrets.token_hex(8)
		_, f_ext = os.path.splitext(filename)
		upfilename = random_hex + f_ext
		updir = os.path.join(basedir, '../resources/static/ecommerce/img/distributor/')
		pathlib.Path(updir).mkdir(exist_ok=True)
		picture_path = os.path.join(updir, upfilename)
		
		if func == 'Add':
			if 'dist_img_filename' in session:
				file_exst = os.path.exists('{}{}'.format(updir,session['dist_img_filename']))
				if file_exst:
					os.remove(os.path.join(updir, session['dist_img_filename']))
					session.pop('dist_img_filename',None)
					session['dist_img_filename'] = upfilename
					upload_img(files, picture_path)
					if 'dist_img_path' in session:
						session.pop('dist_img_path',None)
						session['dist_img_path'] = 'ecommerce/img/distributor/'+session['dist_img_filename']
					else:
						session['dist_img_path'] = 'ecommerce/img/distributor/'+session['dist_img_filename']
					return url_for('static', filename='ecommerce/img/distributor/'+session['dist_img_filename'])
				else:
					session.pop('dist_img_filename',None)
					session['dist_img_filename'] = upfilename
					upload_img(files, picture_path)
					return url_for('static', filename='ecommerce/img/distributor/'+session['dist_img_filename'])
			else:
				session['dist_img_filename'] = upfilename
				upload_img(files, picture_path)
				if 'dist_img_path' in session:
					session.pop('dist_img_path',None)
					session['dist_img_path'] = 'ecommerce/img/distributor/'+session['dist_img_filename']
				else:
					session['dist_img_path'] = 'ecommerce/img/distributor/'+session['dist_img_filename']

				return url_for('static', filename='ecommerce/img/distributor/'+session['dist_img_filename'])

		if func == 'Upd':
			if 'dist_img_filename' in session:
				file_exst = os.path.exists('{}{}'.format(updir,session['dist_img_filename']))
				if file_exst:
					os.remove(os.path.join(updir, session['dist_img_filename']))
					session.pop('dist_img_filename',None)
					session['dist_img_filename'] = upfilename
					upload_img(files, picture_path)
					if 'dist_img_path' in session:
						session.pop('dist_img_path',None)
						session['dist_img_path'] = 'ecommerce/img/distributor/'+session['dist_img_filename']
					else:
						session['dist_img_path'] = 'ecommerce/img/distributor/'+session['dist_img_filename']

					return url_for('static', filename='ecommerce/img/distributor/'+session['dist_img_filename'])
				else:
					session.pop('dist_img_filename',None)
					session['dist_img_filename'] = upfilename
					upload_img(files, picture_path)
					return url_for('static', filename='ecommerce/img/distributor/'+session['dist_img_filename'])

			else:
				session['dist_img_filename'] = upfilename
				upload_img(files, picture_path)
				if 'dist_img_path' in session:
					session.pop('dist_img_path',None)
					session['dist_img_path'] = 'ecommerce/img/distributor/'+session['dist_img_filename']
				else:
					session['dist_img_path'] = 'ecommerce/img/distributor/'+session['dist_img_filename']
					
				return url_for('static', filename='ecommerce/img/distributor/'+session['dist_img_filename'])
			

def upload_img(files, picture_path):
	output_size = (600, 600)
	i = Image.open(files)
	i.thumbnail(output_size)
	i.save(picture_path)