import requests
import sys
import json
import rpi.monitor.service_base as service_base
import math
from datetime import datetime,timedelta

class Handler(service_base.Service):
	LOG_BASE =  2.71828
	def __init__(self,config,logger):
		self.config = config
		self.logger = logger

	def fetch(self,params):

		end = datetime.now()
		start = end - timedelta(minutes=5)

		params['toDate'] = end.strftime("%Y-%m-%dT%H:%M:%S")
		params['fromDate'] = start.strftime("%Y-%m-%dT%H:%M:%S")
		params['dataType'] = "json"

		self.logger.info("Request to %s" % self.config['url']) 
		self.logger.info("Sending params %s" % json.dumps(params))
	
		res = requests.post(
			self.config['url'],
			json=params,
			headers={"content-type":"application/json"}
		).json()

		humidity = self.value_from_json(self.config['xpath-humidity'],res);

		if (self.config['mode'] == "relative"):
			return humidity

		temperature = self.value_from_json(self.config['xpath-temp'],res);
		humidity = float(humidity)

		absolute_humidity = (6.112 * math.exp((17.67 * temperature)/(temperature+243.5)) * humidity * 2.1674)/(273.15+temperature)
		self.logger.info("Absolute humidity for %fC/relative %f is: %f" % (temperature,humidity,absolute_humidity))
		return absolute_humidity
		
		

		
