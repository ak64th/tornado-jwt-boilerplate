# coding=utf-8
from __future__ import unicode_literals
import simplejson as json
import tornado.web

from core.exceptions import APIError


_missing = object()


class JsonHandler(tornado.web.RequestHandler):
    """Request handler where requests and responses speak JSON."""
    def data_received(self, chunk):
        pass

    def parse_json(self):
        rv = getattr(self, '_cached_json', _missing)
        if rv is not _missing:
            return rv

        if self.request.body:
            try:
                rv = json.loads(self.request.body)
                setattr(self, '_cached_json', rv)
                return rv
            except ValueError:
                raise APIError('Unable to parse JSON', status_code=400)

    def write_json(self, data):
        output = json.dumps(data)
        self.write(output)

    def prepare(self):
        self.parse_json()

    def set_default_headers(self):
        self.set_header(b'Content-Type', 'application/json')

    def write_error(self, status_code, **kwargs):
        if 'exc_info' in kwargs:
            exc = kwargs['exc_info'][1]
            if isinstance(exc, APIError):
                self.write_json(exc.to_dict())
                self.finish()
            elif isinstance(exc, tornado.web.HTTPError):
                self.write_json(dict(message=self._reason))
                self.finish()
        if not self._finished:
            super(JsonHandler, self).write_error(status_code, **kwargs)


class MainHandler(JsonHandler):
    def get(self):
        self.write('OK')
