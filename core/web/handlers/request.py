# -*- coding: utf-8 -*-

"""
"""

import abc
import functools
import traceback

import tornado.web as web
import tornado.gen as gen
import config.global_settings as settings

from tornado.concurrent import is_future
from lib.auth import is_authenticated
from lib.error import (ImproperlyConfiguredException,
                       NotYetImplementedException,
                       IllegalArgumentException,
                       TransactorException,
                       DAOException,
                       ValidationException)

GET = "get"
POST = "post"
PUT = "put"
PATCH = "patch"
DELETE = "delete"
UPDATE = "post"
MODIFY = "patch"
CREATE = "put"
REMOVE = "delete"
HEAD = "head"
OPTIONS = "options"

FALLBACK_ERROR_TITLE = "Oops!"
FALLBACK_ERROR_MESSAGE = "An error occurred while processing your request. Please contact your System Administrator"


def authenticated(method):
    """
    @bwebb Pulled from Torando web.py to alter the behavior
    of auth failure to redirect if REDIRECT_LOGIN is true, error out
    otherwise, for all wrapped methods.

    Decorate methods with this to require that the user be logged in.

    If the user is not logged in, they will be redirected to the configured
    `login url <RequestHandler.get_login_url>`.

    If you configure a login url with a query parameter, Tornado will
    assume you know what you're doing and use it as-is.  If not, it
    will add a `next` parameter so the login page knows where to send
    you once you're logged in.
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.get_current_user():
            url = self.get_login_url()
            if "?" not in url:
                if urlparse.urlsplit(url).scheme:
                    # if login url is absolute, make next absolute too
                    next_url = self.request.full_url()
                else:
                    next_url = self.request.uri
                url += "?" + urlencode(dict(next=next_url))
            if settings.REDIRECT_LOGIN:
                self.redirect(url)
                return
            else:
                raise HTTPError(403)
        return method(self, *args, **kwargs)
    return wrapper


def backend(backend):
    """
    Declare the backend to be used by the decorated class
    Support either name, object, or function
    """

    def wrapper(obj):
        if inspect.isclass(obj):
            obj._cls_backend = backend
        else:
            obj.backend = backend
    return cls_wrapper


def model(model):
    """
    Declare the model name to be used by the decorated class
    Support either name, object, or function
    """

    def wrapper(obj):
        if inspect.isclass(obj):
            obj._cls_model = model
        else:
            obj.model = model
    return cls_wrapper


def response(handler):
	"""
    Declare the Response Handler object to be used with the class
    Support either name, object, or function
    """

    def wrapper(obj):
        if inspect.isclass(obj):
            obj._cls_response = handler
        else:
            obj.response = handler
    return cls_wrapper


def catch(Catch, message=None):
	"""
	Handle the defined exception
	"""

	def catch_decorator(fn):
		@functools.wraps(fn)
		def fn_wrapper(*args, **kwargs):
			try:
				return fn(*args, **kwargs)
			except Catch as e:
				msg = "{0}".format(e)
				if message is not None:
					msg = "{0} ({1})".format(message, msg)
	    		raise BaseHandler.HTTPError(400, log_message=msg, reason=msg)


def url(url):
    """
    Attach a url attribute to the class
    TODO Ideally I'd like to define an 'on' callback (i.e. <something>.on("urls", url))
    so that when an application spins up it will call this event and recieve all urls
    defined in this manner. However, I'm going to need to create a event-based comm 
    module that hooks into Tornado's IO for async events (non-async will need dict-
    based impl). Until then, iimplementations creating Application objects will
    need to reach into imported API classes, populate the urls, and pass it to the
    Application instantiation
    """

    def cls_wrapper(cls):
        cls._url = url
    return cls_wrapper


class BaseHandler(web.RequestHandler):
    """
    """

    __metaclass__ = abc.ABCMeta

    logger = logging.getLogger("ef5")
    _url = None
    _cls_backend = None
    _cls_model = None
    _cls_response = None

    def initialize(self):
        """
        Do not override
        :return:
        """
        self._backend = None
         self._model = None
        self._response = None

        # Take advanntage of any logic in the setters
        self.response = self._cls_response
        self.backend = self._cls_backend
        self.model = self._cls_model

        self.configure()
        if self.response is None:
        	raise ImproperlyConfiguredException("Missing response object")

    @classmethod
    def url(cls):
        """
        """
        return cls._url

    @classmethod
    def default_backend(cls):
        """
        """
        return cls._cls_backend

    @classmethod
    def default_model(cls):
        """
        """
        return cls._cls_model

    @classmethod
    def default_response_handler(cls):
        """
        """
        return cls._cls_response

    ###########################################################################
    # Properties
    ###########################################################################

    @property
    def backend(self):
        """
        """
        return self._backend

    @backend.setter
    def backend(self, _backend):
        """
        """
    	if _backend is None:
    		raise IllegalArgumentException("backend cannot be empty")
        # TODO if string, load
        # if function, call
    	self._backend = _backend

    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, model_name):
        """
        """
        if _response is None:
            raise IllegalArgumentException("model name cannot be empty")

        if isinstance(model_name, tuple):
            model_name = model_name[0]
            rest = model_name[1]

        if isinstance(model_name, basestring):
            self._model = self._backend.load(model_name, **rest)
        elif inspect.isfunction(model_name):
            self._model = model_name(**rest)
        else
            self._model = model_name

    @property
    def response(self):
        """
        """
        return self._response
    
    @response.setter
    def response(self, _response):
        """
        """
    	# TODO each response should inherit from a single Response Object
    	# check for that
        # TODO if string, load
        # if function, call 
    	if _response is None:
    		raise IllegalArgumentException("response cannot be empty")
    	self._response = _response

    ###########################################################################
    # Abstract Methods
    ###########################################################################
    
    @abc.abstractmethod    
    def configure(self):
        """
        """

    @abc.abstractmethod
    def prepare(self):
        """
        """

    ###########################################################################
    # Functions
    ###########################################################################
    
    def capture(self, fn_ret):
        """
        """

        result = fn_ret
        if is_future(result): # import is_future
            result = yield result
        return result

   	# TODO set up basic HTTP Auth. Also sure that this could be better
    def get_current_user(self):
        """
        Tornado's authenticated check is basic, so we need to do some extra validation against
        Element to verify that the current user is auth'd and not stale
        """

        user = self.get_cookie(settings.USER_COOKIE)
        if user is None:
            return None
        else:
            if not is_authenticated(self, user):
                self.logger.info("Authentication Failed. Access is forbidden.")
                return None

            return user

    def on_finish(self):
    	"""
    	"""
    	pass

    def respond(self, *args, **kwargs):
        """
        """
    	self.response._respond(*args, **kwargs)

    def write_error(self, status_code, **kwargs):
        """
        :param status_code:
        :param kwargs:
        :return:
        """

        # for requests passing a status code, use the code to look up error
        # if no error exists for status_code, allow pass through
        # if code exists in kwargs, then don't do a look up and dont use status_code (short circuit)
        # code should only be set when a Error Code is passed in

        data = {}

        if self.settings.get("serve_traceback") and "exc_info" in kwargs:
            # in debug mode, try to send a traceback
            data["traceback"] = ""
            for line in traceback.format_exception(*kwargs["exc_info"]):
                data["traceback"] += line

        # if "code" not in kwargs:
        #     try:
        #         error = errors.ErrorCodeEnum().get(status_code)
        #         data = data.update(error)
        #     except AttributeError:
        #         data["code"] = status_code
        #         data["reason"] = kwargs.get("reason", "None") if "reason" in kwargs else self._reason
        #         data["message"] = FALLBACK_ERROR_MESSAGE
        #         data["title"] = FALLBACK_ERROR_TITLE
        # else:
        data["code"] = kwargs.get("code", status_code)
        data["reason"] = kwargs.get("reason", self._reason)
        data["message"] = kwargs.get("message", FALLBACK_ERROR_MESSAGE)
        data["title"] = kwargs.get("title", FALLBACK_ERROR_TITLE)

        self.response.respond(data)
