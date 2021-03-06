# -*- coding: utf-8 -*-

"""
The end-point for a REST API. Provides the Typing and core functionality needed
to perform JSON-based CRUD operations. Implementors should define custom APIs
extending the REST API.
"""

import json
import web.request as request

from request import BaseHandler
from tornado.escape import native_str
from web.handlers import ResponseHandler

CONTENT_JSON = "json"
CONTENT_APPLICATION_JSON = "application/json"

"""

sooooooo....novel idea, but what if we define the url via something like
@GET("/something/{id}"), etc? we can define a root for the class. This would
then allow implementors to define some sort of control method and we can wrap
it with all the exception handling, coroutine, etc we need. We would hide the
get/post/put, etc. methods and any method wrapped by the corresponding
decorator would be called by its named method

so then we wouldn't need multiple models for element (just one) and we
have multiple endpoints for our models? or maybe we can have endpoints
per grouping?

So the last question would then how we hook into tornado's url handling without
imposing a hit to performance?

--> allow pattern matching in the url

--> biggest question is...how does the server determine all the urls at
    startup? or does it even need to? can it do a search during a request?
    that might take a lot of changes to tornado...also slower too. so nope.
    back to the first question.

@backend("Element")
@url("/configuration/context/(?<context>[\w\d-]+){1}/.*/(.*)?")
# Here we've defined the url root as '/atlas/api' in settings
class Atlas(REST):

    def prepare(self):
        # do stuff on the incoming request, like loading the appropriate model

    @authorized
    def get(self, slug):

        # TODO implement load in Transactor
        model = self.backend.load(self.model)
        result = self.capture(model.get(slug, **self.parameters))
        self.respond(result)

    ...etc.


@backend("SQL")
@model("User") # TODO allow either class or function? Should load the Model
@url("/login")
# Here we've defined the url root as '/atlas/api' in settings
class Login(REST):

    def prepare(self):
        # do stuff on the incoming request...

    def get(self):
        # etc...

    @authorized
    def post(self):
        # TODO should we make request body arguments first-class attrs of the class?
        username = self.parameters["username"]
        password = self.parameters["password"]
        self.backend.User.login(username, password)

"""


class REST(BaseHandler):

    def initialize(self):

        content_type = self.headers.get("Content-Type", "")
        if content_type.startswith(CONTENT_APPLICATION_JSON) or \
           content_type.startswith(CONTENT_JSON):
            try:
                uri_arguments = json.loads(native_str(self.body))
            except ValueError as e:
                self.logger.warning('Invalid json body: {0}'.format(e))
                uri_arguments = {}
            for name, values in uri_arguments.items():
                if values:
                    self.body_arguments.setdefault(name, values)
        else:
            msg = "Malformed request: invalid content type; expecting \
                  'applcation/json' or 'json'"
            raise BaseHandler.HTTPError(400, log_message=msg, reason=msg)

        super(REST, self).initialize()

    @property
    def parameters(self):
        return self.body_arguments


class RESTResponseHandler(ResponseHandler):
	"""
    """

    def respond(self, response=None):
        """
        :param response:
        :return:
        """

        if response is None:
            response = {}
        elif isinstance(response, str):
        	try:
            	response = dict(data=self._canonicalize_data(json.loads(response))
            except ValueError:
            	response = dict(message=self._canonicalize_data(response)
        elif isinstance(response, int) or isinstance(response, float):
            response = dict(code=self._canonicalize_data(response))
        elif isinstance(response, tuple):
            response = dict(data=self._canonicalize_data(response))
        elif isinstance(response, list):
            response = dict(data=self._canonicalize_data(response))
        elif isinstance(response, dict):
            response = self._canonicalize_data(response) if "data" in response or "reason" in response \
                else dict(data=self._canonicalize_data(response))

        return response

    def canonicalize_data(self, data):
        """
        :param data:
        :return:
            The canonicalized dictionary
        """

        # Format keys to JS safe
        if isinstance(data, list):
            return [self._canonicalize_data(val) for val in data]
        if isinstance(data, tuple):
            return tuple(self._canonicalize_data(val) for val in data)
        elif isinstance(data, dict):
            return dict(
                (key, self._canonicalize_data(val)) for key, val in data.items()
            )
        elif isinstance(data, str) and re.match(r"true", data, re.IGNORECASE):
            return True
        elif isinstance(data, str) and re.match(r"false", data, re.IGNORECASE):
            return False
        else:
            return data

    def parse(self, data):
    	"""
    	"""
    	return json.dumps(response)
