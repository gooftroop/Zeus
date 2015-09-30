# -*- coding: utf-8 -*-
# 
# Use sqlalchemy.
# Supports:
# Drizzle
# Microsoft SQL Server
# MySQL
# Oracle
# PostgreSQL
# SQLite
# Sybase
# 
# Users should extend sql.py to create "ORM/RDB models". The models will be responsible for providing the 
# custom fields, while sql.py will be responsible for providing the interface to actually interact with the RDB
# 
# Say our mysql DB has a table Users
# I'd like to be able to do something like (assuming we defined a table in the DB as 'Users'):
# import sql
# 
# db = SQL(connection_uri="snowflake.db")
# users = db.Users.get()
# 
# or:
# 
# db.Users.create("admin", password="123", email="admin@snowflake.com")
# 

from dao import DAO
from sqlalchemy import (create_engine, event)
from sqlalchemy.engine import (reflection)
from sqlalchemy.orm import (sessionmaker)

CONNECTION_URI_DELIM = ":///"


class Model(DAO):
	"""
	"""

	def __init__(self, table, engine):

		if not table:
			raise IllegalArgumentException("Table is required")

		if not engine:
			raise IllegalArgumentException("Engine is required")

		super(SQL, self).__init__(self)
		self.Session = None
		self._table = table
		self._session_factory = sessionmaker(bind=self._engine, autoflush=autoflush)


class SQL(object):
	"""
	"""

	# We need database url
	# allow to get table?
	# ok, so we can do this two ways --> either its a sql.py instance per table, 
	# or we allow access via getters/setters with the additional parameter of table
	def __init__(self, dbtype="mysql", connection_uri=None, logging=True, autoflush=True):
		"""
		"""

		if not connection_uri:
			raise IllegalArgumentException("The database connection URI is required")

		super(SQL, self).__init__(self)
		
		self._connection_uri = connection_uri
		self._dbtype = dbtype
		self._engine = create_engine(dbtype + CONNECTION_URI_DELIM + connection_uri, echo=logging)
		self._meta = MetaData()

		self._meta.reflect(bind=self._engine)
		for name, table in self._meta.tables:
			self._models[name] = Model(table, self._engine)

	def __getattr__(self, name):
		try:
			return self._models[name]
		except KeyError:
			msg = "'{0}' object has no attribute '{1}'"
        	raise AttributeError(msg.format(type(self).__name__, name))

    def __setattr__(self, name, value):
    	self.new(name, value)

    def __delattr__(self, name):
    	self.delete(name)


	###########################################################################
	# RDM Specific functionality
	###########################################################################
	
	def listen(target, event, callback):
		event.listen(target, event, callback)
	

	###########################################################################
	# Override Object behavior
	###########################################################################

	def new(self, name, value):
		pass

	def delete(self, name):
		pass
	
