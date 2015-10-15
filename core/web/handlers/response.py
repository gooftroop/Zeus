# -*- coding: utf-8 -*-
"""
Acts as a logical proxy over Torando's RequestHandler.
Tornado bundles the input and output into one class, which muddles the
basic concept of client-server communication. We have this proxy as a means of
introducing a more clear architecture by defining distinct objects and their
roles (separation-of-concern)
"""

from lib.error import IllegalArgumentException

class ResponseHandler(object):

    logger = logging.getLogger("ef5")

    def __init__(self, ctx):
        if not ctx:
            raise IllegalArgumentException("Expected ctx; found 'None'")

        self.ctx = ctx
        self.initialize_filters()
        self.set_default_headers()

    def _respond(self, *args, **kwargs):
        """
        :param response:
        :return:
        """

        if not kwargs.pop("cache", False):
            self.ctx.set_header('Cache-Control', 'no-cache, no-store, must-revalidate')

        response = self.respond(*args, **kwargs)
        response = self.filter(response)
        self.ctx.write(self.parse(response))
        self.ctx.finish()

    @property
    def status(self):
        return self.ctx.get_status()

    @property
    def headers(self):
        """
        """
        return self.ctx._headers

    @headers.setter
    def headers(self, name, value, overwrite=True):
        """
        """
        if overwrite:
            self.ctx.set_header(name, value)
        else:
            self.ctx.add_header(name, value)

    @headers.deleter
    def headers(self, name):
        """
        """
        self.ctx.clear_header(name)

    def clear(self):
        """
        """
        self.ctx.clear()

    def set_default_headers(self):
        """
        """
        pass

    def respond(self, *args, **kwargs):
        """
        """
        pass

    def set_status(self, code, reason=None):
        """
        """
        self.ctx.set_status(code, reason)

    def filter(self, response):
        """
        """
        return response

    def initialize_filters(self):
        """
        """
        pass

    def canonicalize_data(self, data):
        """
        :param data:
        :return:
            The canonicalized dictionary
        """
        return data

    def parse(self, data):
        """
        """

        return data