#!/bin/bash

sudo service postgresql restart && ./app/create_db.py && sudo service apache2 restart
