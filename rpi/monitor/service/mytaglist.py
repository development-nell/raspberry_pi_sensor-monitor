import requests
import sys
import json
from datetime import datetime,timedelta

def fetch(url,params):

	end = datetime.now()
	start = end - timedelta(minutes=1)


	params['toDate'] = end.strftime("%Y-%m-%dT%H:%M:%S")
	params['fromDate'] = start.strftime("%Y-%m-%dT%H:%M:%S")
	params['dataType'] = "json"
	res = requests.post(
		url,
		json=params,
		headers={"content-type":"application/json"}
	)
	return res
