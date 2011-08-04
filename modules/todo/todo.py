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
import string
import datetime
from model.models import *

class TodoHandler(mkhandler.MKHandler):
	
	def base_directory(self):
		return os.path.dirname(__file__)
	
	def internal_get(self):
	
		goals = MKGoal.all().filter('created_by = ', self.current_account).order('creation_date')
		accomplished = []
		pending = []
		
		for goal in goals:
			if goal.date_completed:
				accomplished.append(goal)
			else:
				pending.append(goal)
	
		values = {'accomplished' : accomplished, 'pending' : pending}
		self.render('todo', template_values=values)
		
		#self.base_auth()
		#self.get_internal()
		#user_logout = users.create_logout_url("/eventos/")
		#self.response.out.write("<a href=\"%s\">Logout</a>." %user_logout)
	
	def internal_post(self):
		
		new_todo = self.request.get('newCompromise')
		
		if len(new_todo.strip()) == 0:
			return
		
		goal = MKGoal()
		goal.goal = new_todo
		goal.created_by = self.current_account
		goal.put()
		
		self.redirect('/todo/')

class CompletedGoalHandler(mkhandler.MKHandler):

	def base_directory(self):
		return os.path.dirname(__file__)
	
	def get(self,goal_id):
		self.auth_check()
		self.internal_get(goal_id)
		
	def internal_get(self,goal_id):
		goal_id = int(goal_id)
		goal = MKGoal.get_by_id(goal_id)
		goal.date_completed = datetime.datetime.now()
		goal.put()
		self.redirect('/todo/')
		
class TodoAjaxHandler(mkhandler.MKHandler):
	
	def base_directory(self):
		return os.path.dirname(__file__)
	
	def internal_post(self):
		
		return

def main():
  application = webapp.WSGIApplication([('/todo/', TodoHandler),
										('/todo/completed/(.*?)', CompletedGoalHandler)],
                                       debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
