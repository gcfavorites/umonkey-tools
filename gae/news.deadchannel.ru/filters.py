import hashlib
import logging
import urllib
import urlparse

from google.appengine.ext import webapp

def gravatar(user, size=16):
	url = 'http://www.gravatar.com/avatar/' + hashlib.md5(user.email().lower()).hexdigest() + '?s=' + str(size)
	return url

def sitename(url):
	netloc = urlparse.urlparse(url).netloc
	host = '.'.join(netloc.split('.')[-2:])
	if host in ('co.uk'):
		host = '.'.join(netloc.split('.')[-3:])
	return host

register = webapp.template.create_template_register()
register.filter(gravatar)
register.filter(sitename)
