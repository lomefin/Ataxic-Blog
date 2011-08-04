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
from google.appengine.api import mail
from google.appengine.ext import db
from google.appengine.api import datastore_errors
from google.appengine.ext.webapp import template
from lib import mkhandler
from model.models import *

class DefaultHandler(mkhandler.MKHandler):
	
	def base_directory(self):
		return os.path.dirname(__file__)
	
	def internal_get(self):
		come_back = self.request.get('come_back');
		values = { 'come_back' : come_back, 'account':self.current_account}
		self.render('contact',template_values=values)
		#self.base_auth()
		#self.get_internal()
		#user_logout = users.create_logout_url("/eventos/")
		#self.response.out.write("<a href=\"%s\">Logout</a>." %user_logout)
	def internal_post(self):
		self.flash_message = "Su solicitud ha sido recibida"
		
		contact    = MKContactData()
		contact.created_by = self.current_account
		contact.status     = "Reported"
		contact.resolved   = False
		contact.module	   = self.request.get('module')
		contact.activity   = self.request.get('activity')
		contact.details    = self.request.get('detail')
		contact.url		   = self.request.get('error_url')
		contact.put()
		try:
			message = mail.EmailMessage(sender="soporte@mekuido.info",subject="[Nuevo Contacto] [#"+str(contact.key().id())+"]" )
			message.to = "Soporte MeKuido.info <soporte@mekuido.info>"
			message.body = """
			Ha llegado un nuevo contacto.
			--------------------------------------------------------------
			Fecha creación:"""+ str(contact.creation_date) + """
			Enviado por: %s %s (%s) """ % (str(contact.created_by.name),str(contact.created_by.surname),str(contact.created_by.email)) + """
			Modulo: """+ str(contact.module) + """
			Actividad: """+ str(contact.activity) + """
			URL:  """+ str(contact.url)
			message.send()
		except:
			pass
		self.values = {'come_back':self.request.get('come_back'),'contact':contact}
		self.render('receipt',template_values=self.values)

		
def main():
  application = webapp.WSGIApplication([('/support/contact/', DefaultHandler),
										],
                                       debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
