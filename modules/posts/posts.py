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
from model.models import *



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
			messages = LLArticle.all().order('-date_created').fetch(10,offset)
			
			values = {'messages':messages,'offset':offset+10,'is_offset':len(messages)>10}
			self.render('index',template_values=values)
		else:
			self.render('index')
		#self.base_auth()
		#self.get_internal()
		#user_logout = users.create_logout_url("/eventos/")
		#self.response.out.write("<a href=\"%s\">Logout</a>." %user_logout)
	
	def internal_post(self):
		try:
			message = LLArticle()
			message.title = self.request.get('title')
			message.text = self.request.get('content')
			message.creator = self.current_account
			message.put()
			if self.request.get('publish') is not None:
			  self.set_flash('publish : ' + str(self.request.get('publish')))
			self.set_flash('Post agregado')
		except :
			self.set_flash('No se pudo agregar el post.',flash_type='errorFlash')
			
		self.redirect('/posts/')

class ViewPostHandler(llhandler.LLHandler):
	def base_directory(self):
		return os.path.dirname(__file__)
		
	def get(self,post_id):
		self.auth_check()
		self.view_post(post_id)
		
	def view_post(self,post_id):
		post = LLArticle.all().filter('migration_id =',int(post_id)).get()
		#post = LLArticle.get_by_id(int(post_id))
		if post is not None:
			values = {'post':post,'from':self.request.path}
			self.render('view_post',template_values=values)
		else:
			self.set_flash('No existe ese post',flash_type='errorFlash')
			self.redirect('/posts/')

class EditPostHandler(llhandler.LLHandler):
	def base_directory(self):
		return os.path.dirname(__file__)
		
	def get(self,post_id):
		self.auth_check()
		self.view_post(post_id)
		
	def view_post(self,post_id):
		post = LLArticle.all().filter('migration_id =',int(post_id)).get()
		#post = LLArticle.get_by_id(int(post_id))
		if post is not None:
			values = {'post':post,'from':self.request.path}
			self.render('edit_post',template_values=values)
		else:
			self.set_flash('No existe ese post',flash_type='errorFlash')
			self.redirect('/posts/')
			
	def post(self,post_id):
		self.auth_check()
		#if not self.current_account.is_administrator:
		#	self.set_flash('No tienes autorización para editar el post',flash_type='errorFlash')
		#	self.redirect('/posts/')
		#	return
		self.edit_post(post_id)
	
	def edit_post(self,post_id):
		post = LLArticle.all().filter('migration_id =',int(post_id)).get()
		#post = LLArticle.get_by_id(int(post_id))
		if post is not None:
			post_body = self.request.get('content')
			post.text = post_body
			post.commit()
			self.set_flash('Cambios agregados',flash_type='successFlash')
			self.view_post(post_id)
			
			return
		else:
			self.set_flash('No existe ese post',flash_type='errorFlash')
			self.redirect('/posts/')
			
			
def main():
  application = webapp.WSGIApplication([('/posts/', PostHandler),('/posts/(\d*)',ViewPostHandler),
										('/posts/(\d*)/edit',EditPostHandler),
										('.*',lib.errors.NotFoundHandler)],
                                       debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
