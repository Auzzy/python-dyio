import struct
from serial import Serial
import re

import bowler

class DyIO(object):
	def __init__(self, port, mac):
		if isinstance(port,Serial):
			self.port = port
			if not self.port.isOpen():
				self.port.open()
		else:
			self.port = Serial(port=port, baudrate=115200)
		
		self.mac = self._normalize_mac(mac)
	
	def _normalize_mac(self, mac):
		if isinstance(mac,(list,tuple)):
			return ':'.join(["{:>2x}".format(byte) for byte in mac])
		else:
			if not ((':' in mac) ^ ('-' in mac) ^ (' ' in mac)):
				raise ValueError("Invalid MAC address presented: non-uniform delimiters.")

			return re.sub("[- ]", ':', mac)
	
	def get_namespaces(self):
		pass

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

	def exec_command(self, func, priority=32, state=False, async=False, encrypted=False, ns=0x0, args=[]):
		ns = ns if ns else 0x0
		
		# datagram = bowler.build_datagram(self.mac,affect,ns,name,*args)
		datagram = bowler.build_datagram(self.mac,func,priority,state,async,encrypted,ns,args)
		bowler.send_datagram(self.port,datagram)
	
	def receive(self):
		name,args = bowler.receive_datagram(self.port)
		return args


def bytes_to_int(bytearr):
	return int("".join(["{:0>2}".format(byte) for byte in bytearray(bytearr)]),16)

def exec_command(dyio, func, affect, encrypted=False, ns=0x0, args=[]):
	affect_args = DyIO._get_affect_args(affect)
	return dyio.exec_command(func,encrypted=encrypted,ns=ns,args=args,**affect_args)

if __name__=="__main__":
	dyio = DyIO("COM3","74:F7:26:80:00:4F")
	exec_command(dyio,"_nms",bowler.Affect.GET)

	response = dyio.receive()
	print "\nRESPONSE"
	for byte in response:
		print hex(byte)
	print
