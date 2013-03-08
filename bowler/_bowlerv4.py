from bowler import _DatagramBuilder,_DatagramParser

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
		header.append(bytearray())	# The 9th byte is a reserved byte
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
	def parse(port):
		header = bytearray(port.read(11))
		priority,state,async,dir,encrypted,length = _Parser._parse_header(header)
		func = bytearray(port.read(length))
		name,args = _Parser._parse_func(func)
		return name,args,priority,state,async,dir,encrypted

	@staticmethod
	def _parse_header(header):
		mac = header[0:6]
		affect = header[6]
		encrypted = header[8]
		payload_size = header[9]
		checksum = header[10]
		
		data_checksum = 4+sum(header[:10]) & 0x000000FF
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


def build(mac, func, priority=32, state=False, async=False, encrypted=False, ns=0x0, args=[]):
	return _Builder.build(mac,func,args,priority,state,async,encrypted,ns)

# RETURN: func, args, priority, state, async, dir, encrypted
def parse(port):
	name,args,priority,state,async,dir,encrypted = _Parser.parse(port)
	return func,args,priority,state,async,dir,encrypted
