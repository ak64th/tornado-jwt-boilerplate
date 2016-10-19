#!/usr/bin/env python
from __future__ import print_function
from __future__ import unicode_literals

import os
from datetime import timedelta

import six
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options

import core
import auth

define('debug', default=True, type=bool)
define('port', default=5001, type=int)

define('jwt_secret_key', type=six.string_types)
define('jwt_algorithm', default='HS256', type=six.string_types)
define('jwt_leeway', default=timedelta(seconds=10), type=timedelta)
define('jwt_auth_header_prefix', default='Bearer', type=six.string_types)
define('jwt_expiration_delta', default=timedelta(seconds=300), type=timedelta)
define('jwt_not_before_delta', default=timedelta(seconds=0), type=timedelta)
define('jwt_verify_claims', default=['signature', 'exp', 'nbf', 'iat'], multiple=True, type=six.string_types)
define('jwt_required_claims', default=['exp', 'nbf', 'iat'], multiple=True, type=six.string_types)


def parse_config():
    config_path = os.environ.get('CAS_CONFIG_PATH', 'config.py')
    tornado.options.parse_config_file(config_path)
    tornado.options.parse_command_line()


def make_app():
    parse_config()
    settings = dict(debug=options.debug)

    handlers = [
        (r'/', core.MainHandler),
        (r'/auth/login/', auth.LoginHandler),
        (r'/auth/info/', auth.InfoHandler),
        (r'/auth/refresh/', auth.RefreshHandler),
    ]

    return tornado.web.Application(handlers, **settings)


def main():
    application = make_app()

    print('')
    print('----------------------------------------------')
    print('- serve on 127.0.0.1:%s...                 -' % (options.port,))
    print('----------------------------------------------')
    print('- Conception Proof Only                      -')
    print('----------------------------------------------')
    print('')

    application.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
