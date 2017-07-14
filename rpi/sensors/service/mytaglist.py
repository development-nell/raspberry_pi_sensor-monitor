
import requests
import sys
from datetime import datetime,timedelta

def fetch(url,params):

	end = datetime.now()
	start = end - timedelta(minutes=1)

	params['endDate'] = end.strftime("%Y-%m-%d %H:%M:%S")
	params['fromDate'] = start.strftime("%Y-%m-%d %H:%M:%S")

	res = requests.post(
    	url,
    	json=params,
    	headers={"content-type":"application/json"}
	)
	return res


	
