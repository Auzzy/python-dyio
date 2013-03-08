VERSION = 3

class Affect(object):
	STATUS = 0x00
	GET = 0x10
	POST = 0x20
	CRIT = 0x30
	ASYNC = 0x40


class DatagramBuilder(object):
	@staticmethod
	def get(version):
		if version==3:
			return DatagramBuilderV3
		elif version==4:
			return DatagramBuilderV4
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

class DatagramBuilderV4(DatagramBuilder):
	@staticmethod
	def build(mac, func, priority, state, async, encrypted, ns, args=[]):
		mac = mac.replace(':',' ')
		affect = priority << 3 | state << 2 | async << 1 | 0

		payload = DatagramBuilderV4._build_payload(ns,func,args)
		header = DatagramBuilderV4._build_header(mac,affect,encrypted,len(payload))

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
		arg_bytes = DatagramBuilder.args_to_bytes(args)
		if len(arg_bytes)>2:
			raise ValueError("The maximum argument length has been exceeded.")

		payload = bytearray()
		payload.append(ns)
		payload.extend(func_bytes)
		payload.extend(arg_bytes)
		payload.append(sum(payload) & 0x000000FF)
		return payload

class DatagramBuilderV3(DatagramBuilder):
	@staticmethod
	def build(mac, func, priority, state, async, encrypted, ns, args=[]):
		mac = mac.replace(':',' ')
		affect = DatagramBuilderV3._get_affect(priority,state,async)

		payload = DatagramBuilderV3._build_payload(func,args)
		header = DatagramBuilderV3._build_header(mac,affect,ns,len(payload))
		
		return header + payload

	@staticmethod
	def _get_affect(priority, state, async):
		if priority==0:
			return Affect.CRIT
		elif state:
			return Affect.POST
		elif async:
			return Affect.ASYNC
		else:
			return Affect.GET

	@staticmethod
	def _build_header(mac, affect, ns, payload_size):
		header = bytearray()
		header.append(0x3)
		header.extend(bytearray.fromhex(mac))
		header.append(affect)
		header.append((ns << 1) | 0)
		header.append(payload_size)
		header.append(sum(header) & 0x000000FF)
		return header

	@staticmethod
	def _build_payload(func, args):
		func_bytes = bytearray(4-len(func)) + bytearray(func,"hex")
		arg_bytes = DatagramBuilder.args_to_bytes(args)

		payload = bytearray()
		payload.extend(func_bytes)
		payload.extend(arg_bytes)
		return payload

class DatagramParser(object):
	@staticmethod
	def get(port):
		version = bytearray(port.read())[0]
		if version==3:
			return DatagramParserV3
		elif version==4:
			return DatagramParserV4
		else:
			raise ValueError("Received a packet from an unknown version og the Bolwer protocol.")

class DatagramParserV4(DatagramParser):
	@staticmethod
	def parse(port):
		header = bytearray(port.read(11))
		length = DatagramParserV4._parse_header(header)
		func = bytearray(port.read(length))
		return DatagramParserV4._parse_func(func)

	@staticmethod
	def _parse_header(header):
		mac = header[0:6]
		affect = header[6]
		encrypted = header[8]
		payload_size = header[9]
		checksum = header[10]
		
		data_checksum = sum(bytearray([0x4]) + header[:10]) & 0x000000FF
		if checksum!=data_checksum:
			raise IOError("The received data was corrupted.")
		
		return length

	@staticmethod
	def _parse_func(func):
		ns = func[0]
		name = func[1:5]
		args = func[5:7]
		checksum = func[7]
		
		data_checksum = sum(func[:7]) & 0x000000FF
		if checksum!=data_checksum:
			raise IOError("The received data was corrupted.")

		return name,args

class DatagramParserV3(DatagramParser):
	@staticmethod
	def parse(port):
		header = bytearray(port.read(10))
		length = DatagramParserV3._parse_header(header)
		func = bytearray(port.read(length))
		return DatagramParserV3._parse_func(func)

	@staticmethod
	def _parse_header(header):
		mac = header[0:6]
		affect = header[6]
		ns = header[7]
		length = header[8]
		checksum = header[9]
		
		data_checksum = sum(bytearray([0x3]) + header[:9]) & 0x000000FF
		if checksum!=data_checksum:
			raise IOError("The received data was corrupted.")
		
		return length

	@staticmethod
	def _parse_func(func):
		return func[:4],func[4:]


# def build_datagram(mac, affect, ns, func, *args):
def build_datagram(mac, func, priority=32, state=False, async=False, encrypted=False, ns=0x0, args=[]):
	# ns = ns if ns else 0x0
	
	builder = DatagramBuilder.get(VERSION)
	# return builder.build(mac,affect,ns,func,*args)
	return builder.build(mac,func,priority,state,async,encrypted,ns,args=[])

def send_datagram(port, datagram):
	for byte in datagram:
		print hex(byte)

	port.write(datagram)
	port.flush()

def receive_datagram(port):
	parser = DatagramParser.get(port)
	return parser.parse(port)


# print int("".join(["{:0>2}".format(byte) for byte in bytearray(response)]),16)
