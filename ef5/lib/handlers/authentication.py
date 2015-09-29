"""
"""

import logging
import settings
import tornado.gen as gen

from lib.auth import login, logout, is_authenticated
from lib.error.exceptions import AuthenticationError

class LoginHandler(BaseHandler):

    """
    TODO
    As designed, Tornado is stateless, which means that everything goes back to client
    This can be unsecure, so in the future we might consider patching Tornado to check
    session if xsrf, element session id, and current user is not in a cookie(s)
    """

    logger = logging.getLogger("auth")

    def get_setup_mode(self):
        try:
            with open("/tmp/fcemode", "r") as myfile:
                return myfile.read()
        except (IOError, Exception) as e:
            self.logger.warning("Unable to open setupmode file: {0}".format(e))

        return None

    def get(self):

        # Set client headers
        self.set_header('Content-Type', 'application/json')
        self.set_header(settings.XSRF_TOKEN, self.xsrf_token)

        response = {}
        ########################################################################################################
        # Get setup mode
        ########################################################################################################
        ret = self.get_setup_mode()
        self.logger.info("Server in initial setup mode? {0}".format((ret is not None)))
        response["initial-setup-mode"] = ret is not None

        ########################################################################################################
        # Get serial number
        ########################################################################################################
        response["serial-number"] = ret if ret else ""

        ########################################################################################################
        # Get hostname
        ########################################################################################################
        proc = subprocess.Popen(["hostname"], stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()

        if err is not None:
            self.logger.error(err)

        response["hostname"] = out

        self.response.respond(response)

    @gen.coroutine
    # TODO HTTP basic auth support
    def post(self):

        username = None
        try:
            username = self.request.body_arguments["username"]
            if isinstance(username, list):
                username = username[0]
        except (web.MissingArgumentError, KeyError) as e:
            pass
            # Fall through to check existence of password

        try:
            password = self.request.body_arguments["password"]
            if isinstance(password, list):
                password = password[0]
            if not username:
                msg = "Username is required"
                self.logger.error(msg)
                self.send_error(status_code=401, reason=msg)
                return
        except (web.MissingArgumentError, KeyError) as e:
            # Attempt to use HTTP Basic Auth
            basic_auth = self.request.headers.get('Authorization')
            if not basic_auth or not basic_auth.startswidth('Basic'):
                msg = "Username and Password are required" if not username else "Password is required"
                self.logger.error(msg)
                self.send_error(status_code=401, reason=msg)
                return
            else:
                decoded = base64.decodestring(basic_auth[6:])
                username, password = decoded.split(':', 2)
                self.clear_header('Authorization')

        try:
            yield login(self, username, password)

            # Now that we've authenticated, get the setup mode and serial number
            # TODO the following is similar to atlasHandler.get. Let's see if we can generalize
            # TODO convert strings to consts
            # TODO this relies on hard coded context 'default' - this needs to be dynamic
            try:

            	# TODO This needs to be converted to using the Element DAO
                connection = ElementXMLRPC(url=settings.ELEMENT_URL,
                                           session_id=self._new_cookie.get(settings.ELEMENT_SESSION_ID).value)

                self.response.respond({"message": "Login Successful"})

            except ElementError as e:
                msg = "An error occurred while connecting to Element '{0}': {1}".format(type, e)
                self.logger.exception(msg)
                self.redirect("/atlas/api/logout", permanent=True)

        except AuthenticationError as e:
            # TODO we should check to see if we can resolve any messages coming from pam to readable messages
            msg = "Login Failed. {0}".format(str(e))
            self.logger.error(msg)
            self.logger.error(traceback.format_exc())
            self.send_error(status_code=401, reason=msg)
        except Exception as e:
            msg = "Login Failed. {0}".format(str(e))
            self.logger.error(msg)
            self.logger.error(traceback.format_exc())
            self.send_error(status_code=401, reason=msg)


class LogoutHandler(BaseHandler):

    """
    """

    logger = logging.getLogger("auth")

    @gen.coroutine
    def get(self):
        """
        :return:
        """

        try:
            yield logout(self)
            self.clear_cookie(settings.XSRF_TOKEN)
            self.response.respond({"message": "Logout Successful"})
        except AuthenticationError as e:
            msg = "Logout Failed. {0}".format(str(e))
            self.logger.error(msg)
            self.send_error(status_code=400, reason=msg)
