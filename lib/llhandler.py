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
import time
import datetime
#import controller.sessions.SessionManager
#from appengine_utilities.sessions import Session
from lib.gaesessions import get_current_session
#from controller.appengine_utilities.flash import Flash
#from controller.appengine_utilities.cache import Cache
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db
from google.appengine.api import datastore_errors
from google.appengine.ext.webapp import template
from model.models import *


class LLHandler(webapp.RequestHandler):
	def __init__(self):
		self.flash = None
		self.flash_type = 'normalFlash'
		self.log_count = 1
		#self.auth_check()
	
	def set_flash(self,flash,flash_type='info'):
		if(self.session):
			self.session['flash'] = flash
			self.session['flash_type'] = flash_type
	
	def read_flash(self):
		if(self.session):
			if(self.session.has_key('flash')):
				self.flash = self.session.pop('flash',default=None)
				self.flash_type = self.session.pop('flash_type',default='normalFlash')
			
	
	def auth_check(self):
		
		self.session = get_current_session()
		user = users.get_current_user()
		self.current_account = None
			
		if(user and self.session):
			if self.session.has_key("current_account"):
				self.current_account = self.session["current_account"]	
			else:
				self.current_account = LLAccount.all().filter('email = ',user.email()).get()
				
				if not self.current_account:
					self.current_account = LLAccount()
					self.current_account.email = user.email()
						#self.current_account.put()
					#Setting the session data
				#self.current_account.is_administrator = users.is_current_user_admin()
				self.current_account.last_entrance = datetime.datetime.now()
				self.current_account.put()
				self.session["current_account"] = self.current_account
				
				time.sleep(1)
		
		else:
			self.login_url = users.create_login_url('/')
		
		
		return True
			
	def render(self,pagename,template_values=None):
		
		if not template_values:
			template_values = {}
			
		try:
			self.read_flash()
			
			template_values['flash'] = self.flash
			template_values['flash_type'] = self.flash_type
			
			if self.current_account:
				template_values['logged_user'] = self.current_account
			if self.login_url:
				template_values['login_url'] = self.login_url
			if self.session.has_key("current_account"):
				template_values['logged_user'] = self.session["current_account"]
			if self.logout_url:
				template_values['logout_url'] = self.logout_url
			
		except:
			pass
		
		path = os.path.join(self.base_directory(), 'views/'+pagename+'.html')
		self.response.out.write(template.render(path, template_values))
		
	def render_specific(self,pagename,template_values=None):
		#self.wr(os.path.dirname(__file__))
		path = os.path.join(self.base_directory(), '../../templates/'+pagename)
		#self.wr(path)
		self.response.out.write(template.render(path, template_values))
	
	def wr(self,text):
		self.response.out.write(text)
		
	def log(self,text,type="info"):
		color = "white"
		if(type == "error"): color="aa5555"
		elif(type == "warn"): color="orange"
		elif(type == "ok"): color="#55aa55"
		
		self.wr('<p style="background-color:'+color+'"><span class="operationNumber" style="min-width:50px">'+str(self.log_count)+'</span>'+text+'</p>')
		self.log_count = self.log_count + 1
	def param(self,param_name):
		return self.request.get(param_name)
	
	def get(self):
		self.auth_check()
		self.internal_get()
	
	def post(self):
		self.auth_check()
		self.internal_post()
		



class LLGAEHandler(LLHandler):
	def __init__(self):
		self.flash = ''
		#self.auth_check()
		
	def auth_check(self):
		user = users.get_current_user()
		
		#Check if the user is in @mekuido.info
		if user:
			emailDomain = user.email().split("@")
			if emailDomain[1] == "ataxic.org":
				self.session = get_current_session()
				self.current_account = None
				
				if self.session.has_key("current_account"):
					self.current_account = self.session["current_account"]	
				else:
					self.current_account = LLAccount.all().filter('email = ',user.email()).get()
					
					if not self.current_account:
						self.current_account = LLAccount()
						self.current_account.email = user.email()
						#self.current_account.put()
					#Setting the session data
					self.current_account.last_entrance = datetime.datetime.now()
					self.current_account.put()
					self.session["current_account"] = self.current_account
					#self.session["current_account"].put()
					time.sleep(1)
				return True
			else:
				self.redirect('/admin/unlog/')
				#self.redirect('/unlogFromGoogleAcount')
				
		else:
			self.redirect(users.create_login_url(self.request.uri))
        
			
	
