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

def plural(number, arg):
	"""
	Поддержка русских числительных.  Фильтр применяется к числу, в качестве
	параметра используется строка, содержащая — через запятую — формы слова
	для единицы, двойки и пятёрки.  Пример:

	{{ n.likes|plural:"голос,голоса,голосов" }}
	"""
	words = arg.split(',')
	suffix = int(str(number)[-1])
	if siffux == 1:
		return words[0]
	elif suffix > 1 and suffix < 5:
		return words[1]
	return words[2]

register = webapp.template.create_template_register()
register.filter(gravatar)
register.filter(sitename)
register.filter(plural)
