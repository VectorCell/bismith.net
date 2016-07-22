#!/usr/bin/env python3

import feedparser


def get_github_actions():
	results = feedparser.parse('https://github.com/VectorCell.atom')
	print(type(results))
	for k in results:
		if isinstance(results[k], int) or isinstance(results[k], str):
			print(k, '::', results[k])
		elif isinstance(results[k], list):
			print(k, '::', type(results[k]))
			for item in results[k]:
				print('\t', type(item))
				if isinstance(item, dict):
					for key in item:
						print('\t\t', key, '::', type(item[key]))
		elif isinstance(results[k], dict):
			print(k, '::', type(results[k]))
			for key in results[k]:
				print('\t', key, '::', type(results[k][key]))
		else:
			print(k, '::', type(results[k]))
	for entry in results['entries']:
		#yield {'title': entry['title'], 'content': entry['content'][0]['value']}
		yield {
			'title': entry['title'],
			'content': entry['summary'].replace('href="/', 'href="http://github.com/')
		}


if __name__ == '__main__':
	for action in get_github_actions():
		print(action['title'])
		print(action['content'])
		print()
		pass
