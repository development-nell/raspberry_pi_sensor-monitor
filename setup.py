#!/usr/bin/env python

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
setup(
	name='rpi.sensors',
	version='0.0.3',
	description='A sensor monitor for Raspbian',
	long_description="Monitor an arbitrary number of sensors and services for arbitrary values and launch handler scripts",
	url='https://github.com/hollenbeck-ml/raspberry_pi_sensor-monitor',
	author='Michael Hollenbeck',
	author_email='hollenbeck.ml@gmail.com',
	license='MIT',
	keywords='raspberrypi sbcs',
	packages=["rpi","rpi.monitor","rpi.monitor.service"],
	install_requires=['datetime','requests','xmltodict','importlib'],
	data_files=[
		('/etc/sensor-monitor',['etc/monitor.conf']),
		('/etc/systemd/system',['etc/sensor-monitor.service']),
		('/etc/logrotate.d/',['etc/sensor-monitor-logrotate'])
	],
	scripts=['sensor-monitor']
)
