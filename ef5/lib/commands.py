
import os
import json
import logging
import base64
import settings

import tornado.gen as gen

from lib.error.exceptions import ElementError


class CommandsMixin(object):

    """
    """

    logger = logging.getLogger("ef5")

    def command_start(self, conn, request=None):
        """
        :param conn:
        :return:
        """

        return conn.start()

    def command_commit(self, conn, request=None):
        """
        :param conn:
        :return:
        """

        return conn.commit()

    def command_cancel(self, conn, request=None):
        """
        :param conn:
        :return:
        """

        return conn.cancel()

    def command_revert(self, conn, request=None):
        """
        :param conn:
        :return:
        """

        return conn.revert()

    def command_close(self, conn, request=None):
        """
        :param conn:
        :return:
        """

        return conn.close()

    def command_validate(self, conn, request=None):
        """
        :param conn:
        :return:
        """

        return conn.validate()

    def command_show(self, conn, request=None):
        """
        :param conn:
        :param request:
        :return:
        """

        ret = conn.get("object", request.arguments["path"][0])
        ret = ret.result()
        return ret if ret is not None else {}

    def command_request(self, conn, request=None):
        """
        """

        actionName = request.body_arguments["action"]
        data = request.body_arguments["parameters"] if "parameters" in request.body_arguments else {}
        ret = conn.action(actionName, data)
        return ret if ret is not None else {}

    def command_providers(self, conn, request=None):
        """
        """

        import xmlrpclib
        providers = ["local"]
        try:
            ret = conn.get(
                "list", "/configuration/context{" + settings.DEFAULT_CONTEXT + "}/aaa/auth-provider/web-auth")
            providers += [model["provider-id"] for model in ret.result()]
        except ElementError as e:
            if hasattr(e, "faultCode") and e.faultCode != 6:
                raise e

        try:
            ret = conn.get(
                "list", "/configuration/context{" + settings.DEFAULT_CONTEXT + "}/aaa/auth-provider/ldap")
            providers += [model["provider-id"] for model in ret.result()]
        except ElementError as e:
            if hasattr(e, "faultCode") and e.faultCode != 6:
                raise e

        try:
            ret = conn.get("list", "/configuration/context{"
                           + settings.DEFAULT_CONTEXT + "}/aaa/auth-provider/active-directory-server")
            providers += [model["provider-id"] for model in ret.result()]
        except ElementError as e:
            if hasattr(e, "faultCode") and e.faultCode != 6:
                raise e

        return providers

    def command_importcert(self, conn, request=None):
        """
        """

        fileName = "/home/mag/mag_user_data/" + request.body_arguments["filename"]
        name = request.body_arguments["name"] if "name" in request.body_arguments else ""
        passphrase = request.body_arguments["passphrase"] if "passphrase" in request.body_arguments else ""
        try:
            f = open(fileName, "r")
            f.seek(0)
            encoded = base64.b64encode(f.read()).replace('\n', '')
            data = {"passphrase": passphrase, "p12-pem-data": encoded, "name": name}
        except IOError as e:
            raise ElementError(e)
        finally:
            if os.path.isfile(fileName):
                os.remove(fileName)

        conn.start()
        try:
            conn.update("/configuration/context{" + settings.DEFAULT_CONTEXT + "}/aaa/pki/identity-certificate{" +
                        name + "}", data)
            return conn.commit()
        except ElementError as e:
            self.logger.info("Cancelling transaction...")
            conn.cancel()
            raise e
