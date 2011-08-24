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
from lib import llhandler
from model.models import *

class PolyHandler(llhandler.LLHandler):

	def base_directory(self):
		return os.path.dirname(__file__)
	
	def internal_get(self):
		if not self.current_account.is_administrator:
			self.wr('You do not have permission to run this script')
			return
		
		self.log('Welcome, running script ' +self.__class__.__name__,"ok")
		
		self.log('Checking Posts')
		posts = LLArticle.all()
		for post in posts:
			try:
				self.log('Viewing post %d'%post.key().id())
			except:
				self.log('Log %d could not be transformed'%post.key().id())
		
		pass
	
	def internal_post(self):
		pass


def main():
  application = webapp.WSGIApplication([('.*', PolyHandler)],
                                       debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
