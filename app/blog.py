import feedparser


def parse_blog():
	retval = []
	results = feedparser.parse('http://blog.bismith.net/?feed=rss')
	if 'entries' in results:
		entries = results['entries']
		for e in entries:
			d = {}
			d['url'] = e['id'].replace('http://bismith.net', 'http://blog.bismith.net')
			d['title'] = e['title']
			d['content'] = e['content'][0]['value']
			d['published'] = ' '.join(s for s in e['published'].split(' ')[0:4])
			retval.append(d)
	return retval


if __name__ == '__main__':
	entries = parse_blog()
	for e in entries:
		print(e)
