#!/usr/bin/env python3

import modules.weather as weather


def get_owm():
	return weather.get_owm()


def get_noaa():
	return weather.get_noaa()
