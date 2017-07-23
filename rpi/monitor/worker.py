import threading
import json
import xml.etree.ElementTree as ElementTree
import time
import requests
import re
import os
import importlib
import subprocess
#import RPI.GPIO as GPIO

class Worker(threading.Thread): 
	def __init__(self,config,source,logger):
		threading.Thread.__init__(self)

		self.running = True
		self.logger = logger;
		self.event = threading.Event()
		self.event.clear()
		self.last_action = None

		for key in config:
			setattr(self,key,config[key])

		self.source = source
		self.type = self.source['type']
		handler_mod = importlib.import_module(self.source['module'])
		self.service_handler = getattr(handler_mod,"Handler")(source,logger);

		try:
			self.test_value = getattr(self,self.passes_when)
		except:
			self.logger.error("Test %s in worker %s is not supported." % (self.passes_when,self.name))
			self.running = False

		try:
			handler_mod = importlib.import_module(self.source['module'])
			self.service_handler = getattr(handler_mod,"Handler")(source,logger);
		except Exception as e:
			self.logger.error("Unable to import module %s: for worker %s %s" % (self.source['module'],self.name,e))
			self.running = False

	def run(self):
		if (not self.running):
			self.logger.error("Worker %s unable to start." % self.name)
			return
		self.logger.info("Starting thread for worker %s" % self.name)
		while(self.running):
			self.event.wait(float(self.every_x_seconds))
			current_value = self.service_handler.fetch(self.params)
			if (current_value!=None):
				passed = self.test_value(current_value)
				if (passed):
					self.logger.info("Worker %s passed test %s(%s) with value %s" % (self.name,self.passes_when,",".join(self.criteria),current_value))
					self.last_action = None
			
	def stop(self):
		self.logger.all("Killing thread %s" % self.name);
		self.running=False
		self.event.set()

	def exception(self,value=0,action=0):
		self.logger.warn("Worker %s failed test %s(%s) with value %s" % (self.name,self.passes_when,",".join(self.criteria),value))
		handler = self.handlers[action]
		x = None
		if (action == self.last_action):
			self.logger.debug("Already processed handler '%s' for the current error condition in worker %s" % (handler,self.name))
			return False;
		try:
			self.logger.debug("Running handler '%s' for worker %s" % (handler,self.name))
			hp= re.findall(r'[^"\s]\S*|".+?"',self.handlers[action])

			x = subprocess.check_output(hp,stderr=subprocess.STDOUT)
			self.logger.debug("Handler %s on worker %s  returned %s" % (handler,self.name,x))

			self.last_action = action
		except Exception as e:
			self.logger.error("Unable to execute '%s' for worker %s: %s %s" % (handler,self.name,e,x))

		self.event.wait(float(self.sleep_on_fail))
		return False

	# test values against criteria route accordingly

	def is_less_than(self,value):
		if (float(value)>float(Self.criteria[0])):
			return self.exception(value,0)
		return True

	def is_greater_than(self,value):
		if (float(value)<float(self.criteria[0])):
			return self.exception(value,0)
		return True

	def is_equal(self,value):
		if (float(value)!=float(self.criteria[0])):
			return exception(value,0)
		return true

	def is_between(self,value=0):
		if(float(value)<float(self.criteria[0])):
			return self.exception(value,0)
		elif(float(value)>float(self.criteria[1])):
			return self.exception(value,1)
		return True
