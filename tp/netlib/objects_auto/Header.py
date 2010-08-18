from Packet import Packet
from tp.netlib import structures

class Header( Packet ):
	name = "Header"
	_structures = [
		structures.CharacterStructure("version", "Protocol Version", size=4),
		structures.IntegerStructure("sequence",  "Sequence Number",  size=32, type="unsigned"),
		structures.IntegerStructure("type",      "Packet Type",      size=32, type="unsigned"),
		structures.IntegerStructure("length",    "Length of Packet", size=32, type="unsigned"),
	]

	def __init__(self, *args, **kwargs):
		if len(args) == 0:
			Packet.__init__(self)
		else:
			Packet.__init__(self, self.VERSION, args[0], self.__class__._id, 0, *args[1:], **kwargs)
	
	@property
	def _length(self):
		return sum( s.length( getattr(self, s.name) ) for s in self.structures if s not in Header._structures)

	@_length.setter
	def _length(self, value):
		pass

class HeaderFactory( object ):
	@staticmethod
	def makeHeader( version ):
		class HeaderWithVersion( Header ):
			VERSION = version

		return HeaderWithVersion
