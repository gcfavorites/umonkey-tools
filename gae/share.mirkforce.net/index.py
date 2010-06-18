# -*- coding: utf-8 -*-

# Python imports
import base64
import datetime
import hmac
import hashlib
import logging
import os
import urlparse
import wsgiref.handlers

# GAE imports
from google.appengine.api import memcache
from google.appengine.api import urlfetch
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

import config

class File(db.Model):
	user = db.UserProperty(required=True)
	added = db.DateTimeProperty(auto_now_add=True, required=True)
	url = db.LinkProperty(required=True)
	mime_type = db.StringProperty(required=True)
	size = db.IntegerProperty(required=True)
	description = db.TextProperty()

class BaseRequestHandler(webapp.RequestHandler):
	def __init__(self):
		pass

	def XXX_handle_exception(self, e, debug_mode):
		if not issubclass(e.__class__, acl.HTTPException):
			return webapp.RequestHandler.handle_exception(self, e, debug_mode)

		if e.code == 401:
			self.redirect(users.create_login_url(self.request.url))
		else:
			self.error(e.code)
			self.generate('error.html', template_values={
				'settings': self.settings.dict(),
				'code': e.code,
				'title': e.title,
				'message': e.message,
			})

	def generateRss(self, template_name, template_values={}):
		template_values['self'] = self.request.url
		url = urlparse.urlparse(self.request.url)
		template_values['base'] = url[0] + '://' + url[1]
		self.response.headers['Content-Type'] = 'text/xml'
		return self.generate(template_name, template_values)

	def generate(self, template_name, template_values={}, ret=False):
		"""Generate takes renders and HTML template along with values
			 passed to that template

			 Args:
				 template_name: A string that represents the name of the HTML template
				 template_values: A dictionary that associates objects with a string
					 assigned to that object to call in the HTML template.	The defualt
					 is an empty dictionary.
		"""
		# We check if there is a current user and generate a login or logout URL
		user = users.get_current_user()

		if user:
			log_in_out_url = users.create_logout_url(self.request.path)
		else:
			log_in_out_url = users.create_login_url(self.request.path)

		# We'll display the user name if available and the URL on all pages
		values = {'user': user, 'log_in_out_url': log_in_out_url, 'editing': self.request.get('edit'), 'is_admin': users.is_current_user_admin() }
		url = urlparse.urlparse(self.request.url)
		values['base'] = url[0] + '://' + url[1]
		values.update(template_values)

		# Construct the path to the template
		directory = os.path.dirname(__file__)
		path = os.path.join(directory, 'templates', template_name)

		result = template.render(path, values)
		if ret:
			return result

		# Respond to the request by rendering the template
		self.response.out.write(result)

class IndexHandler(BaseRequestHandler):
	def get(self):
		username = self.request.get('user')

		mk = 'index:' + username
		files = memcache.get(mk)
		if files is None:
			if username:
				files = File.gql('WHERE user = :1 ORDER BY added DESC', users.User(username + '@gmail.com'))
			else:
				files = File.all().order('-added')
			memcache.set(mk, files)

		result = self.generate('index.html', template_values={
			'files': [{ 'owner': f.user.nickname(), 'url': f.url, 'name': urlparse.urlparse(f.url).path.split('/')[-1], 'size': f.size, 'type': f.mime_type, 'date': str(f.added)[:16] } for f in files.fetch(100)],
			'form': self.get_upload_form(),
		}, ret=True)

		self.response.out.write(result)

	def get_upload_form(self):
		user = users.get_current_user()
		if user is not None and users.is_current_user_admin():
			path = user.nickname() + '/' + datetime.datetime.now().strftime('%Y/%m/%d/')

			base = urlparse.urlparse(self.request.url)
			base = base[0] + '://' + base[1] + '/'

			policy_src = {
				'expiration': (datetime.datetime.now() + datetime.timedelta(hours=1)).isoformat() + 'Z',
				'conditions': [
					{ 'acl': 'public-read' },
					{ 'bucket': config.S3_BUK },
					[ 'starts-with', '$key', path ],
					[ 'starts-with', '$success_action_redirect', base ],
				],
			}
			policy_enc = base64.b64encode(unicode(policy_src).encode('utf-8'))

			return {
				'bucket': config.S3_BUK,
				'access_key': config.S3_PUB,
				'key': path + '${filename}',
				'policy': policy_enc,
				'signature': base64.b64encode(hmac.new(config.S3_PRI, policy_enc, hashlib.sha1).digest()),
				'base': base,
				'owner': user.nickname(),
			}

class SubmitHandler(BaseRequestHandler):
	"""
	Adds one file to the database. URL can be passed either with the 'url'
	parameter (full form), or with parameters 'bucket' and 'key' (S3 callback).

	The file is HEAD-ed to find mime type and size and added to the datastore
	if oll is klear, then the user is redirected to the main page.
	"""
	def get(self):
		url = (self.request.get('url') or 'http://' + self.request.get('bucket') + '/' + self.request.get('key')).strip()
		# Make sure the file does not exist.
		if File.gql('WHERE url = :1', url).get() is None:
			logging.info('URL submitted: ' + url)
			head = urlfetch.fetch(url=url, method=urlfetch.HEAD)
			if head.status_code != 200:
				raise Exception('Could not check %s, must be an invalid url.')
			f = File(user=users.get_current_user(), url=url, mime_type='binary/octet-stream', size=0)
			if 'Content-Length' in head.headers:
				f.size = int(head.headers['Content-Length'])
			if 'Content-Type' in head.headers:
				f.mime_type = head.headers['Content-Type']
			f.put()
			# Flush caches.
			memcache.delete('index:')
			memcache.delete('index:' + f.user.nickname())
		else:
			logging.info('URL submitted: ' + url + ' (again)')
		self.redirect('/')

if __name__ == '__main__':
	application = webapp.WSGIApplication([
	('/', IndexHandler),
	('/submit', SubmitHandler),
	], debug=hasattr(config, 'DEBUG') and config.DEBUG)
	wsgiref.handlers.CGIHandler().run(application)
