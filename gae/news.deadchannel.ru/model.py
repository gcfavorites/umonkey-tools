# vim: set fileencoding=utf-8:

from google.appengine.ext import db

class Model(db.Model):
	@classmethod
	def nextid(cls):
		last = cls.all().order('-id').get()
		return last and last.id + 1 or 1

class News(Model):
	id = db.IntegerProperty(required=True)
	author = db.UserProperty()
	added = db.DateTimeProperty(auto_now_add=True, required=True)
	title = db.StringProperty()
	link = db.LinkProperty()
	site = db.StringProperty() # имя домена из link
	text = db.TextProperty()
	labels = db.StringListProperty()
	picture = db.LinkProperty() # исходный адрес картинки
	picture_data = db.BlobProperty(default=None) # содержимое отмасштабированной картинки (JPEG, 100×100)
	language = db.StringProperty()
	# информация о голосах
	comments = db.IntegerProperty() # количество комментариев
	votes = db.IntegerProperty() # количество голосов
	likes = db.IntegerProperty() # количество положительных голосов

class Comment(Model):
	id = db.IntegerProperty()
	added = db.DateTimeProperty(auto_now_add=True, required=True)
	news = db.ReferenceProperty(News, required=True)
	author = db.UserProperty(required=True)
	text = db.TextProperty(required=True)

	def put(self):
		if not self.id:
			self.id = self.nextid()
		return super(Comment, self).put()

class Label(db.Model):
	name = db.StringProperty(required=True)
	count = db.IntegerProperty()