import model.models
from model.properties import GenderProperty
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db
from google.appengine.api import datastore_errors
from google.appengine.ext.webapp import template

from google.appengine.ext.db import polymodel

class LLModel(db.Model):
	date_created = db.DateTimeProperty(auto_now_add=True) 
	is_active = db.BooleanProperty(default=True)
	
class LLAccount(LLModel):

	system_login = db.StringProperty()
	system_password = db.StringProperty()
	
	email = db.EmailProperty()
	wants_email = db.BooleanProperty()
	
	name = db.StringProperty()
	surname = db.StringProperty()
	maiden_name = db.StringProperty()
	
	last_entrance = db.DateTimeProperty()
	active = db.BooleanProperty()
	
	is_administrator	= db.BooleanProperty()

class LLPostedElement(polymodel.PolyModel):
	date_created = db.DateTimeProperty(auto_now_add=True) 
	is_active = db.BooleanProperty(default=True)
	creator = db.ReferenceProperty(LLAccount,collection_name='posts')
	migration_id = db.IntegerProperty()
	
	def commit(self):
		self.put()
		if not self.migration_id:
			self.migration_id = self.key().id()
		
		self.put()
		
	
class LLPost(LLPostedElement):
	title = db.StringProperty()
	slug  = db.StringProperty()
	text = db.TextProperty()
	tags = db.StringListProperty()

class LLNews(LLPostedElement):
	title = db.StringProperty()
	slug  = db.StringProperty()
	text = db.TextProperty()	
	
class LLLink(LLPostedElement):
	title = db.StringProperty()
	description  = db.StringProperty()
	url = db.StringProperty()
	tags = db.StringListProperty()
	
class LLPicture(LLPostedElement):
	title = db.StringProperty()
	description = db.StringProperty()
	tags = db.StringListProperty()
	content = db.BlobProperty()
	content_type = db.StringProperty()
	
class LLPostReply(LLModel):
	replier_name = db.StringProperty()
	reply = db.StringProperty(multiline=True)
	element_replied = db.ReferenceProperty(LLPostedElement,collection_name='replies')
