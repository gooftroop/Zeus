
import logging
import settings
import importlib

from tornado import gen
from lib.error.exceptions import AuthenticationError
from lib.middleware.element import ElementError, ElementXMLRPC

logger = logging.getLogger("auth")


def _load_from_path():

    middleware = settings.AUTHENTICATION_MODULE
    logger.debug("Received middleware {0}".format(middleware))
    try:
        module_path, class_name = middleware.rsplit('.', 1)
    except ValueError as e:
        msg = "{0} is an invalid module path: {1}".format(middleware, str(e))
        logger.error(msg)
        raise AuthenticationError(msg)

    try:
        module = importlib.import_module(module_path)
    except ImportError as e:
        msg = "Error importing module {0}: {1}".format(module_path, str(e))
        logger.error(msg)
        import traceback

        logger.debug(traceback.format_exc())
        raise AuthenticationError(msg)

    try:
        backend = getattr(module, class_name)
    except AttributeError:
        msg = "Module '{0}' does not define a '{1}' class".format(module_path, class_name)
        logger.error(msg)
        raise AuthenticationError(msg)

    logger.debug("Loading Authentication Module {0}".format(backend))
    return backend

backend = _load_from_path()


@gen.coroutine
def login(request, username, password):
    """
    :param request:
    :param username:
    :param password:
    :return:
    """

    auth = backend(request)

    if password is None or username is None:
        raise AuthenticationError("Username and password not provided")

    user = auth.login(request, username, password)
    if user is not None:

        # Log into Element
        try:
            connection = ElementXMLRPC(url=settings.ELEMENT_URL)
            element_session_id = connection.authenticate(username, password)
        except ElementError as e:
            msg = "Failed to authenticate against Element: {0}".format(str(e))
            raise AuthenticationError(msg)

        request.set_cookie(settings.ELEMENT_SESSION_ID, element_session_id)
        request.set_cookie(settings.CONTEXT_COOKIE, settings.DEFAULT_CONTEXT)

        auth.add_to_session(settings.ELEMENT_SESSION_ID, element_session_id)

        gen.Return(True)
    else:
        raise AuthenticationError("Login Failed. No such user exists.")


# TODO need a better way to maintain user auth
@gen.coroutine
def logout(request):
    """
    :param request:
    :return:
    """

    from lib.middleware.element import ElementError, ElementXMLRPC
    auth = backend(request)

    try:
        element_session_id = request.get_cookie(settings.ELEMENT_SESSION_ID)
        if element_session_id:
            connection = ElementXMLRPC(url=settings.ELEMENT_URL, session_id=element_session_id)
            connection.logout()
        gen.Return(True)
    except KeyError:
        raise AuthenticationError("Session Timed Out")
    except ElementError as e:
        msg = "Error logging out Element session: {0}".format(str(e))
        raise AuthenticationError(msg)
    finally:
        auth.logout(request)

        request.clear_cookie(settings.ELEMENT_SESSION_ID)
        request.clear_cookie(settings.CONTEXT_COOKIE)


def is_authenticated(request, user):
    """
    :param user:
    :return:
    """

    if user is None:
        return False

    from lib.middleware.element import ElementXMLRPC

    try:
        connection = ElementXMLRPC(url=settings.ELEMENT_URL)
        if connection.is_active(request.get_cookie(settings.ELEMENT_SESSION_ID)):
            if not backend.is_authenticated(request, user):
                logger.error("User '{0}' is not authenticated".format(user))
                return False
        else:
            logger.error("The element session for user '{0}'' is no longer active or valid".format(user))
            return False
    except Exception as e:
        logger.error("An error occured while authenticating user '{0}': {1}".format(user, e))
        return False

    return True
