#!/usr/bin/env python3

from flask import Flask, render_template, jsonify
import sys

import blog


app = Flask(__name__)


@app.route('/')
@app.route('/index')
@app.route('/home')
def index():
	blogentries = blog.parse_blog()
	return render_template('index.html', blogentries=blogentries)


@app.route('/projects')
def projects():
	return render_template('projects.html')


@app.route('/resume')
def resume():
	return render_template('resume.html')


@app.route('/about')
def about():
	return render_template('about.html')


@app.route('/<path:path>')
def static_proxy(path):
	if '.' not in path:
		path += '.html'
	return app.send_static_file(path)


if __name__ == '__main__':

	blog.parse_blog()

	app.run()
	#app.run(host='10.0.0.3', port=8000)
