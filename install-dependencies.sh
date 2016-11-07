#!/bin/bash

sudo apt-get install apache2
sudo apt-get install python3 python3-pip python3-dev
sudo apt-get install libapache2-mod-wsgi-py3
sudo apt-get install postgresql postgresql-contrib
sudo apt-get install libpq-dev

sudo pip3 install Flask
sudo pip3 install Flask-SQLAlchemy
sudo pip3 install psycopg2
sudo pip3 install feedparser
sudo pip3 install markdown

sudo a2enmod wsgi
sudo cp bismith.net.conf /etc/apache2/sites-available/
cd /etc/apache2/sites-available/ && sudo a2ensite FlaskApp && cd -
