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

class NewsHandler(llhandler.LLHandler):
	
	def base_directory(self):
		return os.path.dirname(__file__)
	
	def internal_get(self):
		if LLNews.all().count() > 0:
			messages = LLNews.all().order('-date_created')
			values = {'messages':messages}
			self.render('index',template_values=values)
		else:
			self.render('index')
		#self.base_auth()
		#self.get_internal()
		#user_logout = users.create_logout_url("/eventos/")
		#self.response.out.write("<a href=\"%s\">Logout</a>." %user_logout)
	
	def internal_post(self):
		try:
			from django.template import defaultfilters
			
			message = LLNews()
			message.title = self.request.get('title')
			message.text = "<p>" + string.replace(cgi.escape(self.request.get('content')),'\n','</p><p>') + "</p>"
			message.slug = defaultfilters.slugify(message.title)
			message.creator = self.current_account
			message.put()
			self.set_flash('Noticia agregada')
		except:
			self.set_flash('No se pudo agregar la noticia',flash_type='errorFlash')
		self.redirect('/news/')


def main():
  application = webapp.WSGIApplication([('/news/', NewsHandler)],
                                       debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
