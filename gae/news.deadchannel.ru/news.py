# vim: set fileencoding=utf-8:

# Python imports
import datetime
import logging
import os
import traceback
import urlparse
import wsgiref.handlers

# GAE imports
from django.utils import simplejson
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

# Local imports
import model

# Enable custom filters.
webapp.template.register_template_library('filters')

class BaseRequestHandler(webapp.RequestHandler):
	def generate(self, template_name, template_values={}, ret=False):
		user = users.get_current_user()
		if user:
			log_in_out_url = users.create_logout_url(self.request.path)
		else:
			log_in_out_url = users.create_login_url(self.request.path)

		# We'll display the user name if available and the URL on all pages
		values = {'user': user, 'log_in_out_url': log_in_out_url, 'is_admin': users.is_current_user_admin() }
		url = urlparse.urlparse(self.request.url)
		values['base'] = url[0] + '://' + url[1]
		values.update(template_values)

		# Construct the path to the template
		directory = os.path.dirname(__file__)
		path = os.path.join(directory, 'templates', template_name)

		result = template.render(path, values)
		if ret:
			return result
		self.response.out.write(result)


class IndexHandler(BaseRequestHandler):
	def get(self):
		self.generate('index.html', {
			'news': model.News.all().order('-id').fetch(20),
		})


class NodeHandler(BaseRequestHandler):
	def get(self, nid):
		news = model.News.gql('WHERE id = :1', int(nid)).get()
		if not news:
			raise Exception('No such node.')
		self.generate('node.html', {
			'node': news,
			'comments': model.Comment.gql('WHERE news = :1', news).fetch(100),
		})

	def post(self, nid):
		user = users.get_current_user()
		if not user:
			raise Exception('Not authorized.')
		news = model.News.gql('WHERE id = :1', int(nid)).get()
		if not news:
			raise Exception('No such node.')
		comment = model.Comment(author=user, news=news, text=self.request.get('comment')).put()
		self.redirect('/node/' + nid)


class ImportHandler(BaseRequestHandler):
	def get(self):
		self.generate('import.html')

	def post(self):
		for news in model.News.all().fetch(1000):
			logging.info('deleted old node/%u' % news.id)
			news.delete()

		data = simplejson.loads(self.request.get("json"))
		for node in data:
			try:
				news = model.News(id=int(node['id']),
					author=users.User(node['author']),
					added=datetime.datetime.strptime(node['added'], '%Y-%m-%d %H:%M:%S'),
					title=node['title'],
					text=node['text'])
				if node.has_key('labels'):
					news.labels = [l.lower() for l in node['labels']]
				if node.has_key('link') and node['link']:
					news.link = node['link']
					news.site = urlparse.urlparse(node['link']).netloc
				if node.has_key('picture'):
					news.picture = node['picture']
				news.language = 'ru'
				if news.labels and 'english' in news.labels:
					news.language = 'en'
				news.comments = 0
				news.votes = 1
				news.likes = 1
				news.put()
				logging.info("node/%s added" % node['id'])
			except Exception, e:
				logging.error("node/%s had issues: %s\n%s" % (node['id'], e, traceback.format_exc(e)))

class SubmitHandler(BaseRequestHandler):
	def get(self):
		self.generate('submit.html')

	def post(self):
		user = users.get_current_user()
		if not user:
			raise Exception('Login required.')
		labels = [l.strip().lower() for l in self.request.get('labels').split(',') if l.strip()]
		news = model.News(id=model.News.nextid(), author=user, title=self.request.get('title'), link=self.request.get('link'), comments=0, votes=1, likes=1, labels=labels)
		news.put()

		self.redirect('/')

if __name__ == '__main__':
	wsgiref.handlers.CGIHandler().run(webapp.WSGIApplication([
		('/', IndexHandler),
		('/import', ImportHandler),
		('/node/(\d+)', NodeHandler),
		('/submit', SubmitHandler),
	], debug=True))
