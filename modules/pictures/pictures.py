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

class PictureViewHandler(llhandler.LLHandler):
	
	def base_directory(self):
		return os.path.dirname(__file__)
	
	def get(self,picture_id):
		#self.auth_check();
		self.view_picture(int(picture_id))
	
	def view_picture(self,picture_id):
		picture = LLPicture.get_by_id(picture_id)		
		
		if picture:
			self.response.headers['Content-Type'] = 'image/jpeg'
			self.response.out.write(picture.content)
		else:
			self.wr( 'err...this is akward')
	

class PicturePostHandler(llhandler.LLHandler):
	
	def base_directory(self):
		return os.path.dirname(__file__)
	
	def internal_get(self):
	
		self.render('upload_pictures')
	
	def internal_post(self):
		try:
			pic = LLPicture()
			pic.title = self.request.get('title')
			pic.description = self.request.get('desc')
			pic.content = self.request.get('content')
			pic.creator = self.current_account
			pic.put()

			self.set_flash('Foto agregada',flash_type='successFlash')
		except:
			self.set_flash('No se pudo agregar la foto',flash_type='errorFlash')
		self.redirect('/pictures/add')


def main():
  application = webapp.WSGIApplication([('/pictures/add', PicturePostHandler),('/pictures/(\d*)',PictureViewHandler)],
                                       debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
