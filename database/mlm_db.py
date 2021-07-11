import pymongo
from pymongo import MongoClient
from pprint import pprint
from bson.objectid import ObjectId
from flask import session
from werkzeug.security import generate_password_hash, check_password_hash

cluster = MongoClient("mongodb://localhost:27017/")
#cluster = MongoClient("mongodb+srv://bukidcity:bukidcity@cluster0.er1qn.mongodb.net/bctest?retryWrites=true&w=majority")
#db = cluster["mlm"]
db = cluster['bctest2']
mlm_users = db['mlm_users'] #add mlm_user collection on mongodb "ATLAS"

insert_users = [
	{
		'username': 'memberuser',
		'password': generate_password_hash('123', method='sha256'),
		'designation': 'Member'
	},
	{
		'username': 'distuser',
		'password': generate_password_hash('123', method='sha256'),
		'designation': 'Distributor'
	},
	{
		'username': 'adminuser',
		'password': generate_password_hash('123', method='sha256'),
		'designation': 'Admin'
	}
	]

def insert_users():
	pass
	#mlm_users.insert_one(test)
#mlm_users.update_many({},{"$set": { 'name': 'Je Ar Becerro' }})