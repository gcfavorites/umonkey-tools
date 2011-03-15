#!/usr/bin/env python
# vim: fileencoding=utf-8:

"""Megaplan client module.

Example usage:

    import megaplan
    c = megaplan.Client('xyz.megaplan.ru')
    access_id, secret_key = c.authenticate(login, password)
    for task in c.get_actual_tasks():
        print task

Example usage without logging in:

    import megaplan
    c = megaplan.Client('xyz.megaplan.ru', access_id, secret_key)
    for task in c.get_actual_tasks():
        print task
"""

import base64
import hashlib
import hmac
import simplejson
import time
import urllib
import urllib2

class Request:
    def __init__(self, hostname, access_id, secret_key, uri, data=None):
        self.method = 'POST'
        self.proto = 'https'
        self.uri = hostname +'/'+ uri
        self.access_id = access_id
        self.secret_key = secret_key
        self.content_type = 'application/x-www-form-urlencoded'
        self.date = time.strftime('%a, %d %b %Y %H:%M:%S +0000', time.gmtime())
        self.signature = None
        self.data = data

    def sign(self):
        text = '\n'.join([self.method, '', self.content_type, self.date, self.uri])
        self.signature = base64.b64encode(hmac.new(self.secret_key, text, hashlib.sha1).hexdigest())

    def send(self):
        url = self.proto + '://' + self.uri
        data = self.data and urllib.urlencode(self.data)

        req = urllib2.Request(url, data)
        req.add_header('Date', self.date)
        req.add_header('Accept', 'application/json')
        req.add_header('User-Agent', 'SdfApi_Request')
        if self.signature:
            req.add_header('X-Authorization', self.access_id + ':' + self.signature)

        res = urllib2.urlopen(req)
        data = simplejson.loads(res.read())
        if data['status']['code'] != 'ok':
            raise Exception(data['status']['message'])

        return data['data']


class Client:
    def __init__(self, hostname, access_id=None, secret_key=None):
        self.hostname = hostname
        self.access_id = access_id
        self.secret_key = secret_key

    def authenticate(self, login, password):
        data = self.request('BumsCommonApiV01/User/authorize.api', { 'Login': login, 'Password': hashlib.md5(password).hexdigest() })
        self.access_id = data['AccessId']
        self.secret_key = data['SecretKey']
        return self.access_id, self.secret_key

    def request(self, uri, args=None, signed=True):
        req = Request(self.hostname, self.access_id, self.secret_key, uri, args)
        if signed:
            req.sign()
        return req.send()

    # SOME HELPER METHODS

    def get_actual_tasks(self):
        return self.request('BumsTaskApiV01/Task/list.api', { 'Status': 'actual' })['tasks']
