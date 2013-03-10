from bowler import _DatagramBuilder,_DatagramParser

class Affect(object):
	STATUS = 0x00
	GET = 0x10
	POST = 0x20
	CRIT = 0x30
	ASYNC = 0x40

class _Builder(_DatagramBuilder):
	@staticmethod
	def build(mac, func, args, affect, ns):
		mac = mac.replace(':',' ')

		payload = _Builder._build_payload(func,args)
		header = _Builder._build_header(mac,affect,ns,len(payload))
		
		return header + payload

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
		arg_bytes = _Builder.args_to_bytes(args)

		payload = bytearray()
		payload.extend(func_bytes)
		payload.extend(arg_bytes)
		return payload

class _Parser(_DatagramParser):
	@staticmethod
	def parse(port):
		header = bytearray(port.read(10))
		affect,dir,length = _Parser._parse_header(header)
		func = bytearray(port.read(length))
		name,args = _Parser._parse_func(func)
		return name,args,affect,dir

	@staticmethod
	def _parse_header(header):
		mac = header[0:6]
		affect = header[6]
		ns = header[7] >> 1
		dir = header[7] & 0x1
		length = header[8]
		checksum = header[9]
		
		data_checksum = 3+sum(header[:9]) & 0x000000FF
		if checksum!=data_checksum:
			raise IOError("The received data was corrupted.")
		
		return affect,dir,length

	@staticmethod
	def _parse_func(func):
		return func[:4],func[4:]

def _get_affect(priority, state, async):
	if priority==0:
		return Affect.CRIT
	elif state:
		return Affect.POST
	elif async:
		return Affect.ASYNC
	else:
		return Affect.GET

def _unpack_affect(affect):
	if affect==Affect.CRIT:
		return 0,False,False
	elif affect==Affect.POST:
		return 32,True,False
	elif affect==Affect.ASYNC:
		return 32,False,True
	else:
		return 32,False,False


def build(mac, func, priority=32, state=False, async=False, encrypted=False, ns=0x0, args=[]):
	affect = _get_affect(priority,state,async)
	return _Builder.build(mac,func,args,affect,ns)

# RETURN: func, args, priority, state, async, dir, encrypted
def parse(port):
	func,args,affect,dir = _Parser.parse(port)
	priority,state,async = _unpack_affect(affect)
	return func,args,priority,state,async,dir,False

