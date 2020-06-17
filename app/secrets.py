import os


SECRETS = {}
# currently, these will be loaded from the secrets dir (secrets)
# from /api/alert:
# pushover_user_key
# pushover_app_token_scripts


def get_secret_from_file(token_name):
	try:
		dir_path = os.path.dirname(os.path.realpath(__file__))
		filename = dir_path + '/secrets/' + token_name
		return get_file_contents(filename)
	except Exception as ex:
		print("Exception in get_secret_from_file:", ex)
		return NULL


def get_secret(token_name):
	if token_name not in SECRETS:
		SECRETS[token_name] = get_secret_from_file(token_name)
	return SECRETS[token_name]


def get_file_contents(filename):
	with open(filename, 'r') as f:
		return f.read().strip()
