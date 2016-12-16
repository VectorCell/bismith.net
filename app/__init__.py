#!/usr/bin/env python3

from flask import Flask, render_template, jsonify
import sys
import os

from models import User, Project
import blog
import projects


UPLOAD_DIR = os.path.realpath(__file__)


app = Flask(__name__)


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


@app.route('/upload')
def upload_page():
	return 


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
		receivers = [base64.b64decode('NTEyNTc4ODA5MUB0eHQuYXR0Lm5ldA==').decode('UTF-8')]
		message = 'ZFS error detected'
		smtpObj = smtplib.SMTP('localhost')
		smtpObj.sendmail(sender, receivers, message)
		status = {'success': True, 'message': message, 'sender': sender,
		          'receivers': receivers}
	except Exception as ex:
		status = {'success': False, 'error': str(ex)}
	return jsonify(status)


if __name__ == '__main__':
	app.run(host='10.0.0.3', port=8888)
