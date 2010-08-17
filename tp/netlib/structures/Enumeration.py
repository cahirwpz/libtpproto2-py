from types import StringTypes, IntType, LongType

from Integer import IntegerStructure

class EnumerationStructure(IntegerStructure):
	def __init__(self, *args, **kw):
		IntegerStructure.__init__(self, *args, **kw)

		if kw.has_key('values'):
			self.values = kw['values']

			for name, id in self.values.items():
				try:
					IntegerStructure.check(self, id)
				except ValueError, e:
					raise ValueError("Id's %s doesn't meet the requirements %s" % (name, e))

				if not isinstance(name, StringTypes):
					raise TypeError("Name of %i must be a string!" % id)

			self.keys = dict( (v,k) for k, v in self.values.items() )
		
	def check_and_fetch(self, value):
		if isinstance(value, (IntType, LongType)):
			if value in self.keys:
				return value
			else:
				raise ValueError("Number %s not in enumeration values." % value)

		elif isinstance(value, StringTypes):
			if value in self.values:
				return self.values[ value ]
			else:
				raise ValueError("String %s not in enumeration keys." % value)
		else:
			raise TypeError("Value must be an integer or string.")

	def check(self, value):
		self.check_and_fetch(value)

		return True

	def as_string(self, obj, objcls):
		try:
			return self.keys[ getattr(obj, "_"+self.name) ]
		except AttributeError, e:
			raise AttributeError("No value defined for %s" % self.name)

	def __set__(self, obj, value):
		setattr(obj, "_"+self.name, self.check_and_fetch(value))
