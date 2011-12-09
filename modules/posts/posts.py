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
#import controller.sessions.SessionManager
#from controller.appengine_utilities.sessions import Session
#from controller.appengine_utilities.flash import Flash
#from controller.appengine_utilities.cache import Cache
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


class PostHandler(llhandler.LLHandler):
	
	def base_directory(self):
		return os.path.dirname(__file__)
	
	def internal_get(self):
		offset = 0
		try:
			if(self.request.get('offset') is not None):
				offset=int(self.request.get('offset'))
		except:
			pass
		if LLArticle.all().count() > 0:
			articles = LLArticle.all().order('-date_created').fetch(10,offset)
			for article in articles:
				article.markdown_html = markdown2.markdown(article.text,extras={"code-friendly":None,"html-classes":{"pre":"prettyprint"}})
			values = {'articles':articles,'offset':offset+10,'is_offset':len(articles)>10}
			self.render('index',template_values=values)
		else:
			self.render('index')
		
	
	

class NewPostHandler(llhandler.LLGAEHandler):
	def base_directory(self):
		return os.path.dirname(__file__)

	def internal_get(self):

		self.render('create_post')
	
	def internal_post(self):
		try:
			message = LLArticle()
			message.title = self.request.get('title')
			message.text = self.request.get('content')
			message.creator = self.current_account
			message.put()
			if self.request.get('publish') != "true":
			  message.is_active = False
			  message.put()
			else:
			  self.set_flash('Post agregado')
		except :
			self.set_flash('No se pudo agregar el post.',flash_type='errorFlash')
			
		self.redirect('/posts/')
	

class ViewPostHandler(llhandler.LLHandler):
	def base_directory(self):
		return os.path.dirname(__file__)
		
	def get(self,slug):
		self.auth_check()
		self.view_post(slug)
		
	def view_post(self,slug):
		post = LLArticle.all().filter('slug =',slug).get()

		if post is not None:
			markdown_html = markdown2.markdown(post.text,extras={"code-friendly":None,"html-classes":{"pre":"prettyprint"}})
			values = {'post':post,'from':self.request.path,'markdown_html':markdown_html}
			self.render('view_post',template_values=values)
		else:
			self.set_flash('No existe ese post',flash_type='errorFlash')
			self.redirect('/posts/')

class EditPostHandler(llhandler.LLGAEHandler):
	def base_directory(self):
		return os.path.dirname(__file__)
		
	def get(self,slug):
		self.auth_check()
		self.view_post(slug)
		
	def view_post(self,slug):
		post = LLArticle.all().filter('slug =',slug).get()
		#post = LLArticle.get_by_id(int(post_id))
		if post is not None:
			markdown_html = markdown2.markdown(post.text,extras={"code-friendly":None,"html-classes":{"pre":"prettyprint"}})
			values = {'post':post,'from':self.request.path,'markdown_html':markdown_html}
			self.render('edit_post',template_values=values)
		else:
			self.set_flash('No existe ese post',flash_type='errorFlash')
			self.redirect('/posts/')
			
	def post(self,slug):
		self.auth_check()
		self.edit_post(slug)
	
	def edit_post(self,slug):
		post = LLArticle.all().filter('slug =',slug).get()
		#post = LLArticle.get_by_id(int(post_id))
		if post is not None:
			post_body = self.request.get('content')
			post.text = post_body
			post.put()
			self.set_flash('Cambios agregados',flash_type='successFlash')
			self.view_post(slug)
			
			return
		else:
			self.set_flash('No existe ese post',flash_type='errorFlash')
			self.redirect('/posts/')
			
			
def main():
  application = webapp.WSGIApplication([('/posts/', PostHandler),
  										('/posts/_new',NewPostHandler),
  										('/posts/([a-zA-Z\-0-9]*)',ViewPostHandler),
										('/posts/([a-zA-Z\-0-9]*)/edit',EditPostHandler),
										('/articles/', PostHandler),
  										('/articles/_new',NewPostHandler),
  										('/articles/([a-zA-Z\-0-9]*)',ViewPostHandler),
										('/articles/([a-zA-Z\-0-9]*)/edit',EditPostHandler),
										('.*',lib.errors.NotFoundHandler)],
                                       debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
