#!/usr/bin/env python3

import sys
import os

from flask import Flask, render_template, jsonify, request, redirect, url_for, abort
from werkzeug.utils import secure_filename

from models import User, Project
import blog
import projects


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


@app.route('/upload', methods=('GET', 'POST'))
def upload_page():
	if request.method == 'POST':
		if 'file' not in request.files:
			return redirect(request.url)
		file = request.files['file']
		if not file.filename:
			return redirect(request.url)
		if file:
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_DIR'], filename))
			return 'file upload complete, reloading ...'
	listdir = os.listdir(app.config['UPLOAD_DIR'])
	filelist = []
	for file in listdir:
		def human_readable_size(numbytes):
			return numbytes
		size = os.path.getsize('/'.join((app.config['UPLOAD_DIR'], file)))
		d = {
			'name': file,
			'size': size,
			'readable_size': human_readable_size(size)
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
	if request.args.get('delete') == 'yes':
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


if __name__ == '__main__':
	app.run(host='10.0.0.3', port=8888)
