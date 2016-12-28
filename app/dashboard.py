#!/usr/bin/env python3

import os
import tempfile
import urllib.request
import json
import time
import datetime


API_KEY_DIR = '/keys'
API_KEY_WEATHER = 'openweathermap_api_key.txt'

CACHE_DIR = '/tmp/weather_cache_{}'.format(os.getuid())
CACHE_LIFESPAN = (60 * 60) # 1 hour

URL_BASE_WEATHER = 'http://api.openweathermap.org/data/2.5/weather?id={}&APPID={}'
URL_BASE_FORECAST = 'http://api.openweathermap.org/data/2.5/forecast/city?id={}&APPID={}'
URL_BASE_MAP = 'https://www.google.com/maps/place/{}%C2%B0{}\'{}+{}%C2%B0{}\'{}'

CITY_ID_AUSTIN = 4671654
TIMEZONE_OFFSET = -6 # UTC-6, hardcoded to CST


def ktoc(k):
	return k - 273.15

def ktof(k):
	return (ktoc(k) * 1.8) + 32

def speed_imperial(v):
	return round(v * 2.23694, 1)

def coordinates(coord):
	latd = int(coord['lat'])
	latm = abs(round((coord['lat'] - latd) * 60))
	lato = 'N'
	if latd < 0:
		latd *= -1
		lato = 'S'
	lond = int(coord['lon'])
	lonm = abs(round((coord['lon'] - lond) * 60))
	lono = 'E'
	if lond < 0:
		lond *= -1
		lono = 'W'
	return '{}°{}\' {}, {}°{}\' {}'.format(latd,
	                                       latm,
	                                       lato,
	                                       lond,
	                                       lonm,
	                                       lono)

def convert_timestamp(stamp, strformat = '%Y-%m-%d %H:%M:%S'):
	stamp += (TIMEZONE_OFFSET * 60 * 60)
	return datetime.datetime.utcfromtimestamp(int(stamp)).strftime(strformat)

def get_map_url(coord):
	latd = int(coord['lat'])
	latm = abs(round((coord['lat'] - latd) * 60))
	lato = 'N'
	if latd < 0:
		latd *= -1
		lato = 'S'
	lond = int(coord['lon'])
	lonm = abs(round((coord['lon'] - lond) * 60))
	lono = 'E'
	if lond < 0:
		lond *= -1
		lono = 'W'
	return URL_BASE_MAP.format(latd, latm, lato, lond, lonm, lono)


def get_api_key_weather():
	with open(os.path.join(API_KEY_DIR, API_KEY_WEATHER)) as keyfile:
		key = keyfile.readline().strip()
	return key


def get_weather_cached(cityid):
	cache_path = os.path.join(CACHE_DIR, 'weather_{}.json'.format(cityid))
	if not os.path.exists(CACHE_DIR):
		os.mkdir(CACHE_DIR)
	if os.path.exists(cache_path):
		if (os.path.getmtime(cache_path) + CACHE_LIFESPAN) < time.time():
			print('CACHE EXPIRED: ' + cache_path)
			os.remove(cache_path)
			return None
		with open(cache_path, 'r') as cache_file:
			data = json.load(cache_file)
		return data
	else:
		return None


def get_weather_fresh(cityid):
	cache_path = os.path.join(CACHE_DIR, 'weather_{}.json'.format(cityid))
	url = URL_BASE_WEATHER.format(cityid, get_api_key_weather())
	with urllib.request.urlopen(url) as response:
		data = json.loads(response.read().decode('utf-8'))
	with open(cache_path, 'w') as outfile:
		json.dump(data, outfile)
	return data


def get_weather(cityid = CITY_ID_AUSTIN):
	data = get_weather_cached(cityid)
	if not data:
		data = get_weather_fresh(cityid)
	return {
		'name':        data['name'],
		'coord':       coordinates(data['coord']),
		'url_map':     get_map_url(data['coord']),
		'url_more':    'https://openweathermap.org/city/{}'.format(cityid),
		'temp':        data['main']['temp'],
		'tempc':       round(ktoc(data['main']['temp'])),
		'tempf':       round(ktof(data['main']['temp'])),
		'lowc':        round(ktoc(data['main']['temp_min'])),
		'lowf':        round(ktof(data['main']['temp_min'])),
		'highc':       round(ktoc(data['main']['temp_max'])),
		'highf':       round(ktof(data['main']['temp_max'])),
		'cond':        data['weather'][0]['main'],
		'cond_detail': data['weather'][0]['description'],
		'wind_speed':  speed_imperial(data['wind']['speed']),
		'sunrise':     convert_timestamp(data['sys']['sunrise'], '%H:%M'),
		'sunset':      convert_timestamp(data['sys']['sunset'], '%H:%M'),
		'updated':     convert_timestamp(data['dt']),
		'source':      data,
		'valid':       True
	}


def get_forecast_cached(cityid):
	cache_path = os.path.join(CACHE_DIR, 'forecast_{}.json'.format(cityid))
	if not os.path.exists(CACHE_DIR):
		os.mkdir(CACHE_DIR)
	if os.path.exists(cache_path):
		if (os.path.getmtime(cache_path) + CACHE_LIFESPAN) < time.time():
			print('CACHE EXPIRED: ' + cache_path)
			os.remove(cache_path)
			return None
		with open(cache_path, 'r') as cache_file:
			data = json.load(cache_file)
		return data
	else:
		return None


def get_forecast_fresh(cityid):
	cache_path = os.path.join(CACHE_DIR, 'forecast_{}.json'.format(cityid))
	url = URL_BASE_FORECAST.format(cityid, get_api_key_weather())
	with urllib.request.urlopen(url) as response:
		data = json.loads(response.read().decode('utf-8'))
	with open(cache_path, 'w') as outfile:
		json.dump(data, outfile)
	return data


def get_forecast(cityid = CITY_ID_AUSTIN):
	data = get_forecast_cached(cityid)
	if not data:
		data = get_forecast_fresh(cityid)
	return data


if __name__ == '__main__':
	print(get_weather())
	print(get_forecast())
