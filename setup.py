#!/usr/bin/env python

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
setup(
    name='instrument-monitor',

    version='0.0.1',

    description='A sensor monitor for Raspbian',
    long_description="Monitor an arbitrary number of sensors and services for arbitrary values and launch handler scripts"
    url='https://github.com/hollenbeck-ml/raspberry_pi_sensor-monitor',
    author='Michael Hollenbeck',
    author_email='hollenbeck.ml@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='raspberrypi sbcs',
    py_modules=["instrument-monitor"],

    install_requires=['yaml','RPi.GPIO','datetime','requests'],

    entry_points={
        'console_scripts': [
            'instrument-monitor=instrument-monitor:main',
        ],
    },
)
