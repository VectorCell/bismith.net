#!/usr/bin/env python3

import sys
import logging

logging.basicConfig(stream=sys.stderr)
if '/var/www/bismith/' not in sys.path:
    sys.path.insert(0, '/var/www/bismith/')
if '/var/www/bismith/app/' not in sys.path:
    sys.path.insert(1, '/var/www/bismith/app/')

from app import app as application
application.secret_key = 'secret'
