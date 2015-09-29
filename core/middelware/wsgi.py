
import os
import traceback
import tornado
import logging
import settings

try:
    import Cookie  # py2
except ImportError:
    import http.cookies as Cookie  # py3

from tornado import escape
from tornado.wsgi import WSGIContainer
from django.conf import settings as djsettings

GET = "get"

logger = logging.getLogger("wsgi")


class DjangoWSGIContainer(WSGIContainer):

    """
    """

    def __call__(self, request):

        data = {}
        response = []

        def start_response(status, response_headers, exc_info=None):
            data["status"] = status
            data["headers"] = response_headers
            return response.append

        app_response = self.wsgi_application(WSGIContainer.environ(request), start_response)

        try:
            response.extend(app_response)
            body = b"".join(response)
        finally:
            if hasattr(app_response, "close"):
                app_response.close()
        if not data:
            raise Exception("WSGI app did not call start_response")

        status_code = int(data["status"].split()[0])
        headers = data["headers"]
        header_set = set(k.lower() for (k, v) in headers)
        body = escape.utf8(body)

        if status_code != 304:
            if "content-length" not in header_set:
                headers.append(("Content-Length", str(len(body))))
            if "content-type" not in header_set:
                headers.append(("Content-Type", "text/html; charset=UTF-8"))
        if "server" not in header_set:
            headers.append(("Server", "TornadoServer/%s" % tornado.version))

        # try:

            # if request.method.lower() != GET:

            # _cookies = Cookie.SimpleCookie()

            # Django session cookies are set at the django level, but
            # tornado-specific cookies are appended here.

            # token = request.cookies[djsettings.CSRF_COOKIE_NAME]
            # if token:
            #     _cookies[settings.XSRF_TOKEN] = token.value

            # TODO Change when we add more contexts
            # _cookies[settings.CONTEXT_COOKIE] = settings.DEFAULT_CONTEXT

            # for c in _cookies.output(sep='\t').split('\t'):
            #     k, v = c.split(': ')
            #     headers.append((k, v + '; Path=/'))

        # except ValueError as e:
        #     logging.getLogger("ef5").error("A Value is either missing or invalid: {0}".format(e))
        # except Exception as e:
        #     logging.getLogger("ef5").error("An unknown error occurred: {0} with stacktrace {1}".format(e, traceback.format_exc()))

        parts = [escape.utf8("HTTP/1.1 " + data["status"] + "\r\n")]
        for key, value in headers:
            parts.append(escape.utf8(key) + b": " + escape.utf8(value) + b"\r\n")

        parts.append(b"\r\n")
        parts.append(body)

        request.write(b"".join(parts))
        request.finish()
        self._log(status_code, request)

    def _set_cookie(self, request, key, value):
        """
        :param key:
        :param value:
        :return:
        """

        request.headers.add("Set-Cookie", "")
