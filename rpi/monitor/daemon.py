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
		self.logger = Logger(self.config['logdir'],self.config['loglevel'])

	def start(self):
		for device in self.config['devices']:
			service = self.config['services'][device['source']]

			if (not service):
			   self.logger.error("Invalid service %s for %s. Skipping." % (device['source'],device['name']))
			else:
				worker = Worker(device,service,self.logger)
				self.threads.append(worker);
				worker.start()
		if (len(self.threads)<1):
			self.logger.error("No valid devices. Please check logs.")
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
			self.logger.info("Exiting");
			sys.exit(0);
		elif (sig==signal.SIGHUP):
			self.logger.info("Received HUP")

	def load_config(self,conf_file):
		try:
			xml = open(conf_file).read()
			config = xmltodict.parse(xml)['config']#l=['device','service','params','criteria'])['config']
		except Exception as e:
			print "Unable to load configuration: %s:" % e
			sys.exit(1)

		# raspbian's version of xmltodict does not support force_array. Huzzah.
		if (isinstance(config['services'],dict)):
			config['services'] = {config['services']['name']:config['services']}
		else:
			config['services'] = dict((a['name'],a) for a in config['services'])

		if (isinstance(config['devices'],dict)):
			config['devices'] = [config['devices']]

	
		for device in config['devices']:
			for field in ['handlers','criteria']:
				if (not isinstance(device[field],list)):
					device[field] = [device[field]]

			if (isinstance(device['params'],dict)):
				device['params'] = {device['params']['@name']:device['params']['@value']}
			else:
				device['params'] = dict((a['name'],a['value']) for a in service['params'])

		for k in config['services']:
			service = config['services'][k]
			if (isinstance(service['params'],dict)):
				service['params'] = {service['params']['@name']:service['params']['@value']}
			else:
				service['params'] = dict((a['@name'],a['@value']) for a in service['params'])

		return config
