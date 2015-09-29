# use the python bindings for element
# should be responsible for implementing dao.py 
# Users should implement "element models" that extend element. The models will be responsible for providing the 
# custom fields, while element.py will be responsible for providing the interface to actually interact with element

from dao import Base

class Element(Base):
	"""
	"""

	def __init__(self):
		super(Element, self).__init()