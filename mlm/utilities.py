from functools import wraps
from flask import session, redirect, render_template, redirect, url_for

def user_classifier():
	if 'user' in session:
		return session['user']
	else:
		return None

def is_admin_login():
	if 'admin_login' in session:
		if session['admin_login'] == True:
			return True
		return False
	else:
		return False

def admin_required(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'admin_login' in session and is_distributor_login() == False:
			if session['admin_login'] == True:
				return f(*args, **kwargs)
			return redirect('/admin/login')
		else:
			return redirect('/admin/login')

	return wrap

def is_distributor_login():
	if 'distributor_login' in session:
		if session['distributor_login'] == True:
			return True
		return False
	else:
		return False

def distributor_required(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'distributor_login' in session:
			if session['distributor_login'] == True:
				return f(*args, **kwargs)
			return redirect('/distributor/login')
		else:
			return redirect('/distributor/login')
	return wrap

def is_member_login():
	if 'member_login' in session:
		if session['member_login'] == True:
			return True
		return False
	else:
		return False

def member_required(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'member_login' in session:
			if session['member_login'] == True:
				return f(*args, **kwargs)
			return redirect('/member/login')
		else:
			return redirect('/member/login')
	return wrap

def error_handlers():
	if is_admin_login() == True:
		return 'admin'
	elif is_distributor_login() == True:
		return 'dist_products'
	elif is_member_login() == True:
		return 'profile'
	else:
		return 'member_login'