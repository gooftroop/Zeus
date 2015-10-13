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
	Wrapper object to adapt data source model for use with a Transactor
	"""

	_get_mapper = dict(all="all", first="first", one="one")

	def __init__(self, table):

		if not table:
			raise IllegalArgumentException("Table is required")

		super(Model, self).__init__(self)
		self.table = table
		self._session = None

	###########################################################################
	# Instance functionality
	# 
	# The following methods provide an interface/proxy to the current Session
	###########################################################################
	
	def destroy(self):
		this.unbind()
		# TODO Any additional cleanup on the table? Drop the table from the session?

	def to_string(self):
		# Hmmmm.....
		pass

	###########################################################################
	# Data Access APIs
	###########################################################################
	
	# TODO use the current bind(session) schema, or require that session be passed in?
	def get(self, name, method, **kwargs):
		# Gets a row from the table
		# TODO 
		# - if name is not specified - don't error out => just don't use .get()
		# - allow distinct?
		# - one_or_none?
		# - first?
		# - as_scalar (or scalar)?
		# - order_by?
		
		_distinct = kwargs.pop("distict", None)
		_order_by = kwargs.pop("order_by", False)
		_group_by = kwargs.pop("group_by", None)
		_having = kwargs.pop("having", None)
		_limit = kwargs.pop("limit", None)
		_ret = self.session.query(self)
		if name:
			_ret = _ret.get(name)

		if _distinct is not None:
			_ret = _ret.distict()

		if _group_by is not None:
			_ret = _ret.group_by(_group_by)
			if _having is not None:
				_ret = _ret.having(_having)

		if _limit is not None:
			_ret = _ret.limit(_limit)

		_ret.filter_by(kwargs).order_by(_order_by)

		if not method or method == "raw":
			return _ret

		return getattr(_ret, self._get_mapper(method))()

	def create(self, **kwargs):
		# Creates a new row
		# This...I'm strugglebus with. Session doesn't actually expose a way to 
		# insert into a table. We can use .add, but since our Tables are generated
		# dynamically, this proves to be difficult (maybe impossible). Accessing
		# Table might work, but the API is not particularly clear
		if not name:
			raise IllegalArgumentException("'name' is required. Name is the identifier (or primary key) of the row to" +
										   "create")
		_warn = kwargs.pop("_warn", True)
		_new = self.table(kwargs)
		self.session.add(_new)

	def update(self, name, values, **kwargs):
		# Updates a new row with the specified content

		if not values:
			raise IllegalArgumentException("'values' are required")

		_sync_stratey = kwargs.pop("synchronize_session", "evaluate")
		_update_args = kwargs.pop("update_args", None)

		_ret = self.session.query(self)
		if name:
			_ret = _ret.get(name)

		_ret.filter_by(kwargs)
			.update(values, synchronize_session=_sync_stratey, update_args=_update_args)

	def replace(self, name, values, **kwargs):
		# Replace is semantically no different than update in SQLAlchemy
		self.update(name, values, **kwargs)

	def delete(self, name, **kwargs):
		# Deletes rows matched by a query
		# TODO do we need to consider session.expunge?

		_sync_stratey = kwargs.pop("synchronize_session", "evaluate")
		_ret = self.session.query(self)
		if name:
			_ret = _ret.get(name)

		_ret.filter_by(kwargs)
			.delete(synchronize_session=_sync_stratey)

	# Special case?
	def expand(self):
		# Adds a new column to this table
		# args:
		pass

	def contrain(self):
		# Adds a new constraint to this table
		# args:
		pass

	def join(self):
		# Performs the specified join
		# args:
		pass

	###########################################################################
	# Data Set operations
	###########################################################################
	
	# If operations are being done on the same Table, then do nothing
	# If operations are being done against other Tables, then perform joins
	# Otherwise, then use union, intersection, etc.
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

	def contains(self, key):
		pass

	def reversed(self):
		pass

	def defaults(self, key):
		pass

	def iterator(self):
		pass


class SQL(Transactor):
	"""
	"""

	def __init__(self, dbtype="mysql", connection_uri=None, logging=True, autoflush=True):
		"""
		"""

		# TODO allow load of table via name from the table or by a model defined elsewhere (via configuration)

		if not connection_uri:
			raise IllegalArgumentException("The database connection URI is required")

		super(SQL, self).__init__(self)

		self._connection_uri = connection_uri
		self._dbtype = dbtype
		self._engine = create_engine(dbtype + CONNECTION_URI_DELIM + connection_uri, echo=logging)
		self._meta = MetaData()

		self.refresh()

	###########################################################################
	# SQLAlchemy Specific functionality
	###########################################################################
	
	def on(target, event, callback, retval=False):
		if not target:
			raise IllegalArgumentException("'target' is requried")

		if not event:
			raise IllegalArgumentException("'event' is requried")

		if not callback:
			raise IllegalArgumentException("'callback' is requried")

		event.listen(target, event, callback, retval=retval)

	def off(target, event, callback):
		if not target:
			raise IllegalArgumentException("'target' is requried")

		if not event:
			raise IllegalArgumentException("'event' is requried")

		if not callback:
			raise IllegalArgumentException("'callback' is requried")

		event.remove(targe, event, callback)

	def registered(target, event, callback):
		if not target:
			raise IllegalArgumentException("'target' is requried")

		if not event:
			raise IllegalArgumentException("'event' is requried")

		if not callback:
			raise IllegalArgumentException("'callback' is requried")

		event.remove(targe, event, callback)
	
	###########################################################################
	# Override Object behavior
	###########################################################################

	def new(self, name, value):
		# Create new Table
		pass

	def delete(self, name):
		# Delete Table
		pass

	def destroy(self):
		# Clean up self
		self.close()

	def to_string(self):
		return "SQL Transactor {0}".format(self.model_names())

	def refresh(self, schema=None, views=False, only=None, extend_existing=False, 
				autoload_replace=True, **dialect_kwargs):

		self._meta.reflect(bind=self._engine, schema=schema, views=views, only=only, 
						   extend_existing=extend_existing, autoload_replace=autoload_replace, 
						   **dialect_kwargs)

		for name, table in self._meta.tables:
			if not hasattr(self._models, name):
				self._models[name] = Model(table, self._engine)

	# TODO Question - right now we expose (the) Session object. To use it, 
	# actors must know about SQLAlchemy's API for the Session. Is there value
	# in consolidating the Session API into this API?

	###########################################################################
	# Transactional API
	###########################################################################

	def close(self):
		if self._session:
			self._session.close()
			self._session = None

	def invalidate(self):
		# Useful for calls in except statements
		if self._session:
			self._session.invalidate()

	def begin(self):
		return (self._session = self._session_factory()) if not self._session else self._session

	def tag(self):
		if not self._session:
			raise IllegalStateException("No Session to tag. You must begin a Session prior to tagging (creating a save point)")
		return self._session.begin_nested()

	def commit(self):
		if not self._session:
			raise IllegalStateException("No Session to commit. You must begin a Session prior to committing")
		self._session.commit()

	def flush(self):
		if not self._session:
			raise IllegalStateException("No Session to commit. You must begin a Session prior to flushing")
		self._session.flush()

	def cancel(self):
		if not self._session:
			raise IllegalStateException("No Session to commit. You must begin a Session prior to cancelling")
		self._session.cancel()

	def rollback(self):
		if not self._session:
			raise IllegalStateException("No Session to rollback. You must begin a Session prior to rolling back one")
		self._session.rollback()

	
