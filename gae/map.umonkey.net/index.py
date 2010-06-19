# vim: set ts=4 sts=4 sw=4 noet fileencoding=utf-8:

import csv
import logging
import os
import sys
import urlparse
import wsgiref.handlers
from xml.sax.saxutils import escape as quoteattr

from google.appengine.api import urlfetch
from google.appengine.ext import db
from google.appengine.ext import webapp

from django.utils import simplejson

CSV_URL = 'http://spreadsheets.google.com/pub?key=0Ai-BMIF8tVI3dERnZ2FtdkNMOE5xTGVPSjBMUzcwUFE&hl=en&single=true&gid=0&output=csv'
CSV_FIELDS = ('name', 'region', 'area', 'is_open', 'founded', 'families', 'winter', 'avg', 'price', 'ownership', 'residence', 'communication', 'internet', 'electricity', 'water', 'url', 'url_own', 'url_vk', 'lat', 'lon')

class Settlement(db.Model):
	# название поселения
	name = db.StringProperty()
	# область
	region = db.StringProperty()
	# площадь поселения
	area = db.FloatProperty()
	# принимаются ли желающие
	is_open = db.BooleanProperty()
	# год основания
	founded = db.IntegerProperty()
	# количество семей
	families = db.IntegerProperty()
	# количество зимующих семей
	winter = db.IntegerProperty()
	# средний размер участка, га
	avg = db.FloatProperty()
	# стоимость вступления
	price = db.IntegerProperty()
	# земля в собственность
	ownership = db.BooleanProperty()
	# возможность прописки
	residence = db.BooleanProperty()
	# сотовая связь
	communication = db.BooleanProperty()
	# интернет
	internet = db.BooleanProperty()
	# электричество
	electricity = db.BooleanProperty()
	# водопровод
	water = db.BooleanProperty()
	# адрес на poselenia.ru
	url = db.LinkProperty()
	# адрес вконтакте
	url_vk = db.LinkProperty()
	# адрес собственного сайта
	url_own = db.LinkProperty()
	# координаты
	ll = db.GeoPtProperty()

class UpdateHandler(webapp.RequestHandler):
	def get(self):
		data = self.convert_to_objects(self.fetch())
		logging.info('Done.')
		self.response.out.write(unicode(data))

	def convert_to_objects(self, rows):
		logging.info('Deleting old settlements.')
		db.delete(Settlement.all().fetch(1000))
		logging.info('Adding %u new ones.' % len(rows))
		for obj in rows:
			self.convert_to_object(obj).put()

	def convert_to_object(self, entry):
		converters = { 'area': lambda x: float(x.strip(u'га').replace(',', '.')), 'avg': float, 'families': int, 'winter': int, 'founded': int, 'price': int }
		obj = Settlement()
		for k in entry:
			if entry[k] is not None and hasattr(obj, k):
				try:
					setattr(obj, k, converters.has_key(k) and converters[k](entry[k]) or entry[k])
				except Exception, e:
					logging.error(('%s (value: %s, type: %s)' % (e, unicode(entry[k]), entry[k].__class__)).encode('utf-8'))
			if entry['lat'] and entry['lon']:
				try: obj.ll = entry['lat'] + ',' + entry['lon']
				except Exception, e: logging.error(('Error setting location: %s: %s, %s' % (e, entry['lat'], entry['lon'])).encode('utf-8'))
		return obj

	def fetch(self):
		logging.info('Fetching CSV data.')
		raw_data = urlfetch.fetch(CSV_URL).content
		return [self.convert_row(cells) for cells in csv.reader(raw_data.split('\n')[1:])]

	def convert_row(self, cells):
		return dict([(CSV_FIELDS[idx], idx<len(cells) and self.fix_cell(cells[idx].decode('utf-8')) or None) for idx in range(len(CSV_FIELDS))])

	def fix_cell(self, value):
		if value == u'да':
			return True
		if value in (u'нет', u'плохая', u'у некоторых', u'обсуждается'):
			return False
		if value.isnumeric():
			return int(value)
		return value

class IndexHandler(webapp.RequestHandler):
	def get(self):
		data = {
			'bounds': {
				'latmin': 1000,
				'latmax': 0,
				'lonmin': 1000,
				'lonmax': 0,
			},
			'markers': self.get_markers(),
		}

		for marker in data['markers']:
			if marker['ll']:
				data['bounds']['latmin'] = min(marker['ll'][0], data['bounds']['latmin'])
				data['bounds']['lonmin'] = min(marker['ll'][0], data['bounds']['lonmin'])
				data['bounds']['latmax'] = max(marker['ll'][0], data['bounds']['latmax'])
				data['bounds']['lonmax'] = max(marker['ll'][0], data['bounds']['lonmax'])

		html = self.render_template('index.html', { 'data': simplejson.dumps(data) })

		self.response.headers['Content-Type'] = 'text/html'
		self.response.out.write(html)

	def get_markers(self):
		objects = [obj for obj in Settlement.all().fetch(1000) if obj.ll]

		converters = { 'll': lambda x: (x.lat, x.lon) }
		convert = lambda key, val: converters.has_key(key) and converters[key](val) or val
		markers = [dict([(x, getattr(obj, x) and convert(x, getattr(obj, x))) for x in obj.fields()]) for obj in objects]

		# Добавление HTML блоков.
		markers = [self.render_one(marker) for marker in markers]

		return markers

	def render_one(self, marker):
		html = u'<p class="name"><span>%s</span>%s</p>' % (marker['name'], marker['region'] and u' (%s)' % marker['region'] or u'')
		# Описание.
		html += u'<p>'
		if marker['founded']:
			html += u'Основано в %sг. ' % marker['founded']
		tmp = []
		if marker['area']:
			tmp.append(u'%sга' % marker['area'])
		if marker['families']:
			tmp.append(u'%s семей' % marker['families'])
		if len(tmp):
			html += u', '.join(tmp) + u'. '
		if marker['ownership']:
			html += u'Земля в собственность. '
		if marker['residence']:
			html += u'Жилой дом с правом прописки. '
		tmp = []
		for k in (('electricity', u'электричество'), ('water', u'водопровод'), ('communication', u'сотовая связь'), ('internet', u'интернет')):
			if marker[k[0]]:
				tmp.append(k[1])
		if len(tmp):
			html += u'Есть ' + u', '.join(tmp) + u'. '
		html += u'</p>'
		if marker['is_open']:
			html += u'<p>Приём продолжается.</p>'
		# Добавление ссылок.
		mklink = lambda url, cls: u'<a target="_blank" class="%s" href="%s">%s</a>' % (cls, quoteattr(url), urlparse.urlparse(url).netloc)
		links = [mklink(marker[k], k) for k in marker if k in ('url', 'url_own', 'url_vk') and marker[k]]
		if len(links):
			html += u'<p>Ссылки: '+ u', '.join(links) +u'.</p>'
		marker['html'] = html
		return marker

	def render_template(self, template_name, vars):
		data = open(os.path.join(os.path.dirname(__file__), 'templates', template_name), 'r').read()
		for k in vars:
			data = data.replace('${'+ k +'}', vars[k])
		return data

if __name__ == '__main__':
	application = webapp.WSGIApplication([
		('/', IndexHandler),
		('/update', UpdateHandler),
	], debug=True)
	wsgiref.handlers.CGIHandler().run(application)
