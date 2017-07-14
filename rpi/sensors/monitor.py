import yaml
import threading
import time
from rpi.sensors.worker import Worker
from datetime import datetime
import signal
import sys
from rpi.sensors.logger import Logger

class Monitor():
	def __init__(self,conf_file="/etc/sensor-monitor/monitor.conf"):
		self.threads = []
		try:
			self.config = yaml.load(open(conf_file))
		except Exception as e:
			print "Unable to open %s" % conf_file
			exit(1)

		self.logger = Logger(self.config['logdir'])

	def start(self):
		for device in self.config['devices']:
			source = config['sources'][device['source']
			if (!source):
			   self.logger.error("Invalid source %s for %s" % (device['source'],device['name']))
			else:
				worker = Worker(device,source,self.logger)
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

