import hashlib
import logging
import urllib

from google.appengine.ext import webapp

def gravatar(user, size=16):
	url = 'http://www.gravatar.com/avatar/' + hashlib.md5(user.email().lower()).hexdigest() + '?s=' + str(size)
	return url

register = webapp.template.create_template_register()
register.filter(gravatar)
