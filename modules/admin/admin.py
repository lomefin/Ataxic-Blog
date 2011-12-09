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

class ArticleAdmin(llhandler.LLGAEHandler):
	def base_directory(self):
		return os.path.dirname(__file__)

	def internal_get(self):
		articles = LLArticle.all().order('-date_created')
		values = {'articles':articles}
		self.render('post_list',template_values=values)
	
	def internal_post(self):
		self.render('post_list')

class PostedElementDeleteConfirmation(llhandler.LLGAEHandler):
	def base_directory(self):
		return os.path.dirname(__file__)
	
	def internal_get(self,element_type,key):
		element_key = LLPostedElement.get(Key(encoded=key))
		values = { 'element' : element_key, 'element_type':element_type}
		self.render('confirm_delete',template_values=values)
	
	def get(self,element_type,key):
		self.auth_check()
		self.internal_get(element_type,key)

class PostedElementActiveStatusModifier(llhandler.LLGAEHandler):
	def base_directory(self):
		return os.path.dirname(__file__)
	
	def internal_get(self,element_type,key):
		element_key = LLPostedElement.get(Key(encoded=key))
		values = { 'element' : element_key, 'element_type':element_type}
		self.render('confirm_delete',template_values=values)
	
	def get(self,element_type,key):
		self.auth_check()
		self.internal_get(element_type,key)

def main():
  application = webapp.WSGIApplication([('/admin/articles/', ArticleAdmin),
  										('/admin/(articles|news|link)/(.+?)/remove',PostedElementDeleteConfirmation),
  										('/admin/(articles|news|link)/(.+?)/(activate|deactivate)',PostedElementActiveStatusModifier),
  										('.*',lib.errors.NotFoundHandler)],
                                       debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()