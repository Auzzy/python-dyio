from serial import SerialTimeoutException

_version = None
SUPPORTED_VERSIONS = (4,3)

def detect_version(dyio):
	global _version

	for ver in SUPPORTED_VERSIONS:
		if _detect_specific_version(dyio,ver):
			_version = ver
			break
	else:
		raise ValueError("Unsupported version detcted")
	
	return _version

def _detect_specific_version(dyio, ver):
	global _version
	_version = ver
	datagram = build_datagram(dyio.mac,"_png")
	send_datagram(dyio.port,datagram)
	try:
		receive_datagram(dyio.port)
		return True
	except SerialTimeoutException:
		return False

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
		version_data = port.read(1)
		if not version_data:
			raise SerialTimeoutException("A timeout occurred while waiting for an incoming packet.")

		version = bytearray(version_data)[0]
		lib = None
		if version==3:
			lib = _bowlerv3
		elif version==4:
			lib = _bowlerv4
		else:
			raise ValueError("Received a packet from an unimplemented version of the Bolwer protocol.")
		
		parser,length = lib.parse,lib.LENGTH
		header_data = port.read(length-1)
		if not header_data:
			raise SerialTimeoutException("A timeout occurred while waiting for an incoming packet.")
		
		return parser,(bytearray([version]) + header_data)

from bowler import _bowlerv3,_bowlerv4

Affect = _bowlerv3.Affect

def build_datagram(mac, func, args=[], priority=31, state=False, async=False, encrypted=False, ns=0x0):
	builder = _DatagramBuilder.get(_version)
	return builder(mac,func,args,priority,state,async,encrypted,ns)

def send_datagram(port, datagram):
	port.write(datagram)
	port.flush()

def receive_datagram(port):
	parser,header = _DatagramParser.get(port)
	return parser(port,header)
