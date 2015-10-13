# -*- coding: utf-8 -*-
"""
"""

import traceback

import tornado.web as webb
import tornado.gen as gen
import config.global_settings as settings

from lib.auth import is_authenticated

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


class BaseHandler(web.RequestHandler):
    """
    """

    logger = logging.getLogger("ef5")

    def initialize(self):
        """
        :return:
        """

        self.response = ResponseHandler(self)

    def prepare(self):
        """
        """

        self.before_prepare()

        super(BaseHandler, self).prepare()

        self.after_prepare()

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

    def before_prepare(self):
        """
        :return:
        """
        pass

    def after_prepare(self):
        """
        :return:
        """
        pass

    def get(self):
        msg = "GET operation not supported"
        raise HTTPError(403, log_message=msg, reason=msg)

    def post(self):
        msg = "POST operation not supported"
        raise HTTPError(403, log_message=msg, reason=msg)

    def put(self):
        msg = "PUT operation not supported"
        raise HTTPError(403, log_message=msg, reason=msg)

    def patch(self):
        msg = "PATCH operation not supported"
        raise HTTPError(403, log_message=msg, reason=msg)

    def delete(self):
        msg = "DELETE operation not supported"
        raise HTTPError(403, log_message=msg, reason=msg)

    def head(self):
        msg = "HEAD operation not supported"
        raise HTTPError(403, log_message=msg, reason=msg)

    def options(self):
        msg = "OPTIONS operation not supported"
        raise HTTPError(403, log_message=msg, reason=msg)
