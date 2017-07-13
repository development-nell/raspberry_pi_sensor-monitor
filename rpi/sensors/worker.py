import threading
import json
import xml.etree.ElementTree as ElementTree
import time
import requests
import re

#import RPI.GPIO as GPIO

class Worker(threading.Thread): 
	def __init__(self,options,logger):
		threading.Thread.__init__(self)
		self.options = options
		self.running = True
		self.log = logger;
		self.event = threading.Event()

		for key in options:
			setattr(self,key,options[key])

		self.type = self.input['type']

		if (hasattr(self,"setup_%s" % self.type)):
			getattr(self,"setup_%s" % self.type)()

		try:
			self.passes = getattr(self,self.passes_when)
			self.getvalue = getattr(self,"process_%s" % self.type)
		except:
			self.running=False
			self.log("Invalid test, exiting thread")

	def run(self):
		self.log("Starting thread for %s" % self.name)
		while(self.running):
			current_value = self.getvalue()
			if (not current_value == None):
				if (not self.passes(current_value)):
					self.triggered(current_value)
					self.event.wait(self.interval);
			
	def stop(self):
		self.log("caught term signal");
		self.running=False
		self.event.set()

	#setup functions
	#
	#def setup_gpio():
		#for pin in self.pins:
			#GPIO.setup(self.pins[pin], GPIO.IN,pull_up_down = GPIO.PUD_DOWN)

	def setup_webservice(self):
		self.url = self.input['url']
		self.xpath = self.input['xpath']
		self.attribute = self.input['attribute']

	def triggered(self,value=0):
		try:
			exec(self.handler)
		except:
			self.log("Unable to execute %s" % self.handler)
		self.event.wait(self.sleep_after)

	def is_less_than(self,value):
		return int(value)<self.criteria[0]
	def is_greater_than(self,value):
		return int(value)>self.criteria[0]
	def is_equal(self,value):
		return int(value)==self.threshold
	def is_between(self,value=0):
		return (int(value)>=self.criteria[0] and int(value)<=self.criteria[1])

	# value getters
	def process_gpio(self):
		# don't need this quite yet and I don't even have a PI 
		# and I'm too lazy to mock it up
		return 0;

	def process_webservice(self):
		try:
			res = requests.get(self.url)
		except Exception as e:
			self.log("Unable to fetch %s %s" % (self.url,e))
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
				self.log("THIS REGEX IMPLEMENTATION SUCKS BALLS")
		else:
			self.log("request to %s returned status %d" % (self.url,res.status_code,res.status_line))
			return 0;

		return 0

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
