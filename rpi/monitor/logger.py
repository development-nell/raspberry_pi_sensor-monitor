
import time
from datetime import datetime

class Logger:
	def __init__(self,logdir):
		self.error_log = open("%s/sensor-monitor-error.log" % logdir,'a')

	def error(self,message):
		self.error_log.write("[%s] %s\n" % (self.now(),message))
		self.error_log.flush()

	def now(self):
		return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

		






