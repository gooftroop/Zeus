
import settings
import logging

from winnebadjango import settings as djsettings
from lib.middleware.element import ElementXMLRPC
from lib.error.exceptions import AuthenticationError, ElementError

import django.db
import django.conf
import django.contrib.auth
import django.utils.importlib

import django.core.handlers.wsgi
from tornado import wsgi


logger = logging.getLogger("auth")


class BaseAuthMixin(object):

    """
    """

    def __init__(self, context):
        """
        :param context:
        :return:
        """

        # We might have to de-pickle this until we get a backend. When we do, this should just be the username
        self._current_user = self._get_current_user(context)
        self._element_session_id = self._get_element_session(context)
        self._session_id = ""
        self._session_name = ""

    # TODO implement persistent user storage - until then, the validity period of the user with PAMAuth is always true
    def _get_current_user(self, context):
        """
        :param context:
        :return:
        """

        if not hasattr(self, "_current_user"):

            # Attempt to get the current user through the overridden get_current_user.
            if hasattr(context, "current_user"):
                self._current_user = context.current_user
            else:
                self._current_user = None

        return self._current_user

    def _get_element_session(self, context):
        """
        :param context:
        :return:
        """

        if not hasattr(self, "_element_session_id"):
            cookie = context.get_cookie(settings.ELEMENT_SESSION_ID)
            if cookie is not None:
                if "=" in cookie:
                    self._element_session_id = cookie.split('=')[1]
                else:
                    self._element_session_id = cookie
            else:
                self._element_session_id = ""

        return self._element_session_id

    @property
    def element_session_id(self):
        """
        :return:
        """

        return self._element_session_id

    @property
    def session_name(self):
        """
        :return:
        """

        return self._session_name

    @property
    def session_id(self):
        """
        :return:
        """

        return self._session_id

    def _get_request(self, context):
        """
        :param context:
        :return:
        """

        raise NotImplementedError("BaseHandler does not implement _get_request")

    def _get_session(self, context):
        """
        :param context:
        :return:
        """

        raise NotImplementedError("BaseHandler does not implement _get_session")

    def get_authenticated_user(self, username, password):
        """
        :param username:
        :param password:
        :return:
        """

        raise NotImplementedError("BaseHandler does not implement get_authenticated_user")

    def logout(self):
        """
        :return:
        """

        raise NotImplementedError("BaseHandler does not implement logout")

    @staticmethod
    def is_authenticated(context, user):
        """
        :param context:
        :param user:
        :return:
        """

        raise NotImplementedError("BaseHandler does not implement is_authenticated")


# TODO Untested
class PAMAuthMixin(BaseAuthMixin):

    """
    """

    def __init__(self, context):
        """
        :param context:
        :return:
        """

        super(PAMAuthMixin, self).__init__(context)

    def get_authenticated_user(self, username, password):
        """
        :param username:
        :param password:
        :return:
        """

        import pam
        from models import User

        if self._current_user.is_authenticated:
            return self._current_user
        else:
            auth_engine = pam.pam()
            if auth_engine.authenticate(username, password):

                try:
                    connection = ElementXMLRPC(url=settings.ELEMENT_URL)
                    self._element_session_id = connection.authenticate(username, password)
                except ElementError as e:
                    raise AuthenticationError(str(e))

                # Until we have a backend, we might have to pickle and de-pickle this
                # When we do, store the object and return the username
                user = User(username, self._element_session_id)
                return user
            else:
                raise AuthenticationError("Login failed: [{0}] {1}".format(auth_engine.code, auth_engine.reason))

    def logout(self):
        """
        :return:
        """

        # This should also have the effect of removing it from the backend
        self._current_user.is_authenticated = False

    @staticmethod
    def is_authenticated(context, user):
        """
        :param context:
        :param user:
        :return:
        """

        return user and user.is_authenticated


class DjangoAuthMixin(BaseAuthMixin):

    """
    """

    def __init__(self, context):
        """
        :param context:
        :return:
        """

        django.db.connection.queries = []

        super(DjangoAuthMixin, self).__init__(context)

        self._get_request(context)

    def _get_request(self, context):
        """
        :param context:
        :return:
        """

        # if not hasattr(self, "_request"):

        if not hasattr(context.request, "host"):
            context.request.host = context.request.headers["host"]

        self._request = django.core.handlers.wsgi.WSGIRequest(wsgi.WSGIContainer.environ(context.request))
        self._request.session = self._get_session(context)
        self._request.user = django.contrib.auth.get_user(self._request)

        return self._request

    def _get_session(self, context):
        """
        :param context:
        :return:
        """

        if not hasattr(self, "_session"):

            try:

                cookie = context.get_cookie(django.conf.settings.SESSION_COOKIE_NAME)
                if cookie is not None:
                    if "=" in cookie:
                        self._session_id = str(cookie).split('=')[1]
                    else:
                        self._session_id = cookie

                engine = django.utils.importlib.import_module(django.conf.settings.SESSION_ENGINE)
                self._session = engine.SessionStore(self._session_id)

                user_id = None
                cookie = context.get_cookie(django.contrib.auth.SESSION_KEY)
                if cookie is not None:
                    if "=" in cookie:
                        user_id = str(cookie).split('=')[1]
                    else:
                        user_id = cookie

                self._session[django.contrib.auth.SESSION_KEY] = user_id
                self._session[django.contrib.auth.BACKEND_SESSION_KEY] = djsettings.AUTHENTICATION_BACKENDS[0]

            except Exception as e:
                logger.error(e)
                logger.error(traceback.format_exc())
                return None

        return self._session

    def clean(self):
        """
        :return:
        """

        # Clean up django ORM connections
        django.db.connection.close()

        if settings.DEBUG:
            logger.info('%d sql queries' % len(django.db.connection.queries))
            for query in django.db.connection.queries:
                logger.debug('%s [%s seconds]' % (query['sql'], query['time']))

        # Clean up after python-memcached
        from django.core.cache import cache

        if hasattr(cache, 'close'):
            cache.close()

    def login(self, context, username, password):
        """
        :param username:
        :param password:
        :return:
        """

        if self._request.user and self._request.user.is_authenticated():
            return self._request.user
        else:
            import django.contrib.auth as dauth
            from django.conf import settings as conf
            # Call PAM's authenticate
            self._request.user = dauth.authenticate(username=username, password=password)
            if self._request.user is not None:

                if self._request.user.is_active:

                    # If Django did not have the user in it's backend, then the user is added
                    # by pam, but without a password. Set the password and save the user
                    if not self._request.user.has_usable_password():
                        self._request.user.set_password(password)
                        self._request.user.save()

                    # Call Django's login
                    dauth.login(self._request, self._request.user)

                    # Extract the Session ID
                    cookie_name = conf.SESSION_COOKIE_NAME
                    if hasattr(self._request.COOKIES, cookie_name):
                        context.set_cookie(cookie_name, self._request.COOKIES[cookie_name])
                    elif hasattr(self._request, "session") and hasattr(self._request.session, "session_key"):
                        context.set_cookie(cookie_name, self._request.session.session_key)
                    else:
                        msg = "Django Login failed. No Session ID was found"
                        self._raise_error(msg)

                    # Extract the pk (primary key) from the user as it's active user id
                    if not hasattr(self._request.user, "pk"):
                        msg = "Django Login failed. No Authenticated User ID was found"
                        self._raise_error(msg)
                    self._request.user.user_id = str(self._request.user.pk)

                    # Verify the user auth backend
                    if not hasattr(self._request.user, "backend"):
                        msg = "Django Login failed. No User backend was found"
                        self._raise_error(msg)

                    # Set cookie content
                    context.set_cookie(conf.CSRF_COOKIE_NAME, self._request.META["CSRF_COOKIE"])
                    context.set_cookie(settings.AUTH_USER_ID, self._request.user.user_id)
                    context.set_cookie(settings.USER_COOKIE, self._request.user.username)
                    context.set_cookie(settings.USER_BACKEND, self._request.user.backend)

                    # Django sepcific content
                    context.set_cookie(django.contrib.auth.BACKEND_SESSION_KEY, djsettings.AUTHENTICATION_BACKENDS[0])
                    context.set_cookie(django.contrib.auth.SESSION_KEY, self._request.user.user_id)

                    # Save session
                    self._request.session.save()
                    return self._request.user
                else:
                    msg = "Your account is not active. Please contact your Site Administrator"
                    self._raise_error(msg)
            else:
                msg = "Username or password incorrect"
                self._raise_error(msg)

    def add_to_session(self, key, value):
        self._request.session[key] = value
        self._request.session.save()

    def logout(self, request):
        """
        :return:
        """

        from django.conf import settings as conf
        django.contrib.auth.logout(self._request)
        self._request.user = None
        request.clear_cookie(conf.CSRF_COOKIE_NAME)
        request.clear_cookie(settings.AUTH_USER_ID)
        request.clear_cookie(settings.USER_COOKIE)
        request.clear_cookie(django.contrib.auth.BACKEND_SESSION_KEY)
        request.clear_cookie(django.contrib.auth.SESSION_KEY)
        request.clear_cookie(conf.SESSION_COOKIE_NAME)
        request.clear_cookie(self._request.session.session_key)

    def _raise_error(self, msg):
        self.clean()
        raise AuthenticationError(msg)

    @staticmethod
    def is_authenticated(context, user):
        """
        :param context:
        :param user:
        :return:
        """

        class FakeRequest():
            pass

        request = FakeRequest()

        session_id = None
        cookie = context.get_cookie(django.conf.settings.SESSION_COOKIE_NAME)
        if cookie is not None:
            if "=" in cookie:
                session_id = str(cookie).split('=')[1]
            else:
                session_id = cookie

        engine = django.utils.importlib.import_module(django.conf.settings.SESSION_ENGINE)
        request.session = engine.SessionStore(session_id)

        user_id = ""
        cookie = context.get_cookie(django.contrib.auth.SESSION_KEY)
        if cookie is not None:
            if "=" in cookie:
                user_id = str(cookie).split('=')[1]
            else:
                user_id = cookie

        request.session[django.contrib.auth.SESSION_KEY] = user_id
        request.session[django.contrib.auth.BACKEND_SESSION_KEY] = djsettings.AUTHENTICATION_BACKENDS[0]

        django_user = django.contrib.auth.get_user(request)
        return django_user.is_authenticated()
