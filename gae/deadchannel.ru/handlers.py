# -*- coding: utf-8 -*-
# vim: set ts=4 sts=4 sw=4 noet:

# Python imports
import datetime
import logging
import os
import urllib
import urllib2
import urlparse
import wsgiref.handlers

# GAE imports
from google.appengine.ext.webapp.util import login_required
from google.appengine.api import mail
from google.appengine.api import memcache
from google.appengine.api import urlfetch
from google.appengine.api import users
from google.appengine.api.labs import taskqueue
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

# Site imports.
import config
import model
import oauth

class BaseRequestHandler(webapp.RequestHandler):
	def render(self, template_name, vars={}, ret=False, mime_type='text/html'):
		u"""
		Вызывает указанный шаблон, возвращает результат.
		"""
		vars['base'] = self.getBaseURL()
		vars['self'] = self.request.uri
		vars['host'] = self.getHost()
		#vars['styles'] = self.get_styles(vars['host'])
		#vars['scripts'] = self.get_scripts(vars['host'])
		#vars['logout_uri'] = users.create_logout_url(self.request.uri)
		#vars['login_uri'] = users.create_login_url(self.request.uri)
		directory = os.path.dirname(__file__)
		path = os.path.join(directory, 'templates', template_name)
		response = template.render(path, vars)
		if not ret:
			self.response.headers['Content-Type'] = mime_type + '; charset=utf-8'
			self.response.out.write(response)
		return response

	def getBaseURL(self):
		"""
		Возвращает базовый адрес текущего сайта.
		"""
		url = urlparse.urlparse(self.request.url)
		return url[0] + '://' + url[1] + '/'

	def getHost(self):
		url = urlparse.urlparse(self.request.url)
		return url[1]


class IndexHandler(BaseRequestHandler):
	"""
	Вывод главной страницы.  Выводит 20 ближайших событий через шаблон
	index.html.
	"""
	def get(self):
		now = datetime.datetime.now()
		events = model.Event.gql('WHERE date > :1 ORDER BY date', now).fetch(20)
		gaid = hasattr(config, 'GA_ID') and config.GA_ID or None
		self.render('index.html', {
			'events': events,
			'status': {
				'subscribed': self.request.get('status') == 'subscribed',
			},
			'gaid': gaid,
		})


class SubmitHandler(BaseRequestHandler):
	"""
	Добавление события в список.  Если событие с таким URL уже есть,
	обвновляется информация о существующем.  После обработки данных
	пользователя отправляют на главную страницу.
	"""
	def get(self):
		self.render('submit.html')

	def post(self):
		date = datetime.datetime.strptime(self.request.get('date'), '%Y-%m-%d %H:%M')
		title = self.request.get('title')
		url = self.request.get('url')
		event = model.Event.gql('WHERE url = :1', url).get()
		if event is None:
			event = model.Event(user=users.get_current_user(), url=url, far_sent=False, soon_sent=False)
		event.date = date
		event.title = title
		event.put()
		self.redirect('/')


class SubscribeHandler(BaseRequestHandler):
	"""
	Добавление данных в список рассылки.  Обрабатывает параметры email и phone,
	сохраняя их как одноимённые объекты.  Существующие объекты не дублируются.
	"""
	def post(self):
		if self.request.get('remove'):
			return self.remove()
		else:
			return self.add()

	def add(self):
		next = '/'
		email = self.request.get('email')
		if email:
			obj = model.Email.gql('WHERE email = :1', email).get()
			if obj is None:
				obj = model.Email(email=email)
				obj.put()
			next = '/?status=subscribed'
		phone = self.request.get('phone')
		if phone:
			# Коррекция формата номера.
			if phone.startswith('8'): phone = '+7' + phone[1:]
			phone = phone.replace(' ', '')
			obj = model.Phone.gql('WHERE phone = :1', phone).get()
			if obj is None:
				obj = model.Phone(phone=phone)
				obj.put()
			next = '/?status=subscribed'
		self.redirect(next)

	def remove(self):
		email = self.request.get('email', 'n/a')
		phone = self.request.get('phone', 'n/a')
		text = 'Email: %s\nPhone: %s' % (email, phone)
		mail.send_mail(sender='justin.forest@gmail.com', to='justin.forest@gmail.com', subject='Unsubscribe request', body=text)


class CronHandler(BaseRequestHandler):
	"""
	Находит события, по которым ещё не были отправлены уведомления, но уже
	пора, и добавляет их в очередь.  Количество дней, за которое отправляется
	уведомление, настраивается в файле config.py, параметрами FAR_LIMIT и
	SOON_LIMIT.

	При отправке уведомлений выбираются все события, до которых осталось менее
	определённого времени (FAR_LIMIT или SOON_LIMIT).  При том, что обработчик
	вызывается каждый час, получается, что при SOON_LIMIT уведомления
	отправляются для событий, до которых осталось от 23 до 24 часов.
	"""
	def get(self):
		emails = model.Email.all().fetch(1000)
		phones = model.Phone.all().fetch(1000)
		count = 0 # количество поставленных в очередь событий
		now = datetime.datetime.now()

		# Отправка уведомлений за неделю
		d1 = now + datetime.timedelta(config.FAR_LIMIT)
		for event in model.Event.gql('WHERE far_sent = :1 AND date < :2 AND date > :3', False, d1, now).fetch(10):
			count += self.notify(event, emails, phones)
			event.far_sent = True
			event.put()

		# Отправка уведомлений за сутки
		d1 = now + datetime.timedelta(config.SOON_LIMIT)
		for event in model.Event.gql('WHERE soon_sent = :1 AND date < :2 AND date > :3', False, d1, now).fetch(10):
			count += self.notify(event, emails, phones)
			event.soon_sent = True
			event.far_sent = True
			event.put()

		if count:
			logging.info('Queued %u notifications.' % count)

	def notify(self, event, emails, phones):
		count = 0
		twit_event(event)
		for email in emails:
			taskqueue.Task(url='/notify', params={ 'event': event.key(), 'email': email.email }).add()
			count += 1
		for phone in phones:
			taskqueue.Task(url='/notify', params={ 'event': event.key(), 'phone': phone.phone }).add()
			count += 1
		return count


class NotifyHandler(BaseRequestHandler):
	"""
	Отправка сообщений подписчикам.  Используется вместе с TaskQueue, один
	запрос отправляет одно сообщение, на email или телефон.  Параметры email
	или phone содержат адреса получателей, параметр event содержит ключ записи.

	SMS отправляется через sms.ru, ключ API указывается в файле config.py,
	через переменную SMS_ID, вот так:

	SMS_ID = 'xyz'
	"""
	def post(self):
		try:
			event = model.Event.get(self.request.get('event'))
			if 'phone' in self.request.arguments():
				self.notify_phone(event, self.request.get('phone'))
			elif 'email' in self.request.arguments():
				self.notify_email(event, self.request.get('email'))
		except Exception, e:
			logging.error('Notification failed: %s' % e)
			self.response.set_status(500)
			self.response.out.write(str(e))

	def notify_phone(self, event, phone):
		date = event.date.strftime('%d.%m')
		time = event.date.strftime('%H:%M')
		text = u'%s в %s %s, см. deadchannel.ru' % (date, time, event.title)
		options = {
			'api_id': config.SMS_ID,
			'to': phone,
			'text': text.encode('utf-8'),
		}
		if hasattr(config, 'SMS_FROM'):
			options['from'] = config.SMS_FROM
		self.fetch('http://sms.ru/sms/send', options)
		logging.info('Sent an SMS to %s' % phone)

	def notify_email(self, event, email):
		date = event.date.strftime('%d.%m.%Y')
		time = event.date.strftime('%H:%M')
		text = u"Привет.\n\nНапоминаю, что %s в %s состоится мероприятие: %s.\n\nПодробности:\n%s" % (date, time, event.title, event.url)
		html = u"<p>Привет.</p><p>Напоминаю, что %s в %s состоится мероприятие: <a href=\"%s\">%s</a>.</p><p>Подробности:<br/>%s</p>" % (date, time, event.url, event.title, event.url)

		# http://code.google.com/intl/ru/appengine/docs/python/mail/emailmessagefields.html
		mail.send_mail(sender='justin.forest@gmail.com', to=email, subject=u'Напоминание о событии', body=text, html=html)

	def fetch(self, url, data=None):
		if data is not None:
			url += '?' + urllib.urlencode(data)
		result = urlfetch.fetch(url)
		if result.status_code != 200:
			raise Exception('Could not fetch ' + url)


class ListHandler(BaseRequestHandler):
	"""
	Выводит список всех подписчиков в формате CSV.
	"""
	def get(self):
		text = ''
		mails = phones = 0
		for email in model.Email.all().order('email').fetch(1000):
			date = email.date_added.strftime('%Y-%m-%d')
			text += '%s,%s,\n' % (date, email.email)
			mails += 1
		for phone in model.Phone.all().order('phone').fetch(1000):
			date = email.date_added.strftime('%Y-%m-%d')
			text += '%s,,%s\n' % (date, phone.phone)
			phones += 1
		header = 'added on,email (%u),phone (%u)\n' % (mails, phones)
		self.response.headers['Content-Type'] = 'text/plain'
		self.response.out.write(header + text)


class RSSHandler(BaseRequestHandler):
	"""
	Выводит RSS ленту со всеми событиями.  В будущем можно будет придумать фильтрацию.
	"""
	def get(self):
		self.render('rss.xml', {
			'events': model.Event.all().order('-date').fetch(1000),
		}, mime_type='text/xml')


class CalHandler(BaseRequestHandler):
	"""
	Выводит календарь со всеми событиями.
	"""
	def get(self):
		text = u'BEGIN:VCALENDAR\n'
		text += u'VERSION:2.0\n'
		text += u'PRODID:-//hacksw/handcal//NONSGML v1.0//EN\n'
		text += u'CALSCALE:GREGORIAN\n'
		text += u'X-WR-CALNAME:Санкт-Петербург\n'
		text += u'X-WR-TIMEZONE:Europe/Moscow\n'
		text += u'X-WR-CALDESC:Афиша тёмной сцены Санкт-Петербурга.\n'
		for event in model.Event.all().order('-date').fetch(1000):
			text += u'BEGIN:VEVENT\n'
			text += u'DTSTAMP:%sZ\n' % event.date.strftime('%Y%m%dT%H%M%S')
			text += u'DTSTART:%sZ\n' % event.date.strftime('%Y%m%dT%H%M%S')
			text += u'SUMMARY:%s\n' % event.title.replace(',', '\\,')
			text += u'DESCRIPTION:%s\n' % event.url
			text += u'END:VEVENT\n'
		text += u'END:VCALENDAR\n'
		self.response.headers['Content-Type'] = 'text/calendar; charset=utf-8'
		self.response.out.write(text)


def shorten_url(url):
	"""
	Возвращает сокращённый адрес страницы.  Если сокращение не работает —
	возвращает исходный адрес.
	"""
	args = { 'login': config.BITLY_NAME, 'apiKey': config.BITLY_KEY, 'domain': 'j.mp', 'format': 'txt', 'longUrl': url }
	url = 'http://api.bit.ly/v3/shorten?' + urllib.urlencode(args)
	result = urlfetch.fetch(url)
	if result.status_code != 200:
		return args['longUrl']
	return result.content


def twit(message):
	"""
	Отправляет в твиттер произвольное сообщение.
	"""
	client = oauth.TwitterClient(config.TWITTER_CONSUMER_KEY, config.TWITTER_CONSUMER_SECRET, 'http://www.deadchannel.ru/verify')
	result = client.make_request('http://twitter.com/statuses/update.json',
		token=config.TWITTER_ACCESS_TOKEN_KEY,
		secret=config.TWITTER_ACCESS_TOKEN_SECRET,
		additional_params={'status':message},
		method=urlfetch.POST)


def twit_event(event):
	"""
	Отправляет в twitter сообщение о событии.
	"""
	date = event.date.strftime('%d.%m')
	time = event.date.strftime('%H:%M')
	text = u'%s в %s, %s. %s' % (date, time, event.title, shorten_url(event.url))
	twit(text)


if __name__ == '__main__':
	wsgiref.handlers.CGIHandler().run(webapp.WSGIApplication([
		('/', IndexHandler),
		('/all.ics', CalHandler),
		('/cron', CronHandler),
		('/list.csv', ListHandler),
		('/notify', NotifyHandler),
		('/rss.xml', RSSHandler),
		('/submit', SubmitHandler),
		('/subscribe', SubscribeHandler),
	], debug=config.DEBUG))
