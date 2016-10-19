from __future__ import unicode_literals
import tornado.web


class APIError(tornado.web.HTTPError):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None, *args, **kwargs):
        super(APIError, self).__init__(status_code, *args, **kwargs)
        self.message = message
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv
