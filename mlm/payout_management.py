from flask import Flask, request, session, render_template, redirect, url_for, jsonify, json
import re
from werkzeug.security import generate_password_hash, check_password_hash

from mlm import app

html = 'admin/payout_management/'

@app.route('/payout-management')
def payout_management():
	return render_template(html+'payout-management.html', 
		title = 'Payout Management',
		products = [],
		member_name = 'Je Ar Becerro',
		page = 'Payroll', payout_management = 'open'
		)
	
@app.route('/payout-management/summary')
def payout_summary():
	return render_template(html+'payout-summary.html', 
		title = 'Payout Management',
		member_name = 'Je Ar Becerro',
		page = 'Payout Summary', payout_management = 'open'
		)