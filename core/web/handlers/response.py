# -*- coding: utf-8 -*-
"""
Acts as a logical proxy over Torando's RequestHandler.
Tornado bundles the input and output into one class, which muddles the
basic concept of client-server communication. We have this proxy as a means of
introducing a more clear architecture by defining distinct objects and their
roles (separation-of-concern)
"""

import abc
import functools
import logging
from lib.error import IllegalArgumentException


class ResponseHandler(object):

    __metaclass__ = abc.ABCMeta

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

    ###########################################################################
    # Properties
    ###########################################################################

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

    @property
    def status(self):
        return self.ctx.get_status()

    ###########################################################################
    # Abstract Methods
    ###########################################################################

    @abc.abstractmethod
    def canonicalize_data(self, data):
        """
        :param data:
        :return:
            The canonicalized dictionary
        """

    @abc.abstractmethod
    def parse(self, data):
        """
        """

    @abc.abstractmethod
    def respond(self, *args, **kwargs):
        """
        """

    ###########################################################################
    # Functions
    # Most of the following functions are simple proxies to
    # Tornado.RequestHandler
    ###########################################################################
    #
    def clear(self):
        """
        """
        self.ctx.clear()

    def clear_all_cookies(self, **kwargs):
        """
        """
        self.ctx.clear_all_cookies(**kwargs)

    def clear_cookies(self, name, **kwargs):
        """
        """
        self.ctx.clear_cookies(name, **kwargs)

    def get_cookie(self, name, default=None):
        """
        """
        return self.ctx.get_cookie(name, default=default)

    def get_secure_cookie(self, name, **kwargs):
        """
        """
        return self.ctx.get_secure_cookie(name, **kwargs)

    def get_secure_cookie_key_version(self, name, **kwargs):
        """
        """
        return self.ctx.get_secure_cookie_key_version(name, **kwargs)

    def filter(self, response):
        """
        """
        return response

    def initialize_filters(self):
        """
        """
        pass

    def redirect(self, url, permanent=False, status=None):
        """
        """
        self.ctx.redirect(url, permanent=permanent, status=status)

    def set_cookies(self, name, value, **kwargs):
        """
        """
        self.ctx.set_cookies(name, value, **kwargs)

    def set_default_headers(self):
        """
        """
        pass

    def set_secure_cookie(self, name, value, **kwargs):
        """
        """
        self.ctx.set_secure_cookie(name, value, **kwargs)

    def set_status(self, code, reason=None):
        """
        """
        self.ctx.set_status(code, reason)
