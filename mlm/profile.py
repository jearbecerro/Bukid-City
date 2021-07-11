from flask import Flask, request, session, render_template, redirect, url_for, jsonify, json
import re, os, secrets, pathlib
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from PIL import Image
from mlm import utilities as u

from mlm import app

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

basedir = os.path.abspath(os.path.dirname(__file__))

app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.route('/uploadajax', methods=['POST'])
def upldfile():
    if request.method == 'POST':
        files = request.files['filename']
        if files and allowed_file(files.filename):
            filename = secure_filename(files.filename)

            random_hex = secrets.token_hex(8)
            _, f_ext = os.path.splitext(filename)
            upfilename = random_hex + f_ext

            updir = os.path.join(basedir, '../resources/static/upload')

            pathlib.Path(updir).mkdir(exist_ok=True)

            picture_path = os.path.join(updir, upfilename)

            output_size = (150, 150)
            i = Image.open(files)
            i.thumbnail(output_size)
            i.save(picture_path)

            return jsonify(name=filename, profilePicture = 'static/upload/'+upfilename)
        else:
        	return jsonify(notAllowed = 'True')

#Personal Profile
@app.route('/profile')
def profile():
	with open('./resources/static/ecommerce/js/address-dropdown/provinces.json') as x:
		provinces = json.load(x)
	return render_template('admin/profile.html', 
		title = 'Profile', page = 'Je Ar Becerro', profile = 'active',
		member_name = 'Je Ar Becerro', career = 'Apprentice',
		direct_sales = '10', indirect_sales = '30',
		entry_date = 'August 30, 2020', sponsor = 'Randy G. Clores', package_purchased = 'Kabuhayan Basket 2899',
		address = 'Butuan City', phone = '09101064727',
		gender = 'Male', birthdate = '1996-11-19', email = 'jearbecerro@gmail.com', 
		provinces = provinces,
		street = 'p17', users_province = 'AGUSAN DEL NORTE', users_citymun = 'Butuan City', users_barangay = 'Mahay'
		)

