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
import datetime
from model.models import *
import random
import string

class AddUserHandler(mkhandler.MKGAEHandler):
	
	def base_directory(self):
		return os.path.dirname(__file__)
	
	def internal_get(self):
		self.render('add_user')
		#self.base_auth()
		#self.get_internal()
		#user_logout = users.create_logout_url("/eventos/")
		#self.response.out.write("<a href=\"%s\">Logout</a>." %user_logout)
	
	def internal_post(self):
		users_created = []
		
		user_name = self.request.get('user_name')
		user_surname = self.request.get('user_surname')
		
		if len(user_name) == 0 or len(user_surname) == 0:
			return
		#Generate a username
		username = user_name[0] + user_surname.replace(' ','')[:8]
		username = username.lower()
		
		#Find if the username already exists
		existing_account = MKAccount.all().filter('system_login =',username).get()
		if existing_account:
			counter = 0
			while existing_account:
				counter = counter + 1
				existing_account = MKAccount.all().filter('system_login =',username + str(counter)).get()
			if counter > 0:
				username = username + str(counter)
		#If exists try with a secuence number
		
		user = MKAccount()
		user.name = user_name.capitalize()
		user.surname = user_surname.capitalize()
		user.system_login = username;
		
		#random password
		user.system_password = ''.join(random.sample(string.lowercase,6))
		user.put()
		
		users_created.append(user)

		
				
			
		flash_message = 'Usuario creados exitosamente'
			
		values = {
					'flash' : flash_message,
					'created_users' : users_created,
					
				}
		
		self.render('added_user',template_values=values)

def main():
  application = webapp.WSGIApplication([('/admin/users/add', AddUserHandler)],
                                       debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
