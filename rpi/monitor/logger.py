
import time
from datetime import datetime


class Logger:
	log_levels = {
		"INFO":15,
		"DEBUG":7,
		"WARN":3,
		"ERROR":1,
	}
	def __init__(self,logdir,level):
		self.error_log = open("%s/sensor-monitor-error.log" % logdir,'a')
		self.all("initializing at loglevel %s" % level)
		try:
			self.loglevel = int(self.log_levels[level])
		except:
			self.loglevel = 1;
			self.all("Invalid loglevel %s. Setting to ERROR" % level)

	def error(self,message):
		if (self.loglevel & 1):
			self.write("ERROR",message)
	
	def warn(self,message):
		if (self.loglevel & 2):
			self.write("WARN",message)

	def debug(self,message):
		if (self.loglevel  & 4):
			self.write("DEBUG",message)

	def info(self,message):
		if (self.loglevel & 8):
			self.write("INFO",message)

	def all(self,message):
		self.write("ALL",message)
		
	def write(self,msgtype,message):
		self.error_log.write("%s: [%s] %s\n" % (msgtype,self.now(),message))
		self.error_log.flush()
	
	def now(self):
		return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

		






