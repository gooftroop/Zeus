# -*- coding: utf-8 -*-

# Base dao for this app
# Provide the core api for working with data sources
# Also, the DAO object should act as a proxy for interacting with a DAO in a 
# pythonic manner - that is, provide a polymorphic API for python internal
# attribtue and container methods 

from exceptions import (IllegalStateException, IllegalArgumentException) # TODO implement these


class DAO(object):
	"""
	"""

	def __init__(self):
		"""
		"""

		self._models = {}

	###########################################################################
	# Instance functionality
	###########################################################################
	
	def destroy(self):
		pass

	def to_string(self):
		pass

	def model_names(self):
		return self._models.keys()

	@property	
	def models(self):
		return self._models

	###########################################################################
	# Transactional API
	###########################################################################
	
	def new(self):
		# create a new model (i.e. Table, etc.)
		pass

	def close(self):
		pass

	def invalidate(self):
		pass

	def begin(self):
		pass

	def commit(self):
		pass

	def flush(self):
		pass

	def cancel(self):
		pass

	def rollback(self):
		pass

	###########################################################################
	# Data Access APIs
	###########################################################################
	
	def get(self, key, *args, **kwargs):
		pass

	def create(self, key, value, *args, **kwargs):
		pass

	def update(self, key, value, *args, **kwargs):
		pass

	def replace(self, key, value, *args, **kwargs):
		pass

	def delete(self, key, value, *args, **kwargs):
		pass

	###########################################################################
	# Data Set operations
	###########################################################################
	
	def add(self, other):
		pass 

	def sub(self, other):
		pass 

	def mul(self, other):
		pass 

	def div(self, other):
		pass 

	def AND(self, other):
		pass 

	def OR(self, other):
		pass 

	def XOR(self, other):
		pass

	def invert(self, other):
		# Complement
		pass

	###########################################################################
	# Container operations
	###########################################################################
	
	def size(self):
		pass

	def has(self, key):
		pass

	def reversed(self):
		pass

	def defaults(self, key):
		pass

	def iterator(self):
		pass

	###########################################################################
	# Private functions
	# Top-level implementations should not have to worry about these methods
	# DAO does some simple rerouting of python internal methods to allow
	# implementations to easily alter data access behavior.
	###########################################################################

	# __del__ is called when the instance is about to be destroyed.
	# This method should be responsible for safe cleanup
	def __del__(self):
		self.destroy()

	# Custom defined human-readable string description of this object
	# Implementing this method is optional
	def __str__(self):
		self.to_string()

	# Define attribtue access against the data source	
	def __getattribute__(self, name):
		try:
			return self.get(key)
		except KeyError:
			return self.__missing__(key)

	def __setattr__(self, name, value):
		if not self._contains(key):
			return self.create(key, value)
		else:
			return self.update(key, value)

	def __delattr__(self, name):
		return self.delete(key)
	
	# Emulate container types.
	# We should allow data source access to be operated upon as if they were
	# as set, list, etc. 
	def __getitem__(self, key):
		try:
			return self.get(key)
		except KeyError:
			return self.__missing__(key)

	def __setitem__(self, key, value):
		if not self._contains(key):
			return self.create(key, value)
		else:
			return self.update(key, value)

	def __len__(self):
		return self.size()

	def __iter__(self):
		return self.iterator()

	def __contains__(self, key):
		return self.has(key)

	def __reversed__(self):
		return self.reversed()

	def __missing__(self, key):
		return self.defaults(key)

	# We assume that models is a set or multiset of data.
	# Let's expose set operations so that implementors can interact with data 
	# sources as if they were sets. The data-source-sepcific dao should then 
	# implement the appropriate functions and return the correct model/data. 
	# For example:
	#   Add: two ORM models should do a full join
	def __add__(self, other):
		return self.add(other)

	def __sub__(self, other):
		return self.sub(other)

	def __mul__(self, other):
		return self.mul(other)

	def __div__(self, other):
		return self.div(other)

	def __and__(self, other):
		return self.AND(other)

	def __xor__(self, other):
		return self.XOR(other)

	def __or__(self, other):
		return self.OR(other)

	def __invert__(self):
		return self.invert(other)

