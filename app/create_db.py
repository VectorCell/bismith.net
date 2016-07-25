#!/usr/bin/env python3

import json

from models import db, User, Project


def create_db():
	db.drop_all()
	db.create_all()

	create_users()
	create_projects()

	db.session.commit()

	print()
	print('The database contains:')
	for user in User.query.all():
		print(repr(user))
		print('\tid:', user.id)
		print('\tname:', user.name)
	for project in Project.query.all():
		print(repr(project))
		print('\tid:', project.id)
		print('\tname:', project.name)
		print('\tauthor:', project.author)
		print('\tdescription:', project.description)


def create_users():
	with open('data/users.json') as users_file:
		users = json.load(users_file, strict=False)

	for d in users:
		id = d['id']
		name = d['name']

		user = User.query.get(id)
		if not user:
			user = User(id=id, name=name)
		else:
			user.name = name

		db.session.add(user)
		print('Adding', repr(user))


def create_projects():
	with open('data/projects.json') as projects_file:
		projects = json.load(projects_file, strict=False)

	for d in projects:
		id = d['id']
		name = d['name']
		author = d['author']

		if isinstance(d['description'], str):
			description = d['description']
		elif isinstance(d['description'], list):
			description = '</p><p>'.join(line for line in d['description'])
			description = '<p>' + description + '</p>'
	
		project = Project.query.get(id)
		if not project:
			project = Project(id=id, name=name, author=author,
			                  description=description)
		else:
			project.name = name

		db.session.add(project)
		print('Adding', repr(project))


if __name__ == '__main__':
	create_db()
