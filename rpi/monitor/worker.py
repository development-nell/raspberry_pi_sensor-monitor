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
		self.service_handler = importlib.import_module(self.source['module'])

		if (hasattr(self,"setup_%s" % self.type)):
			getattr(self,"setup_%s" % self.type)()

		try:
			self.test_value = getattr(self,self.passes_when)
		except:
			self.logger.error("Test %s in worker %s is not supported." % (self.passes_when,self.name))
			self.running = False
		try:
			self.fetch_value = importlib.import_module(self.source['module'])
		except Exception as e:
			self.logger.error("Unable to import module %s: for worker %s %s" % (self.source['module'],self.name,e))
			self.running = False
		try:	
			self.getvalue = getattr(self,"process_%s" % self.type)
		except Exception as e:
			self.running=False
			self.logger.error("Service type '%s' invalid for worker" % (self.type,self.name))

	def run(self):
		if (not self.running):
			self.logger.error("Worker %s unable to start." % self.name)
			return
		self.logger.info("Starting thread for worker %s" % self.name)
		while(self.running):
			self.event.wait(float(self.every_x_seconds))
			current_value = self.getvalue()
			if (current_value):
				passed = self.test_value(current_value)
				if (passed):
					self.last_action = None
			
	def stop(self):
		self.logger.all("Killing thread %s" % self.name);
		self.running=False
		self.event.set()

	#setup functions
	#
	#def setup_gpio():
		#for pin in self.pins:
			#GPIO.setup(self.pins[pin], GPIO.IN,pull_up_down = GPIO.PUD_DOWN)

	def setup_webservice(self):
		self.logger.info("Initializing webservice %s for worker %s" % (self.source['name'],self.name))
		self.url = self.source['url']
		self.xpath = self.source['xpath']
		self.attribute = self.source['attribute']
		self.logger.info("Using url %s and xpath %s" % (self.url,self.xpath))

	def exception(self,value=0,action=0):
		self.logger.warn("Worker %s failed test %s(%s) with value %s" % (self.name,self.passes_when,",".join(self.criteria),value))
		handler = self.handlers[action]
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
			self.logger.error("Unable to execute '%s' for worker %s: %s" % (handler,self.name,e))

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

	def process_gpio(self):
		# don't need this quite yet
		return 0;

	def process_webservice(self):
		try:
			res = self.service_handler.fetch(self.url,self.logger,self.params)
		except Exception as e:
			self.logger.error("Exception in service request for worker %s: %s" % (self.name,e))
			return None

		content_type = res.headers['content-type']

		if (res.status_code == 200):
			if (re.match('^text/xml',content_type)):
				return self.from_xml(res.text)
			elif (re.match('^application/json',content_type)):
				return self.from_json(res.json())
			elif (re.match('\w+=\w+(?:&)?',res.text)):
				return self.from_query_string(res.text)
			else:
				self.logger.warn("Unable to detect content type from request %s in worker %s" % (self.source['name'],self.name))
		else:
			self.logger.warn("Request to %s returned status %d in worker %s" % (self.url,res.status_code,self.name))
			return None

		return None

	# webservice value extractors
	def from_xml(self,body):
		value = None

		try:
			tree = ElementTree.fromstring(body)
		except Exception as e:
			return ret

		node = tree.find(self.xpath)
		if (self.attribute):
			value =  node.attrib[self.attribute]
		else:
			value =  node.text

		return value
		

	def from_json(self,data):
		self.logger.debug("Request to %s from worker %s returned: %s" % (self.source['name'],self.name,json.dumps(data)))
		value=data
		lastnode = ""
		for node in self.xpath.split("/"):
			if (value==None):
				break
			if (isinstance(value,dict)):
				if (node in value):
					value = value[node]
				else:
					self.logger.warn("Value %s not found. Please check API docs for correct format of xpath %s" % (node,self.xpath))
					value = None
					break
			elif(isinstance(value,list)):
				if (not len(value)):
					self.logger.error("No rows returned for array element '%s' in path '%s' for worker %s." % (lastnode,self.xpath,self.name))
					value = None
					break
				value = value[int(node)]
			lastnode = node
		return value
	
	def from_query_string(self,text):
		for pair in text.split('&'):
			kv = pair.split("=")
			if (kv[0]==self.attribute):
				return kv[1]
		return None
