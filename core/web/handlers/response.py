# -*- coding: utf-8 -*-
"""
"""

class ResponseHandler(object):

    logger = logging.getLogger("ef5")

    def __init__(self, request):
        if not request:
            raise AttributeError("Expected request; found 'None'")

        self.request = request

        self._initialize_filters()

    def respond(self, response=None, cache=False):
        """
        :param response:
        :return:
        """

        if not cache:
            self.request.set_header('Cache-Control', 'no-cache, no-store, must-revalidate')

        if response is None:
            response = {}
        elif isinstance(response, str):
            if response.startswith("{") and response.endswith("}"): # TODO this test can be better/more stable

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

        response = self.filter(response)

        self.request.write(json.dumps(response))
        self.request.finish()

    def filter(self, response):
        return response

    def _initialize_filters(self):
        pass

    def _canonicalize_data(self, data):
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