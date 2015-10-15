# -*- coding: utf-8 -*-

# This is the end-point for a rest API. Provides CRUD operations
# rest has a request and response handler
# rest is a <tornado request>
# rest uses/calls the dao
# 
# Implementors should define custom APIs extending rest (which provides the adapter to be associated with the DAO)

"""
"""

import json
import web.request as request

from request import BaseHandler
from tornado.escape import native_str
from web.handlers import ResponseHandler

CONTENT_JSON = "json"
CONTENT_APPLICATION_JSON = "application/json"


@BaseHandler.responsehandler(RESTResponseHandler)
class REST(BaseHandler):
	
	def initialize(self):

		content_type = self.headers.get("Content-Type", "")
		if content_type.startswith(CONTENT_APPLICATION_JSON) or content_type.startswith(CONTENT_JSON):
	        try:
	            uri_arguments = json.loads(native_str(self.body))
	        except ValueError as e:
	            self.logger.warning('Invalid json body: {0}'.format(e))
	            uri_arguments = {}
	        for name, values in uri_arguments.items():
	            if values:
	                self.body_arguments.setdefault(name, values)
        else
        	msg = "Malformed request: invalid content type; expecting 'applcation/json' or 'json'"
        	raise BaseHandler.HTTPError(400, log_message=msg, reason=msg)

    super(REST, self).initialize()


class RESTResponseHandler(ResponseHandler):
	"""
	"""

	@BaseHandler.responsefilter
    def respond(self, response=None):
        """
        :param response:
        :return:
        """

        if response is None:
            response = {}
        elif isinstance(response, str):
            if response.startswith("{") and response.endswith("}"): # TODO this test can be better/more stable, as in...use try/except

                # Validate the dict being passed in by string
                try:
                    response = dict(data=self._canonicalize_data(json.loads(response)))
                except Exception as e:
                    msg = "Invalid JSON response detected: {0}".format(e)
                    self.logger.error(msg)
                    self.request.send_error(status_code=400, reason=msg)

                    # Prevent any additional processing
                    self.request.finish()
                    return
            else:
                response = dict(message=self._canonicalize_data(response))
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
            # For now, just return the value. Later expansions can use this to work on the data explicitly
            return data

    def parse(self, data):
    	"""
    	"""
    	return json.dumps(response)
