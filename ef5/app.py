# -*- coding: utf-8 -*-

"""
module: app.py

App.py is the entry point for the ef5 Tornado Server and is responsible for instantiating,
loading, configuring and starting the server.

members:

    ef5 is Mocana specific implementation of the Tornado Application.
    Loads and sets the URL Definitions, as well as any APP_SETTINGS.

History:
<date>          <author>            <comment>
07/2014         Brandon Webb        Creation

"""

__author__ = "Brandon Webb"
__copyright__ = "Copyright (c) 2014 by Mocana Corporation. All rights reserved"
__license__ = ""
__version__ = "1.0"

import os
import sys
import traceback
import signal

WINNEBADJANGO = "winnebadjango"
DJANGO_APP = "winnebadjango"

# TODO move to environment
# Adds the parent directory of the current directory of this file (*whew*) to the sys
pwd = os.path.dirname(os.path.realpath(__file__))
django_dir = os.path.join(pwd, WINNEBADJANGO)
contrib_dir = os.path.join(pwd, "lib/contrib")

if pwd not in sys.path:
    sys.path.insert(1, pwd)

if django_dir not in sys.path:
    sys.path.insert(1, django_dir)

if contrib_dir not in sys.path:
    sys.path.insert(1, contrib_dir)


# set the path for tornado. This is kind of a hack since the call context
# changes throughout this file.
os.environ["DJANGO_SETTINGS_MODULE"] = "winnebadjango.settings"

from tornado.httpserver import HTTPServer
from tornado.ioloop import PeriodicCallback
import tornado.ioloop as ioloop
import tornado.web
import tornado.wsgi

import settings
settings.configure()

import logging

from handlers import core, atlas
import urls as base_urls

from tornado.httpserver import HTTPServer
from django.core.handlers import wsgi as dwsgi
from lib.middleware.wsgi import DjangoWSGIContainer

logger = logging.getLogger("ef5")

bind_handlers = set()


class EF5(tornado.web.Application):

    """
    """

    def __init__(self):

        winnebadjango = DjangoWSGIContainer(dwsgi.WSGIHandler())

        base_urls.populate_url_definitions()
        urls = base_urls.url_definitions
        # urls = url_definitions
        urls.append((r"/atlas/(?:api/)?ping", core.Ping))
        urls.append((r"/atlas/(?:api/)?login", core.LoginHandler))
        urls.append((r"/atlas/(?:api/)?logout", core.LogoutHandler))
        urls.append((r"/atlas/(?:api/)?error/?(?P<error>[^ &<])?", core.ErrorHandler))
        urls.append((r"/atlas/(?:api/)?test/mock", atlas.TestHandler))
        urls.append((r"/atlas/(?:api/)?keys/(?P<target>[^ &<]+)", atlas.KeyHandler))
        urls.append((r"/atlas/(?:api/)?commands/?(?P<action>[^ &<]+)?", core.CommandHandler))
        urls.append((r"/atlas/(?:api/)?schema(?P<name>/[^ &<]+)?", core.Schema))
        urls.append((r"/atlas/(?:api/)?upload/?(?P<filename>[^ &<]+)?", core.FileUploadHandler))
        urls.append((r"/atlas/static/(.*)", tornado.web.StaticFileHandler, {
            'path': settings.path(settings.ROOT, "winnebadjango/public/atlas/static")
        }))
        urls.append((r"/atlas/(.*)", core.DjangoHandler, {'fallback': winnebadjango}))

        tornado.web.Application.__init__(self, urls, **settings.APP_SETTINGS)


class EF5HttpsServer(HTTPServer):

    def __init__(self, *args, **kwargs):
        super(EF5HttpsServer, self).__init__(*args, **kwargs)
        self.setup_worker_handlers()

    def setup_worker_handlers(self):

        def graceful_shutdown_handler(signum, _):
            logger.info("Received signal {0}. Starting shutdown process".format(signum))
            for handler in bind_handlers:
                ioloop.IOLoop.instance().remove_handler(handler[0])
            ioloop.IOLoop.instance().add_callback(ioloop.IOLoop.instance().stop)
            logger.info("Finished shutdown process")

        logger.info("STARTUP: registering signal handlers...")
        signal.signal(signal.SIGTERM, graceful_shutdown_handler)
        signal.siginterrupt(signal.SIGHUP, False)  # prevent interrupted system call errors

        signal.signal(signal.SIGINT, graceful_shutdown_handler)
        signal.siginterrupt(signal.SIGHUP, False)  # prevent interrupted system call errors

        signal.signal(signal.SIGHUP, graceful_shutdown_handler)
        signal.siginterrupt(signal.SIGHUP, False)  # prevent interrupted system call errors

        signal.signal(signal.SIGQUIT, graceful_shutdown_handler)
        signal.siginterrupt(signal.SIGQUIT, False)  # prevent interrupted system call errors


def add_tornado_handler(fd, handler, events=None):

    logger.info("Adding handler '{0}:{1}' to be attached to the EF5 servers".format(fd, handler))

    if not events:
        events = ioloop.IOLoop.READ | ioloop.IOLoop.WRITE | ioloop.IOLoop.ERROR

    bind_handlers.add((fd, handler, events))


def main():
    """
    ef5 Tornado Application.
    Load, initialize, and run the Tornado server with the configured parameters found in settings.
    :return:
    """

    logger.info("STARTUP: initializing server...")
    os.system("{0}/manage.py syncdb --noinput".format(django_dir))

    try:

        if settings.GC_DEBUG:
            import gc
            gc.set_debug(gc.DEBUG_LEAK)

    except Exception as e:
        msg = "ERROR: Failed to set garbage collection debugging: {0}".format(str(e))
        logger.error(msg)
        logger.debug(traceback.format_exc())

    try:

        app = EF5()

        sockets = set()
        for port in settings.PORTS:
            logger.info("STARTUP: binding server on port {0}".format(port))
            s = set(tornado.netutil.bind_sockets(port))
            sockets = sockets.union(s)

        for handler in bind_handlers:
            ioloop.IOLoop.instance().add_handler(*handler)

        # Instantiate server
        http_server = EF5HttpsServer(app, xheaders=True)  # , max_body_size=settings.MAX_BODY_SIZE)
        http_server.add_sockets(sockets)

    except Exception as e:
        msg = "ERROR: Failed to initialize server: {0}".format(str(e))
        logger.error(msg)
        logger.error(traceback.format_exc())
        return

    try:

        logger.info("STARTUP: starting server...")
        ioloop.IOLoop.instance().start()
        logger.info("SHUTDOWN: server shutting down...")

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt detected")
        tornado.ioloop.IOLoop.instance().add_callback(ioloop.IOLoop.instance().stop)
    except Exception as e:
        msg = "An error was detected while starting the server: {0}".format(str(e))
        logger.error(msg)
        logger.error(traceback.format_exc())
        tornado.ioloop.IOLoop.instance().add_callback(ioloop.IOLoop.instance().stop)
    finally:
        logger.info("Exiting...")
        if ioloop.IOLoop.instance().initialized():
            ioloop.IOLoop.instance().close(all_fds=False)
        os._exit(0)

if __name__ == "__main__":
    start_app()
