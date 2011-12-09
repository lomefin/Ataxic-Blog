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
from lib import comments
from lib import errors
from model.models import *

class LinkHandler(llhandler.LLHandler):
	
	def base_directory(self):
		return os.path.dirname(__file__)
	
	
	
	def internal_get(self):
		if LLLink.all().count() > 0:
			links = LLLink.all().order('-date_created')
			values = {'links':links}
			self.render('index',template_values=values)
		else:
			self.render('index')
		#self.base_auth()
		#self.get_internal()
		#user_logout = users.create_logout_url("/eventos/")
		#self.response.out.write("<a href=\"%s\">Logout</a>." %user_logout)
	
	def bitly_url(self,url):
		import urllib
		from google.appengine.api import urlfetch
		form_fields = {
			"login": "lomefin",
			"apiKey": "R_ecdc45222b96e2c01a7d7f5856c1f589",
			"longUrl": url,
			"format":"txt"
		}
		form_data = urllib.urlencode(form_fields)
		url = "http://api.bitly.com/v3/shorten?"+str(form_data)
		
		result = urlfetch.fetch(url=url,
                        method=urlfetch.GET)
		return str(result.content.replace("\n", ""))
	
	def internal_post(self):
		try:
			link = LLLink()
			link.title = self.request.get('title')
			link.url = self.bitly_url(self.request.get('url'))
			link.short_url = link.url
			link.description = cgi.escape(self.request.get('description'))
			link.creator = self.current_account
			link.put()
			self.set_flash('Link agregado')
		except:
			self.set_flash('No se pudo agregar el Link',flash_type='errorFlash')
		self.redirect('/links/')

class LinkReplyHandler(llhandler.LLHandler):
	
	def base_directory(self):
		return os.path.dirname(__file__)
	
	def internal_get(self):
		self.redirect('/links')
	
	def internal_post(self):
		
		link_key = int(self.request.get('link_key_id'))
		element = LLPostedElement.get_by_id(link_key)
		
		if not element:
			self.set_flash('El vinculo no existe',flash_type='errorFlash')
			self.redirect('/links/')
			return
		
		reply = LLPostReplyManager.append_reply(element, self.request.get('replier_name'), self.request.get('reply_text'))
		if not reply:
			self.set_flash('No se pudo agregar la respuesta',flash_type='errorFlash')
			self.redirect('/links/')
			return
		element.reply = reply
		element.put()
		self.set_flash('Respuesta agregada')
		self.redirect('/links/')


def main():
  application = webapp.WSGIApplication([('/links/', LinkHandler),
										('/links/reply/', LinkReplyHandler)
										,('.*',errors.NotFoundHandler)
										],debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
