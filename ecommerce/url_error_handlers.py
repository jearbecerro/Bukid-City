from ecommerce import utilities as u
from flask import render_template
from ecommerce import app

@app.errorhandler(404)
def page_not_found(e):
	u.set_current_path(['index','/'])
	return render_template('ecommerce/error.html', 
		title = 'Bukid City',
		account = u.login_classifier(),
		cart_count = u.cart()[0], cart = u.cart_classifier(), subtotal = u.cart()[1],
		error_code = '404',
		error_desc = 'Opps! PAGE NOT BE FOUND',
		error_details = 'Sorry but the page you are looking for does not exist, have been removed, name changed or is temporarily unavailable.'
		), 404

@app.errorhandler(405)
def method_not_allowed(e):
	u.set_current_path(['index','/'])
	return render_template('ecommerce/error.html', 
		title = 'Bukid City',
		account = u.login_classifier(),
		cart_count = u.cart()[0], cart = u.cart_classifier(), subtotal = u.cart()[1],
		error_code = '405',
		error_desc = 'Opps! Method not allowed!',
		error_details = "“We need to have a talk on the subject of what'password yours and what'password mine.” ― Stieg Larsson, The Girl with the Dragon Tattoo"
		), 405


@app.route('/shop/pagenotfound')
@app.route('/places/pagenotfound')
def error_handler():
	u.set_current_path(['index','/'])
	return render_template('ecommerce/error.html', 
		title = 'Bukid City',
		account = u.login_classifier(),
		cart_count = u.cart()[0], cart = u.cart_classifier(), subtotal = u.cart()[1],
		error_code = '404',
		error_desc = 'Opps! PAGE NOT BE FOUND',
		error_details = 'Sorry but the page you are looking for does not exist, have been removed, name changed or is temporarily unavailable.'
		), 404
