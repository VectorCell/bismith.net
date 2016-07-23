#!/usr/bin/env python3

from flask import Flask, render_template, jsonify
import sys

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
	#githubactions = projects.get_github_actions()
	#project_names = ('aes-rijndael',
	#                 'output-sparse',
	#                 'physmem',
	#                 'power-relays',
	#                 'sumpass')
	#githubprojects = projects.get_github_projects(project_names)
	#return render_template('projects.html',
	#                       githubactions=githubactions,
	#                       githubprojects=githubprojects)
	return render_template('projects.html')


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


if __name__ == '__main__':
	app.run()
	#app.run(host='10.0.0.3', port=8000)
