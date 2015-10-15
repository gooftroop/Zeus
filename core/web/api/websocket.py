# -*- coding: utf-8 -*-

"""
"""

from web.handlers import BaseHandler
from tornado.websocket import WebSocketHandler

class WebSocket(BaseHandler, WebSocketHandler):
	"""
	"""
	
	def intialize(self):
		super(WebSocket, self).initialize()
		self.respond = self.write