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

URL_BASE_OWM = 'http://api.openweathermap.org/data/2.5/weather?id={}&APPID={}'
URL_BASE_OWM_FORECAST = 'http://api.openweathermap.org/data/2.5/forecast/city?id={}&APPID={}'
URL_BASE_MAP = 'https://www.google.com/maps/place/{}%C2%B0{}\'{}+{}%C2%B0{}\'{}'
URL_BASE_MAP_METRIC = 'https://www.google.com/maps/place/{}+{}'
URL_BASE_NOAA = 'http://forecast.weather.gov/MapClick.php?lat={}&lon={}&FcstType=json'

CITY_ID_AUSTIN = 4671654
TIMEZONE_OFFSET = -6 # UTC-6, hardcoded to CST

STATES = ('Alabama',
          'Alaska',
          'Arizona',
          'Arkansas',
          'California',
          'Colorado',
          'Connecticut',
          'Delaware',
          'Florida',
          'Georgia',
          'Hawaii',
          'Idaho',
          'Illinois',
          'Indiana',
          'Iowa',
          'Kansas',
          'Kentucky',
          'Louisiana',
          'Maine',
          'Maryland',
          'Massachusetts',
          'Michigan',
          'Minnesota',
          'Mississippi',
          'Missouri',
          'Montana',
          'Nebraska',
          'Nevada',
          'New Hampshire',
          'New Jersey',
          'New Mexico',
          'New York',
          'North Carolina',
          'North Dakota',
          'Ohio',
          'Oklahoma',
          'Oregon',
          'Pennsylvania',
          'Rhode Island',
          'South Carolina',
          'South Dakota',
          'Tennessee',
          'Texas',
          'Utah',
          'Vermont',
          'Virginia',
          'Washington',
          'West Virginia',
          'Wisconsin',
          'Wyoming')

DAYS = (('Sunday',    'Sun', 'S'),
        ('Monday',    'Mon', 'M'),
        ('Tuesday',   'Tue', 'T'),
        ('Wednesday', 'Wed', 'W'),
        ('Thursday',  'Thu', 'Th'),
        ('Friday',    'Fri', 'F'),
        ('Saturday',  'Sat', 'Sa'))


def ctof(c):
	return (c * 1.8) + 32

def ftoc(f):
	return (f - 32) / 1.8

def ktoc(k):
	return k - 273.15

def ktof(k):
	return ctof(ktoc(k))

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


def get_api_key_openweathermap():
	with open(os.path.join(API_KEY_DIR, API_KEY_WEATHER)) as keyfile:
		key = keyfile.readline().strip()
	return key


def get_owm_cached(cityid):
	cache_path = os.path.join(CACHE_DIR, 'owm_{}.json'.format(cityid))
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


def get_owm_fresh(cityid):
	cache_path = os.path.join(CACHE_DIR, 'owm_{}.json'.format(cityid))
	url = URL_BASE_OWM.format(cityid, get_api_key_openweathermap())
	with urllib.request.urlopen(url) as response:
		data = json.loads(response.read().decode('utf-8'))
	with open(cache_path, 'w') as outfile:
		json.dump(data, outfile)
	return data


def get_owm(cityid = CITY_ID_AUSTIN):
	data = get_owm_cached(cityid)
	if not data:
		data = get_owm_fresh(cityid)
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


def get_owm_forecast_cached(cityid):
	cache_path = os.path.join(CACHE_DIR, 'owm_forecast_{}.json'.format(cityid))
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


def get_owm_forecast_fresh(cityid):
	cache_path = os.path.join(CACHE_DIR, 'owm_forecast_{}.json'.format(cityid))
	url = URL_BASE_OWM_FORECAST.format(cityid, get_api_key_openweathermap())
	with urllib.request.urlopen(url) as response:
		data = json.loads(response.read().decode('utf-8'))
	with open(cache_path, 'w') as outfile:
		json.dump(data, outfile)
	return data


def get_owm_forecast(cityid = CITY_ID_AUSTIN):
	data = get_owm_forecast_cached(cityid)
	if not data:
		data = get_owm_forecast_fresh(cityid)
	return data


def get_noaa_cached(lat, lon):
	cache_path = os.path.join(CACHE_DIR, 'noaa_{}_{}.json'.format(lat, lon))
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


def get_noaa_fresh(lat, lon):
	cache_path = os.path.join(CACHE_DIR, 'noaa_{}_{}.json'.format(lat, lon))
	url = URL_BASE_NOAA.format(lat, lon)
	with urllib.request.urlopen(url) as response:
		data = json.loads(response.read().decode('utf-8'))
	with open(cache_path, 'w') as outfile:
		json.dump(data, outfile)
	return data


def get_noaa(lat = '30.358474196237566', lon = '-97.74917148132334'):
	data = get_noaa_cached(lat, lon)
	if not data:
		data = get_noaa_fresh(lat, lon)
	cityname = data['currentobservation']['name'].split(',')[0]
	if cityname[-5:] == ' City' and cityname[:-5] not in STATES:
		cityname = cityname[:-5]
	forecast = []
	for i in range(min(12, len(data['data']['pop']))):
		forecast.append({
			'tempf':      int(data['data']['temperature'][i]),
			'temp_name': data['time']['tempLabel'][i],
			'cond':      data['data']['weather'][i],
			'precip':    data['data']['pop'][i],
			'text':      data['data']['text'][i],
			'icon':      data['data']['iconLink'][i],
			'time':      data['time']['startValidTime'][i],
			'time_name': data['time']['startPeriodName'][i],
		})
	for item in forecast:
		item['tempc'] = round(ftoc(item['tempf']))
		item['class'] = 'templow'
		if item['temp_name'] == 'High':
			item['class'] = 'temphigh'
		for day in DAYS:
			if item['time_name'].startswith(day[0]):
				item['time_name'] = day[1] + item['time_name'][len(day[0]):]
	icon = 'http://forecast.weather.gov/newimages/large/' + data['currentobservation']['Weatherimage']
	clean = {
		'name':      cityname,# + ', ' + data['currentobservation']['state'],
		'coord_lat': float(data['currentobservation']['latitude']),
		'coord_lon': float(data['currentobservation']['longitude']),
		'tempf':     int(data['currentobservation']['Temp']),
		'cond':      data['currentobservation']['Weather'],
		'date':      data['currentobservation']['Date'],
		'icon':      icon,
		'forecast':  forecast,
		'data':      data
	}
	clean['tempc'] = round(ftoc(clean['tempf']))
	clean['coord'] = '{}, {}'.format(clean['coord_lat'], clean['coord_lon'])
	clean['url_map'] = URL_BASE_MAP_METRIC.format(clean['coord_lat'], clean['coord_lon'])
	return clean


if __name__ == '__main__':
	print(get_owm())
	print(get_owm_forecast())
