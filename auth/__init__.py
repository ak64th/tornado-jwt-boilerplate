# coding=utf-8
from __future__ import unicode_literals

import jwt
import six
import tornado.options
from datetime import datetime

from core import APIError
from core import JsonHandler
from db import user_index, username_index


def request_callback(request):
    auth_header_value = request.headers.get('Authorization', None)
    auth_header_prefix = tornado.options.options.jwt_auth_header_prefix

    if not auth_header_value:
        return

    parts = auth_header_value.split()

    if parts[0].lower() != auth_header_prefix.lower():
        raise APIError('Unsupported authorization type')
    elif len(parts) == 1:
        raise APIError('Token missing')
    elif len(parts) > 2:
        raise APIError('Token contains spaces')

    return parts[1]


def _jwt_required(self):
    token = request_callback(self.request)

    if token is None:
        raise APIError('Authorization Required')

    secret = tornado.options.options.jwt_secret_key
    algorithm = tornado.options.options.jwt_algorithm
    leeway = tornado.options.options.jwt_leeway
    verify_claims = tornado.options.options.jwt_verify_claims
    required_claims = tornado.options.options.jwt_required_claims

    try:
        options = {'verify_' + claim: True for claim in verify_claims}
        options.update({'require_' + claim: True for claim in required_claims})
        payload = jwt.decode(token, secret, options=options, algorithms=[algorithm], leeway=leeway)
    except jwt.InvalidTokenError as e:
        raise APIError('Invalid token: {}'.format(e.message))

    user_id = payload['identity']
    self.request.identity = identity = user_index.get(user_id, None)
    if identity is None:
        raise APIError('User does not exist')


def jwt_required():
    def wrapper(fn):
        @six.wraps(fn)
        def decorator(self, *args, **kwargs):
            _jwt_required(self)
            return fn(self, *args, **kwargs)

        return decorator

    return wrapper


def username_login_callback(username, password):
    user = username_index.get(username, None)
    if user and user.password.encode('utf-8') == password.encode('utf-8'):
        return user
    return {}


def jwt_encode_callback(identity):
    secret = tornado.options.options.jwt_secret_key
    algorithm = tornado.options.options.jwt_algorithm

    iat = datetime.utcnow()
    exp = iat + tornado.options.options.jwt_expiration_delta
    nbf = iat + tornado.options.options.jwt_not_before_delta
    identity = getattr(identity, 'id') or identity['id']
    payload = {'exp': exp, 'iat': iat, 'nbf': nbf, 'identity': identity}
    return jwt.encode(payload, secret, algorithm=algorithm)


class LoginHandler(JsonHandler):
    def post(self):
        try:
            data = self.parse_json()
            credential_type = data.get('type')
            credential = data.get('credential')
        except AttributeError:
            raise APIError('Invalid credentials')

        if credential_type == 'username':
            identity = username_login_callback(**credential)
        else:
            raise NotImplementedError

        if identity:
            access_token = jwt_encode_callback(identity)
            self.write_json({'access_token': access_token.decode('utf-8')})
        else:
            raise APIError('Invalid credentials')


class InfoHandler(JsonHandler):
    @jwt_required()
    def get(self):
        user = self.request.identity
        self.write_json({'id': user.id, 'username': user.username})


class RefreshHandler(JsonHandler):
    @jwt_required()
    def get(self):
        access_token = jwt_encode_callback(self.request.identity)
        self.write_json({'access_token': access_token.decode('utf-8')})
