#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import cgi
import datetime
import os
import lib
import string
import sys

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db
from google.appengine.api import datastore_errors
from google.appengine.ext.webapp import template
from lib import errors
from lib import llhandler
from lib import slugify
from model.models import *
from lib import markdown2

class AdminStart(llhandler.LLGAEHandler):
	def base_directory(self):
		return os.path.dirname(__file__)

	def internal_get(self):
		self.render('admin_index')
	

class ArticleAdmin(llhandler.LLGAEHandler):
	def base_directory(self):
		return os.path.dirname(__file__)

	def internal_get(self):
		articles = LLArticle.all().order('-date_created')
		values = {'articles':articles}
		self.render('article_list',template_values=values)
	

class NewsAdmin(llhandler.LLGAEHandler):
	def base_directory(self):
		return os.path.dirname(__file__)

	def internal_get(self):
		news = LLNews.all().order('-date_created')
		values = {'news_list':news}
		self.render('news_list',template_values=values)

class LinkAdmin(llhandler.LLGAEHandler):
	def base_directory(self):
		return os.path.dirname(__file__)

	def internal_get(self):
		links = LLLink.all().order('-date_created')
		values = {'links':links}
		self.render('link_list',template_values=values)	

class PostedElementDeleteConfirmation(llhandler.LLGAEHandler):
	def base_directory(self):
		return os.path.dirname(__file__)
	
	def internal_get(self,element_type,key):
		element = LLPostedElement.get(db.Key(encoded=key))
		values = { 'element' : element, 'element_type':element_type}
		self.render('confirm_delete',template_values=values)
	
	def get(self,element_type,key):
		self.auth_check()
		self.internal_get(element_type,key)
	
	def post(self,element_type,key):
		self.auth_check()
		self.internal_post(element_type,key)

	def internal_post(self, element_type, key):
		element = LLPostedElement.get(db.Key(encoded=key))
		element.delete()
		self.set_flash('El elemento ha sido <strong>eliminado para siempre</strong>.')
		self.redirect('/admin/')
		
class PostedElementActiveStatusModifier(llhandler.LLGAEHandler):
	def base_directory(self):
		return os.path.dirname(__file__)
	
	def internal_get(self,element_type,key):
		element = LLPostedElement.get(db.Key(encoded=key))
		values = { 'element' : element, 'element_type':element_type}
		self.render('confirm_delete',template_values=values)
	
	def get(self,element_type,key):
		self.auth_check()
		self.internal_get(element_type,key)
	
	def post(self,element_type,key,status):
		self.auth_check()
		self.internal_post(element_type,key,status)

	def internal_post(self, element_type, key,status):
		element = LLPostedElement.get(db.Key(encoded=key))
		if element.is_active == (status == 'activate'):
			self.set_flash('El elemento ya esta en el estado solicitado','warning')
			self.redirect('/admin/')
			return
		element.is_active = (status == 'activate')
		try:
			element.put()
			self.set_flash('El elemento ha sido cambiado de estado.','success')
		except:
			self.set_flash('No se pudo actualizar el elemento.','error')
		self.redirect('/admin/')

def main():
  application = webapp.WSGIApplication([('/admin/articles/', ArticleAdmin),
  										('/admin/news/',NewsAdmin),
  										('/admin/links/',LinkAdmin),
  										('/admin/(articles|news|link)/(.+?)/remove',PostedElementDeleteConfirmation),
  										('/admin/(articles|news|link)/(.+?)/(activate|deactivate)',PostedElementActiveStatusModifier),
  										('/admin/',AdminStart),
  										('.*',lib.errors.NotFoundHandler)],
                                       debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()