from itertools import izip

class PacketMeta(type):
	@property
	def structures(cls):
		"""
		get_structures() -> [<structure>,]

		A list of structures. Cascades up the parent classes.

		For example,

		>>>class A:
		>>> __metaclass__ = PacketMeta
		>>>	pass
		>>>
		>>>A.structure = [1,]
		>>>
		>>>class B(A):
		>>>	pass
		>>>
		>>>B.structure = [2,]
		>>>
		>>>print B.structure
		[<structure 0x123456>, <structure 0x7890123>,]
		"""

		parent = cls.__bases__[0]
		r = []
		if parent != Packet:
			r += parent.structures
		if cls.__dict__.has_key('_structures'):
			r += cls._structures
		return r

	@structures.setter
	def structures(cls, value):
		cls._structures = value

	def __str__(self):
		return "<dynamic-class '%s' at %s>" % (self._name, hex(id(self)))

	__repr__ = __str__

class Packet(object):
	__metaclass__ = PacketMeta

	name = "Root Packet"

	def __init__(self, *args):
		self.structures = self.__class__.structures

		if len(args) == 0:
			return

		if len(args) < len(self.structures):
			raise ValueError("Not enough arguments given (received %s rather than %s)" % (len(args), len(self.structures)))
		
		# Check each argument is valid
		for structure, argument in izip(self.structures, args):
			structure.check(argument)
			structure.__set__(self, argument)
			setattr(self, structure.name, argument)

	@property
	def xstruct(self):
		xstruct = ""
		for structure in self.structures:
			xstruct += structure.xstruct
		print xstruct
		return xstruct
	
	def pack(self):
		return ''.join( s.pack(self) for s in self.structures )
	
	def unpack(self, string):
		for structure in self.structures:
			string = structure.unpack(self, string)
		return string
