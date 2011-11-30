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
import time
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
from lib import mkhandler
from model.models import *

class LogoutHandler(mkhandler.MKHandler):
	
	def base_directory(self):
		return os.path.dirname(__file__)
	
	def internal_get(self):
		self.session.terminate()
		self.redirect("/login")
		
		
class DefaultHandler(mkhandler.MKHandler):
		
	def base_directory(self):
		return os.path.dirname(__file__)
	
	def get(self):
		self.internal_get()
		
	def internal_get(self):
		values = {'flash_message' : 'Problemas'}
		values = {}
		self.render('index',template_values=values)
		#self.base_auth()
		#self.get_internal()
		#user_logout = users.create_logout_url("/eventos/")
		#self.response.out.write("<a href=\"%s\">Logout</a>." %user_logout)

	def internal_post(self):
		
		#Look up for the username
		self.current_account =  LLAccount.all().filter('system_login = ',self.request.get('username')).filter('system_password = ',self.request.get('password')).get()
		
		if not self.current_account:
			values = {'flash' : 'Nombre de usuario o contrasena no existe'}
			self.render('index',template_values=values)
			return
		
		
		
def main():
  application = webapp.WSGIApplication([('/login', DefaultHandler),('/logout', LogoutHandler)],
                                       debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
