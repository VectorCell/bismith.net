#!/usr/bin/env python3

import sys
import os
import time
import datetime
import json

from flask import Flask, render_template, jsonify, request, redirect, url_for, abort
from werkzeug.utils import secure_filename

from models import User, Project
import blog
import projects
import dashboard
import landing

import secrets


ALLOW_FILE_DELETION = True


GLOBAL_CACHE = {}


app = Flask(__name__)


UPLOAD_DIR = os.path.realpath(__file__)[:-len('__init__.py')] + 'static/uploads'
app.config['UPLOAD_DIR'] = UPLOAD_DIR
app.config['MAX_CONTENT_LENGTH'] = 64 * 1024 * 1024 # 64 MiB


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


@app.route('/landing')
def landing_page():
	dir_path = os.path.dirname(os.path.realpath(__file__))
	with open(dir_path + '/data/landing.json', encoding='utf-8') as file:
		data = json.load(file)
	print(data)
	return render_template('landing.html', data=data, text=json.dumps(data, indent=4))


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


@app.route('/wildsurge')
def wildsurge():
	if 'surgelist' not in GLOBAL_CACHE:
		dir_path = os.path.dirname(os.path.realpath(__file__))
		surgelist = []
		surgenum = 0
		with open(dir_path + "/data/wildsurges.txt", encoding="utf-8") as file:
			for line in file:
				line = line.strip()
				tokens = line.split(" ")
				num = tokens[0][-4:]
				text = " ".join(tokens[1:])
				surgelist.append(
					{
						'num': num,
						'text': text,
					})
				print("{:04} :: added {} -> {}".format(surgenum, surgelist[-1]['num'], surgelist[-1]['text']))
				surgenum += 1
		GLOBAL_CACHE['surgelist'] = surgelist
	if request.args.get('num'):
		num = request.args.get('num')
		if num == "all":
			surgelist = GLOBAL_CACHE['surgelist']
			return render_template('wildsurge.html', surgelist=surgelist)
		else:
			digits = "0123456789"
			num = "".join(c for c in num if c in digits)
			while len(num) < 4:
				num = "0" + num
			if int(num) < 0 or int(num) > 9999:
				return render_template('wildsurge.html', invalidnum=True)
			else:
				return render_template('wildsurge.html', surgenum=num, surgetext=GLOBAL_CACHE['surgelist'][int(num)]['text'])
	else:
		return render_template('wildsurge.html')
		# return render_template('wildsurge.html', surgelist=GLOBAL_CACHE['surgelist'])


@app.route('/<path:path>')
def static_proxy(path):
	if '.' not in path:
		path += '.html'
	return app.send_static_file(path)


@app.route('/api/ip')
def get_ip_addr():
	data = {}
	data['ip_addr'] = request.environ['REMOTE_ADDR']
	return jsonify(data)


@app.route('/api/alert')
def send_alert():
	def get_file_contents(filename):
		with open(filename, 'r') as f:
			return f.read().strip()
	try:
		# https://pushover.net/api
		app_token = secrets.get_secret("pushover_app_token_alerts")
		user_key = secrets.get_secret("pushover_user_key")

		if request.args.get('message'):
			message = request.args.get('message')
		elif request.args.get('msg'):
			message = request.args.get('msg')
		else:
			message = "[no message supplied]"
			return jsonify({'success': False, 'error': message})

		import http.client, urllib
		conn = http.client.HTTPSConnection("api.pushover.net:443")
		conn.request("POST", "/1/messages.json",
		  urllib.parse.urlencode({
		    "token": app_token,
		    "user": user_key,
		    "message": message,
		    "title": "Alerts API (bismith.net/api/alert)"
		  }), { "Content-type": "application/x-www-form-urlencoded" })
		response = conn.getresponse().read().decode('utf-8')
		status = {'success': True, 'response': response}
	except Exception as ex:
		status = {'success': False, 'error': str(ex)}
	return jsonify(status)


@app.route('/api/arrival')
def arrival():
	valid_hostname_chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.-_'
	hostname_raw = request.args.get('hostname')
	try:
		hostname = ''.join(c for c in hostname_raw if c in valid_hostname_chars)
		message = '{} arrived'.format(hostname)
		import base64
		import smtplib
		sender = base64.b64decode('QVJSSVZBTC5BTEVSVEBiaXNtaXRoLm5ldA==').decode('UTF-8')
		recipient = base64.b64decode('NTEyNTc4ODA5MUB0eHQuYXR0Lm5ldA==').decode('UTF-8')
		smtpObj = smtplib.SMTP('localhost')
		smtpObj.sendmail(sender, [recipient], message)
		status = {'success': True, 'message': message, 'sender': sender,
		          'recipients': recipient}
	except Exception as ex:
		status = {'success': False, 'error': str(ex)}
	return jsonify(status)


if __name__ == '__main__':
	app.run(host='172.16.0.3', port=8888)
