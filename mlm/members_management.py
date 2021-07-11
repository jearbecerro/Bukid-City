from flask import Flask, request, session, render_template, redirect, url_for, jsonify, json, send_from_directory
import re, os, secrets, pathlib
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from PIL import Image
from datetime import date, datetime

from bson.objectid import ObjectId
from database import ecommerce_db as db

from mlm import app
mlm_db = db.cluster["mlm"] #MLM database separate into ecommerce database
db_products = mlm_db['products']

with open('./resources/static/ecommerce/js/address-dropdown/provinces.json') as x:
	provinces = json.load(x)

html = 'admin/members_profile/'
#Profile Management
@app.route('/members-profile/add-member')
def add_member():
	#products = db_products.find().sort('price', db.pymongo.ASCENDING)
	member = [
			{
			'date_added':'',
			'profile_picture':'',
			'name': '',
			'gender': '',
			'birthdate': '',
			'contact_number':'',
			'email':'',
			'street':'',
			'region':'',
			'province':'',
			'city':'',
			'brgy':'',
			'username':'',
			'password':'',
			'code':'',
			'product_purchased_ids':'',
			'sponsor_id':'',
			'career':''
			}
		]
	consumer = [
			{
			'date':'',
			'member_id_s':'',
			'sponsor_id':'',
			}
		]
	apprentice = [
			{
			'date':'',
			'member_id':'',
			'sponsor_id':'',
			}
		]
	associate = [
			{
			'date':'',
			'member_id':'',
			'sponsor_id':'',
			}
		]
	supervisor = [
			{
			'date':'',
			'member_id':'',
			'sponsor_id':'',
			}
		]
	manager = [
			{
			'date':'',
			'member_id':'',
			'sponsor_id':'',
			}
		]
	director = [
			{
			'date':'',
			'member_id':'',
			'sponsor_id':'',
			}
		]
	CBP = 0
	'''
	after adding new member
	e check unsa na product ang ge avail para makita if pang marketing plan ba siya or dili
	pag pang marketing plan e formulate ang designated CBP 
	check 
	if new member's sponsor_id is in apprentice collection
		e set ang sales/payout/points ni sponsor 10% commission sa product value + designated cbp
	
	has_upline = True
	while has_upline:
			apprrentice = db...
			associate = db...
			supervisor = db...
			manager = db...
			director = db...
	'''
	return render_template(html+'add-member.html', 
		title = 'Profile Management',
		member_name = 'Je Ar Becerro',
		page = 'Add Member', profile_management = 'open', add_member = 'active',
		provinces = provinces)#, products = products)

@app.route('/members-profile/members-list')
def member_list():
	products = db.fapc('5f0e434c4858e5ca8ee00563')
	return render_template(html+'members-list.html', 
		products = products,
		title = 'Profile Management',
		member_name = 'Je Ar Becerro',
		page = 'Members List', profile_management = 'open', members_list = 'active'
		)