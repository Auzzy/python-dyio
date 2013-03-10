import struct
from serial import Serial
import re

import bowler
import namespaces

class DyIO(object):
	def __init__(self, port, mac):
		self.mac = self._normalize_mac(mac)
		self._namespace_list = []
		self._namespaces = {}
		if isinstance(port,Serial):
			self.port = port
			if not self.port.isOpen():
				self.port.open()
		else:
			self.port = Serial(port=port, baudrate=115200, timeout=1)
		
		self._detect_bowler_version(self)
		self._construct_namespaces()

	def _normalize_mac(self, mac):
		if isinstance(mac,(list,tuple)):
			return ':'.join(["{:>2x}".format(byte) for byte in mac])
		else:
			if not ((':' in mac) ^ ('-' in mac) ^ (' ' in mac)):
				raise ValueError("Invalid MAC address presented: non-uniform delimiters.")

			return re.sub("[- ]", ':', mac)
	
	def _construct_namespaces(self):
		namespaces.init_core(self)
		
		count = namespaces.count(self)
		for index in range(count):
			namespace = namespaces.get(self,index)
			self._namespace_list.append(namespace.name)
			self._namespaces[namespace.name] = namespace
	
	def _detect_bowler_version(self, core):
		bowler.detect_version(core)
	
	def get_namespace(self, id):
		if isinstance(id,int):
			return self._namespaces[self._namespace_list[id]]
		else:
			return self._namespaces[id] if id in self._namespaces else None
	
	def get_core_namespace(self):
		return self.get_namespace(0)

	@staticmethod
	def _get_affect_args(affect):
		affect_args = {"priority":32, "state":False, "async":False}
		if affect==bowler.Affect.CRIT:
			affect_args["priority"] = 0
		elif affect==bowler.Affect.POST:
			affect_args["state"] = True
		elif affect==bowler.Affect.ASYNC:
			affect_args["async"] = True
		return affect_args



if __name__=="__main__":
	dyio = DyIO("COM3","74:F7:26:80:00:4F")
	# core = dyio.get_namespace(0)
	# print core.ping()
