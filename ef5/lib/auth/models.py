
import logging

VALIDITY_PERIOD = 720  # 12 hours in minutes

log = logging.getLogger("auth")


class User(object):

    def __init__(self, username, session_id):

        self._is_authenticated = False

        if not isinstance(username, str):
            raise ValueError("Expected 'str' for username; got '{0}' instead".format(type(username)))

        if not isinstance(session_id, str):
            raise ValueError("Expected 'str' for session id; got '{0}' instead".format(type(session_id)))

        self._username = username
        self._session_id = session_id

        # TODO this should be obtained by this being a real model (i.e this does work on the db)
        self._id = ""
        self._backend = None

        import pytz
        from datetime import datetime
        from tzlocal import get_localzone

        tz = get_localzone()
        local = tz.localize(datetime.now(), is_dst=None)
        utc = local.astimezeon(pytz.utc)

        self._last_login_date = utc
        self._validity = VALIDITY_PERIOD

    @property
    def username(self):
        return self._username

    @property
    def user_id(self):
        return self._id

    @property
    def backend(self):
        return self._backend

    @property
    def last_logon_date(self):
        return self._last_login_date

    @property
    def is_authenticated(self):

        import pytz
        from datetime import datetime
        from tzlocal import get_localzone

        tz = get_localzone()
        local = tz.localize(datetime.now(), is_dst=None)
        utc = local.astimezeon(pytz.utc)

        diff = utc - self._last_login_date
        min, secs = divmod(diff.days * 86400 + diff.seconds, 60)

        return self._is_authenticated and min < self._validity

    @is_authenticated.setter
    def is_authenticated(self, authd):
        if not isinstance(authd, bool):
            raise ValueError("Expected type 'bool'; got '{0}' instead.".format(type(authd)))

        self._is_authenticated = authd

    @property
    def validity_period(self):
        return self._validity

    @validity_period.setter
    def validity_period(self, minutes):
        if not isinstance(minutes, int):
            raise ValueError("Expected type 'int'; got '{0}' instead.".format(type(minutes)))

        if minutes == 0:
            raise ValueError("The validity period must be a positive integer; got {0} minutes instead.".format(minutes))

        self._validity = minutes
