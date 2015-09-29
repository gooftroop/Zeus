"""
"""

import settings
from tornado.web import HTTPError

try:
    from urllib import urlencode  # py2
except ImportError:
    from urllib.parse import urlencode  # py3


def authenticated(method):
    """
    12/02/14 @bwebb Pulled from Torando web.py to alter the behavior
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