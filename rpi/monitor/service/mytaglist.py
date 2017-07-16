import requests
import sys
import json
from datetime import datetime,timedelta

def fetch(url,logger,params):

	end = datetime.now()
	start = end - timedelta(minutes=5)

	params['toDate'] = end.strftime("%Y-%m-%dT%H:%M:%S")
	params['fromDate'] = start.strftime("%Y-%m-%dT%H:%M:%S")
	params['dataType'] = "json"

	logger.info("Request to %s" % url) 
	logger.info("Sending params %s" % json.dumps(params))
	
	res = requests.post(
		url,
		json=params,
		headers={"content-type":"application/json"}
	)
	return res
