#!/usr/bin/env python3

from flask import Flask, render_template, jsonify
import sys

from models import User, Project

import blog
import projects


app = Flask(__name__)


@app.route('/')
@app.route('/index')
@app.route('/home')
def index_page():
	blogentries = blog.parse_blog()
	return render_template('index.html', blogentries=blogentries)


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


@app.route('/<path:path>')
def static_proxy(path):
	if '.' not in path:
		path += '.html'
	return app.send_static_file(path)


@app.route('/api/sendzfsalert')
def send_zfs_alert():

	try:
		import smtplib
		sender = 'brandon@bismith.net'
		receivers = ['5125788091@txt.att.net']
		message = 'this is a test message (test 3)'
		smtpObj = smtplib.SMTP('localhost')
		smtpObj.sendmail(sender, receivers, message)
		status = {'success': True}
	except Exception:
		print("Error: unable to send email")
		status = {'success': False}
	return jsonify(status)


if __name__ == '__main__':
	app.run(host='10.0.0.3', port=8000)
