import re

import bowler

class Namespace(object):
	_ORG = "(.*?)"
	_LIB = "(.*?)(?:\.\*)?"
	_VER = "(\d*\.\d*)"
	_ID_RE = "{org}\.{lib};(?:{ver};)?;".format(org=_ORG,lib=_LIB,ver=_VER)

	def __init__(self, dyio, index):
		self._dyio = dyio
		self.index = index
		self.org,self.lib,self.ver,self.name = None,None,None,None
	
	@staticmethod
	def parse_id(id):
		match = re.match(Namespace._ID_RE,id)
		org,lib,ver = match.groups()
		name = "{org}.{lib}".format(org=org,lib=lib)
		return org,lib,ver,name
	
	def send(self, func, args=[], priority=32, state=False, async=False, encrypted=False):		
		datagram = bowler.build_datagram(self._dyio.mac,func,priority,state,async,encrypted,self.index,args)
		bowler.send_datagram(self._dyio.port,datagram)
	
	# RETURN: func, args, priority, state, async, dir, encrypted
	def receive(self):
		return bowler.receive_datagram(self._dyio.port)

class BcsCore(Namespace):
	def __init__(self, dyio):
		Namespace.__init__(self,dyio,0)

		id = self.get_namespace_id(0)
		self.org,self.lib,self.ver,self.name = Namespace.parse_id(id)

	def ping(self):
		self.send("_png")
		func,args,priority,state,async,dir,encrypted = self.receive()
		return True

	def count_namespaces(self):
		self.send("_nms")
		func,args,priority,state,async,dir,encrypted = self.receive()
		return bytes_to_int(args)

	def get_namespace_id(self, index):
		self.send("_nms",[index])
		func,args,priority,state,async,dir,encrypted = self.receive()
		return str(args)

def init_core(dyio):
	global core
	core = BcsCore(dyio)


# type("NAME", (Namespace,), {"__init__": lambda self,**kwargs: self.__dict__.update(kwargs)})

def count(dyio):
	return core.count_namespaces()

def _ns_to_class_name(ns):
	cls_name = ns[0].upper()
	index = 1
	old_index = 1
	while '.' in ns[old_index:]:
		index = ns.find('.',old_index)
		cls_name += ns[old_index:index] + ns[index+1].upper()
		old_index = index+2
	return cls_name + ns[old_index:]
	
def get(dyio, index):
	if index==0:
		return core
	else:
		def __init__(self, dyio, index):
			Namespace.__init__(self,dyio,index)
			self.org = org
			self.lib = lib
			self.ver = ver
			self.name = name
		
		funcs = {"__init__":__init__}

		ns_id = core.get_namespace_id(index)
		org,lib,ver,name = Namespace.parse_id(ns_id)
		cls_name = _ns_to_class_name(name)

		ns = type(cls_name, (Namespace,), funcs)
		return ns(dyio,index)


def bytes_to_int(bytearr):
	return int("".join(["{:0>2}".format(byte) for byte in bytearray(bytearr)]),16)
