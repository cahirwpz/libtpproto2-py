from types import *

class Structure(object):
	def __init__(self, name=None, longname="", description="", example="", **kw):
		if name is None:
			raise ValueError("Name did not exist!")
		
		self.name = name
		self.longname = longname
		self.description = description
		self.example = example
	
	def check(self, value):
		"""\
		check(value) -> None

		This function will check if an argument is valid for this structure.
		If the argument is not valid it should throw a ValueError exception.
		"""
		raise SyntaxError("Not Implimented")

	def length(self, value):
		"""\
		length(value) -> int

		This function will return the length (number of bytes) of the encoded
		version of the value.
		"""
		raise SyntaxError("Not Implimented")

	def xstruct(self):
		"""\
		xstruct() -> string

		Returns the xstruct value for this structure.
		"""
		raise SyntaxError("Not Implimented")
	xstruct = property(xstruct)

	def __str__(self):
		return "<%s %s %s>" % (self.__class__.__name__.split('.')[-1], hex(id(self)), self.name)
	__repr__ = __str__

	def __set__(self, obj, value):
		self.check(value)
		setattr(obj, "__"+self.name, value)

	def __get__(self, obj, objcls):
		try:
			return getattr(obj, "__"+self.name)
		except AttributeError, e:
			raise AttributeError("No value defined for %s" % self.name)

	def __delete__(self, obj):
		delattr(obj, "__"+self.name)

class StringStructure(Structure):
	def check(self, value):
		if not isinstance(value, StringTypes):
			raise ValueError("Value must be a string type")

	def length(self, value):
		return 4+len(value)

	xstruct = 'S'

class StringStructureTest(object):
	def test(self):
		class StringObject(object):
			s = StringStructure('s')
		
		str = StringObject()
		# Check that the default value is empty
		try:
			str.s
			assert False
		except AttributeError, e:
			pass

		# Check assignment is a value
		str.s = "test"
		assert str.s == "test"

		# Check the length
		assert StringObject.s.length(str.s) == 8

		# Check that you can't assign crap values
		for crap in [1, 6L, [], (), str]:
			try:
				str.s = crap
				assert False, "Was able to assign %r to a string attribute!" % crap
			except TypeError, e:
				pass

class CharacterStructure(StringStructure):
	def __init__(self, *args, **kw):
		Structure.__init__(self, *args, **kw)

		if kw.has_key('size'):
			self.size = kw['size']
		else:
			self.size = 1
	
	def check(self, value):
		StringStructure.check(self, value)
		if len(value) != self.size:
			raise ValueError("Value is not the correct size! Must be length %i" % self.size)
			
	def length(self, value):
		return self.size
	
	def xstruct(self):
		if self.size == 1:
			return 'c'
		return str(self.size)+'s'
	xstruct = property(xstruct)

class IntegerStructure(Structure):
	sizes = {
		8: ('b', 'B', None), 
		16: ('h', 'H', 'n'),
		32: ('i', 'I', 'j'),
		64: ('q', 'Q', 'p'),
	}
	
	def __init__(self, *args, **kw):
		Structure.__init__(self, *args, **kw)

		if kw.has_key('size'):
			size = kw['size']
		else:
			size = 32
		
		if kw.has_key('type'):
			type = kw['type']
		else:
			type = 'signed'
		
		if not size in self.sizes.keys():
			raise ValueError("Only supported sizes are %r not %i" % (self.sizes.keys(),size))
		self.size = size

		if not type in ("signed", "unsigned", "semisigned"):
			raise ValueError("Type can only be signed, unsigned or semisigned")
		self.type = type

	def check(self, value):
		if not isinstance(value, (IntType, LongType)):
			raise ValueError("Value (%s) must be a number" % value)

		# Do a bounds check now
		if self.type == "signed":
			max = 2**(self.size-1)-1
			min = -2**(self.size-1)
		elif self.type == "unsigned":
			max = 2**self.size-1
			min = 0
		elif self.type == "semisigned":
			max = 2**self.size-2
			min = -1

		if value < min:
			raise ValueError("Value is too small! Must be bigger then %i" % min)
		
		if value > max:
			raise ValueError("Value is too big! Must be smaller then %i" % max)
			
	def length(self, value):
		return self.size / 8

	def xstruct(self):
		if self.type == "signed":
			xstruct = self.sizes[self.size][0]
		elif self.type == "unsigned":
			xstruct = self.sizes[self.size][1]
		elif type == "semesigned":
			xstruct = self.sizes[self.size][2]
		return xstruct
	xstruct = property(xstruct)

import time
from datetime import datetime
class DateTimeStructure(Structure):
	sizes = {
		32: ('t'),
		64: ('T'),
	}

	def __init__(self, *args, **kw):
		Structure.__init__(self, *args, **kw)
		if kw.has_key('size'):
			size = kw['size']
		else:
			size = 64
		
		if not size in self.sizes.keys():
			raise ValueError("Only supported sizes are %r not %i" % (self.sizes.keys(),size))
		self.size = size
	
	def check(self, value):
		if not isinstance(value, datetime):
			raise ValueError("Value must be a datetime")

		i = time.mktime(value.timetuple())
		if i < 0:
			raise ValueError("Value is too small! Must be bigger then %i" % min)
		
		if i > 2**self.size-1:
			raise ValueError("Value is too big! Must be smaller then %i" % max)
	
	def length(self, value):
		return self.size / 8
	
	def xstruct(self):
		xstruct = self.sizes[self.size][0]
	xstruct = property(xstruct)

class EnumerationStructure(IntegerStructure):
	def __init__(self, *args, **kw):
		IntegerStructure.__init__(self, *args, **kw)

		if kw.has_key('values'):
			values = kw['values']

			for id, name in self.values.items():
				try:
					IntegerStructure.check(self, id)
				except ValueError, e:
					raise ValueError("Id's %i doesn't meet the requirements %s" % (type(id), e))

				if not isinstance(value, StringTypes):
					raise ValueError("Name of %i must be a string!" % id)
		
	def check(self, value):
		if isinstance(value, (IntType, LongType)):
			if value in self.values.keys():
				return	

		if isinstance(value, StringTypes):
			if value in self.values.values():
				return	

		raise ValueError("Value must be a number")

			
	def length(self, value):
		return self.size / 8

	def xstruct(self):
		if self.type == "signed":
			xstruct = self.sizes[self.size][0]
		elif self.type == "unsigned":
			xstruct = self.sizes[self.size][1]
		elif type == "semesigned":
			xstruct = self.sizes[self.size][2]
		return xstruct
	xstruct = property(xstruct)

class GroupStructure(Structure):
	class GroupProxy(object):
		def __init__(self, group, obj, objcls):
			self.group  = group
			self.obj    = obj
			self.objcls = objcls

		def __eq__(self, other):
			l = []
			for i, structure in enumerate(self.group.structures):
				l.append(self[i])
			return l == other

		def __getitem__(self, position):
			return self.group.structures[position].__get__(self.obj, self.objcls)

		def __setitem__(self, position, value):
			return self.group.structures[position].__set__(self.obj, value)
	
		def __delitem__(self, position):
			return self.group.structures[position].__delete__(self.obj)

		def __getattr__(self, name):
			for i, structure in enumerate(self.group.structures):
				if structure.name == "__%s_%s" % (self.group.name, name):
					return self[i]
			raise AttributeError("No such attribute %s" % name)

		def __setattr__(self, name, value):
			if name in ("group", "obj", "objcls"):
				object.__setattr__(self, name, value)
			else:
				for i, structure in enumerate(self.group.structures):
					if structure.name == "__%s_%s" % (self.group.name, name):
						self[i] = value
						return
				raise AttributeError("No such attribute %s" % name)
		def __delattr__(self, name):
			for i, structure in enumerate(self.group.structures):
				if structure.name == name:
					del self[i]
					return
			raise AttributeError("No such attribute %s" % name)
	
	def __init__(self, *args, **kw):
		Structure.__init__(self, *args, **kw)

		if kw.has_key('structures'):
			structures = kw['structures']
		else:
			structures = []
		
		if not isinstance(structures, (TupleType, ListType)):
			raise ValueError("Argument must be a list or tuple")

		for structure in structures:
			if not isinstance(structure, Structure):
				raise ValueError("All values in the list must be structures!")

			# Rewrite the names so they don't clash
			structure.name = "__%s_%s" % (self.name, structure.name)

		self.structures = structures

	def check(self, values, checkall=True):
		if not isinstance(values, (TupleType, ListType)):
			raise ValueError("Value must be a list or tuple")
		
		if len(values) != len(self.structures):
			raise ValueError("Value is not the correct size, was %i must be %i" % (len(list), len(self.structures)))

		if checkall:
			for i in xrange(0, len(self.structures)):
				self.structures[i].check(values[i])

	def length(self, list):
		length = 0
		for i in xrange(0, len(self.structures)):
			length += self.structures[i].length(item[i])
		return length
	
	def xstruct(self):
		for struct in self.structures:
			xstruct += struct.xstruct
	xstruct = property(xstruct)

	def __set__(self, obj, value):
		self.check(value, False)
		value = list(value)
		for structure in self.structures:
			structure.__set__(obj, value.pop(0))

	def __get__(self, obj, objcls):
		return self.GroupProxy(self, obj, objcls)

	def __del__(self, obj):
		for structure in self.structures:
			structures.__del__(obj)

class ListStructure(GroupStructure):
	def check(self, list):
		if not isinstance(list, (TupleType, ListType)):
			raise ValueError("Value must be a list or tuple")
		
		for item in list:
			if len(self.structures) != 1:
				if not isinstance(item, (TupleType, ListType)):
					raise ValueError("Value items must be a list or tuple not %r" % type(item))

				if len(item) != len(self.structures):
					raise ValueError("Value item was not the correct size (was %i must be %i)" % (len(item), len(self.structures)))
			
				for i in xrange(0, len(self.structures)):
					self.structures[i].check(item[i])
			else:
				self.structures[0].check(item)
	
	def length(self, list):
		length = 4
		for item in list:
			if len(self.structures) != 1:
				for i in xrange(0, len(self.structures)):
					length += self.structures[i].length(item[i])
			else:
				length += self.structures[0].check(item)
		return length

	def xstruct(self):
		xstruct = "["
		for struct in self.structures:
			xstruct += struct.xstruct
		return xstruct+"]"
	xstruct = property(xstruct)

String 		= StringStructure
Character	= CharacterStructure
Integer		= IntegerStructure
DateTime	= DateTimeStructure
Enumeration	= EnumerationStructure
Group		= GroupStructure
List		= ListStructure

__all__ = ["StringStructure", "CharacterStructure", "IntegerStructure", "DateTimeStructure", "GroupStructure", "ListStructure"]

if __name__ == "__main__":

	class Test(object):
		test = StringStructure("test")

		pos = GroupStructure("pos", structures=[IntegerStructure("x"), IntegerStructure("y")])

	t = Test()

	t.test = "Testing"
	print t.test
	del t.test
	try:
		print t.test
		assert False
	except Exception, e:
		print e
	try:
		t.test = 12
		assert False
	except Exception, e:
		print e

	t.test = "test"
	print t.test

	t.pos = [10, 11]
	assert t.pos == [10, 11]
	assert t.pos[0] == 10
	assert t.pos[1] == 11
	assert t.pos.x == 10
	assert t.pos.y == 11

	t.pos.x = 12
	assert t.pos == [12, 11]
	assert t.pos[0] == 12
	assert t.pos[1] == 11
	assert t.pos.x == 12
	assert t.pos.y == 11

	t.pos.y = 13
	assert t.pos == [12, 13]
	assert t.pos[0] == 12
	assert t.pos[1] == 13
	assert t.pos.x == 12
	assert t.pos.y == 13

