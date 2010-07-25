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
from google.appengine.api import images
from google.appengine.api import urlfetch
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

# Local imports
import model

# Enable custom filters.
webapp.template.register_template_library('filters')

def add_labels(labels):
	for label in labels:
		l = model.Label.gql('WHERE name = :1', label.lower()).get()
		if not l:
			l = model.Label(name=label.lower(), count=0)
		l.count += 1
		l.put()

def remove_labels(labels):
	for label in labels:
		l = model.Label.gql('WHERE name = :1', label.lower()).get()
		if i is not None:
			l.count -= 1
			if l.count > 0:
				l.put()
			else:
				l.delete()

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
		"""
		Adds a new comment.
		"""
		user = users.get_current_user()
		if not user:
			raise Exception('Not authorized.')
		news = model.News.gql('WHERE id = :1', int(nid)).get()
		if not news:
			raise Exception('No such node.')
		comment = model.Comment(author=user, news=news, text=self.request.get('comment')).put()
		news.comments += 1
		news.put()
		self.redirect('/node/' + nid)


class ImportHandler(BaseRequestHandler):
	def get(self):
		self.generate('import.html')

	def post(self):
		news = model.News.gql('WHERE id = :1', int(self.request.get('id'))).get()
		if not news:
			news = model.News(id=int(self.request.get('id')))
		news.author = users.User(self.request.get('author'))
		news.title = self.request.get('title')
		news.added = datetime.datetime.strptime(self.request.get('added'), '%Y-%m-%d %H:%M:%S')
		link = self.request.get('link')
		if link:
			news.link = link
		text = self.request.get('text')
		if text:
			news.text = text
		self.add_picture(news, self.request.get('picture'))
		news.comments = 0
		news.votes = 1
		news.likes = 1
		if self.request.get('labels'):
			news.labels = [l.strip().lower() for l in self.request.get('labels').split(',')]
			if 'enlgish' in news.labels:
				news.language = 'en'
		news.put()

	def add_picture(self, news, picture_url):
		if picture_url:
			news.picture = picture_url
			try:
				img = images.Image(image_data=urlfetch.Fetch(picture_url).content)

				if img.height > img.width:
					shift = float(img.height - img.width) / 2 / img.height
					crop_args = (0.0, shift, 1.0, 1.0 - shift)
				elif img.width > img.height:
					shift = float(img.width - img.height) / 2 / img.width
					crop_args = (shift, 0.0, 1.0 - shift, 1.0)
				if img.width != img.height:
					# logging.info('crop=%s, %s, %s, %s' % crop_args)
					img.crop(*crop_args)
				# logging.info('width=%s, height=%s' % (img.width, img.height))
				img.im_feeling_lucky()
				img.resize(100, 100)
				news.picture_data = img.execute_transforms(images.JPEG)
			except TypeError, e:
				logging.error('Error transforming image at %s: %s' % (picture_url, e))

class NodeImageHandler(BaseRequestHandler):
	def get(self, id):
		news = model.News.gql('WHERE id = :1', int(id)).get()
		if not news or not news.picture_data:
			raise Exception('Image not found.')
		self.response.headers['Content-Type'] = 'image/jpeg'
		self.response.out.write(news.picture_data)

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
		('/node/image/(\d+)', NodeImageHandler),
		('/submit', SubmitHandler),
	], debug=True))
