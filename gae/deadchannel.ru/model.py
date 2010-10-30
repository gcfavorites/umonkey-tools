# vim: set ts=4 sts=4 sw=4 noet fileencoding=utf-8:

from google.appengine.ext import db

class Event(db.Model):
	user = db.UserProperty(required=True) # кто добавил
	date = db.DateTimeProperty()
	title = db.StringProperty()
	url = db.LinkProperty()
	short_url = db.LinkProperty()
	far_sent = db.BooleanProperty()
	soon_sent = db.BooleanProperty()


class Email(db.Model):
	date_added = db.DateTimeProperty(auto_now_add=True)
	email = db.EmailProperty()
	# Напоминание отправляется только на подтверждённые адреса.
	confirmed = db.BooleanProperty()
	confirm_code = db.IntegerProperty()


class Phone(db.Model):
	date_added = db.DateTimeProperty(auto_now_add=True)
	phone = db.PhoneNumberProperty()
	# Напоминания отправляются только на подтверждённые номера.
	confirmed = db.BooleanProperty()
	# Код подтверждения.  Сохраняется при выдаче, после проверки очищается.
	confirm_code = db.IntegerProperty()
