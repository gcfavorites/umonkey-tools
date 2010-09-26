# vim: set ts=4 sts=4 sw=4 noet fileencoding=utf-8:

from google.appengine.ext import db

class Event(db.Model):
	user = db.UserProperty(required=True) # кто добавил
	date = db.DateTimeProperty()
	title = db.StringProperty()
	url = db.LinkProperty()
	far_sent = db.BooleanProperty()
	soon_sent = db.BooleanProperty()

class Email(db.Model):
	date_added = db.DateTimeProperty(auto_now_add=True)
	email = db.EmailProperty()

class Phone(db.Model):
	date_added = db.DateTimeProperty(auto_now_add=True)
	phone = db.PhoneNumberProperty()
