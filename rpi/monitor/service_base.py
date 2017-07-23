import json
import xml.etree.ElementTree as ElementTree

class Service:
	def __init__(config,logger):
		self.config = config;
		self.logger = logger;

	def fetch(self,params):
		self.logger.debug("sir this is an abstract base class")
		return None

	def value_from_json(self,xpath,data):
		self.logger.debug("Request to %s from worker returned: %s" % (self.config['name'],json.dumps(data)))
		value=data
		lastnode = ""

		for node in xpath.split("/"):

			if (value==None):
				break
			if (isinstance(value,dict)):
				if (node in value):
					value = value[node]
				else:
					self.logger.warn("Value %s not found. Please check API docs for correct format of xpath %s" % (node,xpath))
					value = None
					break
			elif(isinstance(value,list)):
				if (not len(value)):
					self.logger.error("No rows returned for array element '%s' in path '%s' for worker %s." % (lastnode,xpath,self.config['name']))
					value = None
					break
				value = value[int(node)]
				
					
			lastnode = node
		return value

	def value_from_xml(self,xpath,body):
		value = None
		try:
			tree = ElementTree.fromstring(body)
		except Exception as e:
			return ret
		
		node = tree.find(xpath)

		if (self.attribute):
			value =  node.attrib[self.attribute]
		else:
			value =  node.text
	
		return value
	
	def from_query_string(self,text):
		for pair in text.split('&'):
			kv = pair.split("=")
			if (kv[0]==self.attribute):
				return kv[1]
		return None


