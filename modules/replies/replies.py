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
from lib import llhandler, comments
from model.models import *

class ReplyAddHandler(llhandler.LLHandler):
	
	def base_directory(self):
		return os.path.dirname(__file__)
	
	def internal_get(self):
		self.redirect('/')
	
	def internal_post(self):
		element = LLPostedElement.get_by_id(int(self.request.get('posted_element_id')))
		
		reply = LLPostReply()
		reply.element_replied = element
		reply.replier_name = self.request.get('replier_name')
		reply.reply = self.request.get('reply')
		reply.put()
		self.set_flash('Comentario Agregado',flash_type='successFlash')
		self.redirect(self.request.get('sent_from'))
			
		
		
		

class ViewPostHandler(llhandler.LLHandler):
	def base_directory(self):
		return os.path.dirname(__file__)
		
	def get(self,post_id):
		self.auth_check()
		self.view_post(post_id)
		
	def view_post(self,post_id):
		post = LLArticle.get_by_id(int(post_id))
		if post is not None:
			values = {'post':post}
			self.render('view_post',template_values=values)
		else:
			self.set_flash('No existe ese post',flash_type='errorFlash')
			self.redirect('/posts/')

def main():
  application = webapp.WSGIApplication([('/replies/add', ReplyAddHandler),('/posts/(\d*)',ViewPostHandler)],
                                       debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
