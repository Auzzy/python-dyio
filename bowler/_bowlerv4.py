from bowler import _DatagramBuilder,_DatagramParser

LENGTH = 12

class _Builder(_DatagramBuilder):
	@staticmethod
	def build(mac, func, args, priority, state, async, encrypted, ns):
		mac = mac.replace(':',' ')
		affect = priority << 3 | state << 2 | async << 1 | 0

		payload = _Builder._build_payload(ns,func,args)
		header = _Builder._build_header(mac,affect,encrypted,len(payload))

		return header + payload
	
	@staticmethod
	def _build_header(mac, affect, encrypted, payload_size):
		header = bytearray()
		header.append(0x4)
		header.extend(bytearray.fromhex(mac))
		header.append(affect)
		header.append(0x0)		# The 9th byte is a reserved byte
		header.append(encrypted)
		header.append(payload_size)
		header.append(sum(header) & 0x000000FF)
		return header

	@staticmethod
	def _build_payload(ns, func, args):
		func_bytes = bytearray(4-len(func)) + bytearray(func,"hex")
		arg_bytes = _Builder.args_to_bytes(args)
		if len(arg_bytes)>2:
			raise ValueError("The maximum argument length has been exceeded.")

		payload = bytearray()
		payload.append(ns)
		payload.extend(func_bytes)
		payload.extend(arg_bytes)
		payload.append(sum(payload) & 0x000000FF)
		return payload

class _DatagramParserV4(_DatagramParser):
	@staticmethod
	def parse(port, header):
		priority,state,async,dir,encrypted,length = _Parser._parse_header(header)
		
		func = bytearray(port.read(length))
		if not func:
			print "TIMEOUT"
			raise SerialTimeoutException("A timeout occurred while reading an incoming packet.")
		print "FUNC"
		for byte in func:
			print hex(byte)
		
		name,args = _Parser._parse_func(func)
		return name,args,priority,state,async,dir,encrypted

	@staticmethod
	def _parse_header(header):
		mac = header[1:7]
		affect = header[7]
		encrypted = header[9]
		payload_size = header[10]
		checksum = header[11]
		
		data_checksum = sum(header[:11]) & 0x000000FF
		if checksum!=data_checksum:
			raise IOError("The received data was corrupted.")
		
		priority = affect >> 3
		state = (affect >> 2) & 0x1
		async = (affect >> 1) & 0x1
		dir = affect & 0x1
		return priority,state,async,dir,encrypted,length

	@staticmethod
	def _parse_func(func):
		checksum = func.pop()
		ns = func[0]
		name = func[1:5]
		args = func[5:]
		
		data_checksum = sum(func) & 0x000000FF
		if checksum!=data_checksum:
			raise IOError("The received data was corrupted.")

		return name,args


def build(mac, func, args=[], priority=31, state=False, async=False, encrypted=False, ns=0x0):
	return _Builder.build(mac,func,args,priority,state,async,encrypted,ns)

# RETURN: func, args, priority, state, async, dir, encrypted
def parse(port, header):
	name,args,priority,state,async,dir,encrypted = _Parser.parse(port,header)
	return func,args,priority,state,async,dir,encrypted
