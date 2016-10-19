from __future__ import unicode_literals

import unittest

import tornado.testing
import simplejson as json

from server import make_app
from db import users


class TestServerApp(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return make_app()

    def post_json(self, url, data):
        body = json.dumps(data)
        response = self.fetch(url, method='POST', headers={'Content-Type': 'application/json'}, body=body)
        return response, json.loads(response.body)

    def test_homepage(self):
        response = self.fetch('/')
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, 'OK')

    def test_jwt_required_decorator_with_valid_request_current_identity(self):
        user = users[0]
        data = {
            'credential': {
                'username': user.username,
                'password': user.password
            },
            'type': 'username'
        }
        resp, resp_data = self.post_json('/auth/login/', data)
        self.assertEqual(resp.code, 200)
        token = resp_data['access_token']
        self.assertTrue(token)
        resp = self.fetch('/auth/info/', headers={'authorization': 'Bearer ' + token})
        resp_data = json.loads(resp.body)
        self.assertEqual(resp_data['username'], user.username)
        self.assertEqual(resp_data['id'], user.id)


if __name__ == '__main__':
    unittest.main()
