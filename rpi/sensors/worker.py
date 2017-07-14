import threading
import json
import xml.etree.ElementTree as ElementTree
import time
import requests
import re
import os
import importlib
#import RPI.GPIO as GPIO

class Worker(threading.Thread): 
	def __init__(self,config,source,logger):
		threading.Thread.__init__(self)

		self.config = config
		self.running = True
		self.logger = logger;
		self.source = source
		self.event = threading.Event()
		self.event.clear()
		self.last_action = None

		for key in config:
			setattr(self,key,config[key])

		self.type = self.source['type']

		if (hasattr(self,"setup_%s" % self.type)):
			getattr(self,"setup_%s" % self.type)()

		try:
			self.test_value = getattr(self,self.passes_when)
			self.fetch_value = importlib.import_module(self.source['module'])
			self.getvalue = getattr(self,"process_%s" % self.type)
		except:
			self.running=False
			self.logger.error("Invalid test, exiting thread")
		

	def run(self):
		self.logger.error("Starting thread for %s" % self.name)
		
		while(self.running):
			current_value = self.getvalue()
			if (not current_value == None):
				passed = self.test_value(current_value)
				if (passed)
					self.event.wait(self.every_x_seconds);
			
			
	def stop(self):
		self.logger.error("caught term signal");
		self.running=False
		self.event.set()

	#setup functions
	#
	#def setup_gpio():
		#for pin in self.pins:
			#GPIO.setup(self.pins[pin], GPIO.IN,pull_up_down = GPIO.PUD_DOWN)

	def setup_webservice(self):
		self.url = self.source['url']
		self.xpath = self.input['xpath']
		self.attribute = self.input['attribute']
		self.params={}
		for key in self.input['params']:
			self.params[key] = self.input['params'][key]
		 for key in self.source['default_params']:
            self.params[key] = self.source['default_params'][key]

	def exception(self,value=0,action=0):
		if (action == self.last_action):
			return True
		try:
			os.system(self.handlers[which])
			self.last_action = action
		except:
			self.logger.error("Unable to execute %s" % self.handlers[action])

		self.event.wait(self.sleep_x_seconds_on_error)

	# test values against criteria route accordingly

	def is_less_than(self,value):
		if (not int(value)<self.criteria[0]):
			return self.exception(value,0)

	def is_greater_than(self,value):
		if (int(value)>self.criteria[0]):
			return self.exception(value,0)
		return True

	def is_equal(self,value):
		if (int(value)!=self.threshold):
			return exception(value,0)

	def is_between(self,value=0):
		if(int(value)<self.criteria[0]):
			return self.exception(value,0)
		elif(int(value)>self.criteria[1]):
			return self.exception(value,1)
		return True

	def process_gpio(self):
		# don't need this quite yet and I don't even have a PI 
		# and I'm too lazy to mock it up
		return 0;

	def process_webservice(self):
		try:
			res = requests.get(self.url)
		except Exception as e:
			self.logger.error("Unable to fetch %s %s" % (self.url,e))
			return 0

		content_type = res.headers['content-type']

		if (res.status_code == 200):
			if (re.match('^text/xml',content_type)):
				return self.from_xml(res.text)
			elif (re.match('^application/json',content_type)):
				return self.from_json(res.json())
			elif (re.match('\w+=\w+(?:&)?',res.text)):
				return self.from_query_string(res.text)
			else:
				self.logger.error("Unable to detect content type")
		else:
			self.logger.error("request to %s returned status %d" % (self.url,res.status_code))
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
		

	def from_json(self,json):
		value=json
		for node in self.xpath.split("/"):
			if (value==None):
				break
			if (isinstance(value,dict)):
				value = value[node]
			else:
				value = value[int(node)]
		return value
	
	def from_query_string(self,text):
		for pair in text.split('&'):
			kv = pair.split("=")
			if (kv[0]==self.attribute):
				return kv[1]
		return None
