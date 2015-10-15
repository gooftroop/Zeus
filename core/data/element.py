# use the python bindings for element
# should be responsible for implementing dao.py 
# Users should implement "element models" that extend element. The models will be responsible for providing the 
# custom fields, while element.py will be responsible for providing the interface to actually interact with element

from dao import Base

class MOI(DAO):
	"""
	"""

	def __init__(self):
		super(Model, self).__init__(self)

	def destroy(self):
		pass

	def to_string(self):
		pass

	###########################################################################
	# Data Access APIs
	###########################################################################
	
	@DAO.gen.coroutine
	def get(self, key, *args, **kwargs):
		pass

	@DAO.gen.coroutine
	def create(self, key, value, *args, **kwargs):
		pass

	@DAO.gen.coroutine
	def update(self, key, value, *args, **kwargs):
		pass

	@DAO.gen.coroutine
	def replace(self, key, value, *args, **kwargs):
		pass

	@DAO.gen.coroutine
	def delete(self, key, value, *args, **kwargs):
		pass

	###########################################################################
	# Data Set Operations
	###########################################################################
	
	@DAO.gen.coroutine
	def add(self, other):
		pass 

	@DAO.gen.coroutine
	def sub(self, other):
		pass 

	@DAO.gen.coroutine
	def mul(self, other):
		pass 

	@DAO.gen.coroutine
	def div(self, other):
		pass 

	@DAO.gen.coroutine
	def AND(self, other):
		pass 

	@DAO.gen.coroutine
	def OR(self, other):
		pass 

	@DAO.gen.coroutine
	def XOR(self, other):
		pass

	@DAO.gen.coroutine
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


class Element(Transactor):
	"""
	"""

	def __init__(self):
		super(Element, self).__init()

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