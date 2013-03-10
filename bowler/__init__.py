version = 3

def detect_version(port):
	global version
	version = 3

class _DatagramBuilder(object):
	@staticmethod
	def get(version):
		if version==3:
			return _bowlerv3.build
		elif version==4:
			return _bowlerv4.build
		else:
			raise ValueError("Trying to build a packet for an unknown version.")
	
	@staticmethod
	def args_to_bytes(args):
		args_bytes = bytearray()
		for arg in args:
			if isinstance(arg,int):
				arg_rev = hex(arg)[2:][::-1]
				int_bytes = [int(arg_rev[index:index+2],16) for index in range(0,len(arg_rev),2)][::-1]
				args_bytes.extend(int_bytes)
			elif isinstance(arg,str):
				args_bytes.extend(bytearray(str(arg)))
		return args_bytes

class _DatagramParser(object):
	@staticmethod
	def get(port):
		print port.inWaiting()
		version = bytearray(port.read(1))[0]
		if version==3:
			return _bowlerv3.parse
		elif version==4:
			return _bowlerv4.parse
		else:
			raise ValueError("Received a packet from an unimplemented version of the Bolwer protocol.")
			
from bowler import _bowlerv3,_bowlerv4

Affect = _bowlerv3.Affect

def build_datagram(mac, func, priority=32, state=False, async=False, encrypted=False, ns=0x0, args=[]):
	builder = _DatagramBuilder.get(version)
	return builder(mac,func,priority,state,async,encrypted,ns,args)

def send_datagram(port, datagram):
	port.write(datagram)
	port.flush()

def receive_datagram(port):
	parser = _DatagramParser.get(port)
	return parser(port)
