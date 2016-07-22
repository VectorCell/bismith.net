#!/usr/bin/env python3

import sys
import logging

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/var/www/bismith/')

from app import app as application
application.secret_key = 'secret'
