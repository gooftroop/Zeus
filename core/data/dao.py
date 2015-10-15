# -*- coding: utf-8 -*-

# Base dao for this app
# Provide the core api for working with data sources
# Also, the DAO object should act as a proxy for interacting with a DAO in a 
# pythonic manner - that is, provide a polymorphic API for python internal
# attribtue and container methods 

import tornado.gen as gen

from exceptions import (IllegalStateException, IllegalArgumentException, TransactorException, DAOException) # TODO implement these


class Transactor(object):
	"""
	"""

	# TODO allow for Transactor reuse opaquely

	def __init__(self):
		self._models = {}
		self._session = None

	###########################################################################
	# Primary Transactor Methods
	###########################################################################

	def new(self, name, value):
		pass

	def delete(self, name):
		pass

	def destroy(self):
		pass

	def to_string(self):
		pass

	def session(self):
		pass

	def refresh(self):
		pass

	def model_names(self):
		return self._models.keys()

	# TODO should we care about multi session for a transactor? How do we want
	# to work with 'unit of work'? If we want to do multi session, then the
	# Transactional API methods will not work
	def session(self):
		"""
		Entry point for this Transactor. All operations done on a Model should
		be done in the scope of this method. 

		with db.session() as s:
        	db.Users.get("admin")
		"""
		self._session = self.begin()
		try:
			yield self._session
			self._session.commit()
		except Exception as e: # TDOD placeholder - Catch specific exceptions
			self._session.rollback()
			raise TransactorException(e)
		finally:
			self.close()

	@property	
	def models(self):
		return self._models

	###########################################################################
	# Session API
	###########################################################################

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
	# Private Methods
	###########################################################################
	
	# __del__ is called when the instance is about to be destroyed.
	# This method should be responsible for safe cleanup
	def __del__(self):
		self.destroy()

	# Custom defined human-readable string description of this object
	# Implementing this method is optional
	def __str__(self):
		self.to_string()

	def __getattr__(self, name):
		try:
			model = self._models[name]
			model.bind(self._session)
			yield model
			model.unbind()
		except KeyError:
			msg = "'{0}' object has no attribute '{1}'"
        	raise TransactorException(msg.format(type(self).__name__, name))

    def __setattr__(self, name, value):
    	self.new(name, value)

    def __delattr__(self, name):
    	self.delete(name)


class DAO(object):
	"""
	"""

	def __init__(self):
		pass

	###########################################################################
	# Instance functionality
	###########################################################################
	
	def destroy(self):
		pass

	def to_string(self):
		pass

	def bind(self, session=None):
		if not session:
			raise IllegalArgumentException("'session' is required")
		self._session = session

	def unbind(self):
		self._session = None

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
	# Data Set Operations
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
	# Container Operations
	###########################################################################
	
	def size(self):
		pass

	def contains(self, key):
		pass

	def reversed(self):
		pass

	def defaults(self, key):
		pass

	def iterator(self):
		pass

	###########################################################################
	# Private Methods
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
		return self.contains(key)

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

