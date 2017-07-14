
import time
from datetime import datetime

class Logger:
	def __init__(self,logdir):
		self.sensor_log = open("%s/sensor.log" % logdir,'a')
		self.error_log = open("%s/error.log" % logdir,'a')

	def error(self,message):
		self.error_log.write("[%s] %s\n" % (self.now(),message))
		self.error_log.flush()

	def sensor(self,name,value):
		self.sensor_log.write("%s|%s|%s\n" % (name,self.now(),str(value)))
		self.sensor_log.flush()

	def now(self):
		return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

		






