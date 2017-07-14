import yaml
import threading
import time
from rpi.monitor.worker import Worker
from datetime import datetime
import signal
import sys
import xmltodict
import json
from rpi.monitor.logger import Logger


class Daemon():
	def __init__(self,conf_file="/etc/sensor-monitor/monitor.conf"):
		self.threads = []
		self.config = self.load_config(conf_file)
		self.logger = Logger(self.config['logdir'])

	def start(self):
		for device in self.config['devices']:
			service = self.config['services'][device['source']]

			if (not service):
			   self.logger.error("Invalid service %s for %s" % (device['source'],device['name']))
			else:
				worker = Worker(device,service,self.logger)
				self.threads.append(worker);
				worker.start()
		if (len(self.threads)<1):
			print "No valid devices. Please check logs."
		else:
			signal.signal(signal.SIGINT,self.signal_received)
			signal.signal(signal.SIGTERM,self.signal_received)
			signal.signal(signal.SIGHUP,self.signal_received)
			signal.pause()

	def quit(self):
		for thread in self.threads:
			thread.stop()
			thread.join()
	def signal_received(self,sig,frame):
		if (sig==signal.SIGINT or sig==signal.SIGTERM):
			self.quit()
			self.logger.error("Exiting");
			sys.exit(0);
		elif (sig==signal.SIGHUP):
			self.logger.error("Received HUP")
	def load_config(self,conf_file):
		try:
			xml = open(conf_file).read()
			config = xmltodict.parse(xml,force_list=['device','service','params','criteria'])['config']
		except Exception as e:
			print "Unable to load configuration: %s:" % e
			sys.exit(1)

		config['services'] = dict((a['name'],a) for a in config['services']['service'])
		config['devices'] = config['devices']['device']

		for device in config['devices']:
			device['params'] = dict((a['name'],a['value']) for a in device['params'])
			device['handlers'] = device['handlers']['handler']

		for k in config['services']:
			service = config['services'][k]
			service['params'] = dict((a['name'],a['value']) for a in service['params'])

		return config
