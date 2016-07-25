#!/bin/bash

sudo service postgresql restart && (cd app && ./create_db.py) && sudo service apache2 restart
