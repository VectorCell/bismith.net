#!/usr/bin/env python3

from flask import Markup
import markdown
import urllib.request
import feedparser


def get_github_actions():
	results = feedparser.parse('https://github.com/VectorCell.atom')
	for entry in results['entries']:
		yield {
			'title': entry['title'],
			'content': entry['summary'].replace('href="/', 'href="http://github.com/')
		}

def get_github_projects(names):
	for name in names:
		readme_url = 'https://raw.githubusercontent.com/VectorCell/' + name + '/master/README.md'
		response = urllib.request.urlopen(readme_url)
		readme = response.read().decode('utf-8')
		#readme = Markup(markdown.markdown(readme))
		yield {'name': name, 'description': readme}


if __name__ == '__main__':
	for action in get_github_actions():
		print(action['title'])
		print(action['content'])
		print()
		pass
