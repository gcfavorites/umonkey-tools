# vim: set ts=4 sts=4 sw=4 noet fileencoding=utf-8:

import csv
import logging
import os
import sys
import urlparse
import wsgiref.handlers
from xml.sax.saxutils import escape as quoteattr

from google.appengine.api import memcache
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
		memcache.set('/data.js', get_data_script())
		logging.info('Done.')
		self.redirect('/')

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

class DataHandler(webapp.RequestHandler):
	def get(self):
		script = memcache.get('/data.js')
		if script is None:
			script = get_data_script()
			print >>sys.stderr, script
			memcache.set('/data.js', script)

		self.response.headers['Content-Type'] = 'text/plain'
		self.response.out.write(script)

def get_data_script():
	# Загрузка объектов, имеющих координаты.
	objects = [obj for obj in Settlement.all().fetch(1000) if obj.ll]

	# Преобразование объектов в словари.
	converters = { 'll': lambda x: (x.lat, x.lon) }
	convert = lambda key, val: converters.has_key(key) and converters[key](val) or val
	markers = [dict([(x, getattr(obj, x) and convert(x, getattr(obj, x))) for x in obj.fields()]) for obj in objects]

	# Отдаваемые данные.
	data = {
		'bounds': {
			'latmin': 1000,
			'latmax': 0,
			'lonmin': 1000,
			'lonmax': 0,
		},
		'markers': markers,
	}

	# Подсчёт минимальных и максимальных координат, для центрования карты.
	for marker in data['markers']:
		if marker['ll']:
			data['bounds']['latmin'] = min(marker['ll'][0], data['bounds']['latmin'])
			data['bounds']['lonmin'] = min(marker['ll'][0], data['bounds']['lonmin'])
			data['bounds']['latmax'] = max(marker['ll'][0], data['bounds']['latmax'])
			data['bounds']['lonmax'] = max(marker['ll'][0], data['bounds']['lonmax'])

	# Компоновка результата.
	return 'var map_data = ' + simplejson.dumps(data) + ';'

if __name__ == '__main__':
	application = webapp.WSGIApplication([
		('/data.js', DataHandler),
		('/update', UpdateHandler),
	], debug=True)
	wsgiref.handlers.CGIHandler().run(application)
