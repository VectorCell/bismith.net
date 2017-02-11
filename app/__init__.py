#!/usr/bin/env python3

import sys
import os
import time
import datetime

from flask import Flask, render_template, jsonify, request, redirect, url_for, abort
from werkzeug.utils import secure_filename

from models import User, Project
import blog
import projects
import dashboard


ALLOW_FILE_DELETION = False


app = Flask(__name__)


UPLOAD_DIR = os.path.realpath(__file__)[:-len('__init__.py')] + 'static/uploads'
app.config['UPLOAD_DIR'] = UPLOAD_DIR
app.config['MAX_CONTENT_LENGTH'] = 64 * 1024 * 1024


@app.route('/')
@app.route('/index')
@app.route('/home')
def index_page():
	blogentries = blog.parse_blog()
	githubactions = list(projects.get_github_actions())
	return render_template('index.html',
	                       blogentries=blogentries,
	                       githubactions=githubactions)


@app.route('/projects')
def projects_page():
	project_names = ('aes-rijndael',
	                 'output-sparse',
	                 'physmem',
	                 'power-relays',
	                 'sumpass')
	allprojects = Project.query.all()
	githubactions = list(projects.get_github_actions())
	del githubactions[8:]
	return render_template('projects.html',
	                       projects=allprojects,
	                       githubactions=githubactions)


@app.route('/blog')
def blog_page():
	blogentries = blog.parse_blog()
	return render_template('blog.html', blogentries=blogentries)


@app.route('/resume')
def resume_page():
	return render_template('resume.html')


@app.route('/about')
def about_page():
	return render_template('about.html')


@app.route('/dashboard')
def dashboard_page():
	if request.args.get('source') == 'owm':
		return render_template('dashboard.html',
		                       source = 'OpenWeatherMap',
		                       weather = dashboard.get_owm())
	else:
		layout = request.args.get('layout')
		if not layout:
			layout = 'today_top'
		return render_template('dashboard.html',
		                       source = 'NOAA',
		                       weather = dashboard.get_noaa(),
		                       layout = layout)


@app.route('/upload', methods=('GET', 'POST'))
def upload_page():
	if request.method == 'POST':
		if 'file' not in request.files:
			return 'File not specified'
			#return redirect(request.url)
		file = request.files['file']
		if not file.filename:
			return 'File not specified'
			#return redirect(request.url)
		if file:
			filename = secure_filename(file.filename)
			if not os.path.isfile(os.path.join(app.config['UPLOAD_DIR'], filename)):
				file.save(os.path.join(app.config['UPLOAD_DIR'], filename))
				return 'file upload complete'
			else:
				return 'a file of that name already exists'
		else:
			return 'file cannot be uploaded: ' + str(file)
	listdir = os.listdir(app.config['UPLOAD_DIR'])
	listdir.sort()
	filelist = []
	for file in listdir:
		if file != 'metadata.json':
			path = os.path.join(app.config['UPLOAD_DIR'], file)
			size = os.path.getsize(path)
			d = {
				'name': file,
				'size': size,
				'size_readable': size,
				'mtime': os.path.getmtime(path),
				'mtime_readable': datetime.datetime.fromtimestamp(os.path.getmtime(path)).strftime('%Y-%m-%d %H:%M:%S UTC'),
				'allow_delete': ALLOW_FILE_DELETION
			}
			filelist.append(d)
	return render_template('upload.html',
	                       upload_dir=app.config['UPLOAD_DIR'],
	                       filelist=filelist)


@app.route('/uploaded')
def uploaded_file():
	filename = secure_filename(request.args.get('file'))
	if '/' in filename:
		abort(400)
	if request.args.get('delete') == 'yes' and ALLOW_FILE_DELETION:
		os.remove(app.config['UPLOAD_DIR'] + '/' + filename)
		return redirect(url_for('upload_page'))
	else:
		return redirect('/uploads/' + filename)


@app.route('/<path:path>')
def static_proxy(path):
	if '.' not in path:
		path += '.html'
	return app.send_static_file(path)


@app.route('/api/sendzfsalert')
def send_zfs_alert():
	try:
		import base64
		import smtplib
		sender = base64.b64decode('WkZTLkFMRVJUQGJpc21pdGgubmV0').decode('UTF-8')
		receiver = base64.b64decode('NTEyNTc4ODA5MUB0eHQuYXR0Lm5ldA==').decode('UTF-8')
		message = 'ZFS error detected'
		smtpObj = smtplib.SMTP('localhost')
		smtpObj.sendmail(sender, [receivers], message)
		status = {'success': True, 'message': message, 'sender': sender,
		          'receivers': receivers}
	except Exception as ex:
		status = {'success': False, 'error': str(ex)}
	return jsonify(status)


@app.route('/api/arrival')
def arrival():
	valid_hostname_chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.'
	hostname = ''.join(c for c in request.args.get('hostname') if c in valid_hostname_chars)
	message = '{} arrived'.format(hostname)
	try:
		import base64
		import smtplib
		sender = base64.b64decode('WkZTLkFMRVJUQGJpc21pdGgubmV0').decode('UTF-8')
		receiver = base64.b64decode('NTEyNTc4ODA5MUB0eHQuYXR0Lm5ldA==').decode('UTF-8')
		smtpObj = smtplib.SMTP('localhost')
		smtpObj.sendmail(sender, [receivers], message)
		status = {'success': True, 'message': message, 'sender': sender,
		          'receivers': receivers}
	except Exception as ex:
		status = {'success': False, 'error': str(ex)}
	return jsonify(status)


if __name__ == '__main__':
	app.run(host='10.0.0.3', port=8888)
