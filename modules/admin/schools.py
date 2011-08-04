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

class ListSchoolHandler(mkhandler.MKGAEHandler):
	def base_directory(self):
		return os.path.dirname(__file__)
	
	def internal_get(self):
		schools = MKSchool.all()
		
		values = {'schools':schools}
		self.render('list_school',template_values=values)

class DefineSchoolWeeksHandler(mkhandler.MKGAEHandler):
	
	def base_directory(self):
		return os.path.dirname(__file__)
	
	def get(self, school_id):
		self.auth_check()
		self.internal_get(school_id)
		
	def post(self, school_id):
		self.auth_check()
		self.internal_post(school_id)

	def internal_get(self,school_id):
	
		week_numbers = range(1,30)
		
		
		values = {'week_numbers':week_numbers,'year':2011}
	
		self.render('week_numbers',template_values=values)
	
	def internal_post(self,school_id):
		week_numbers = range(1,30)
		
		for i in week_numbers:
			this_week_start = self.request.get('weekStart' + str(i))
			this_week_end = self.request.get('weekEnd' + str(i))
			this_week_trivia = self.request.get('triviaWeeks'+str(i))
			this_week_foodlog = self.request.get('foodLogWeeks'+str(i))
			this_week_todo = self.request.get('todoWeeks'+str(i))
			this_week_year = self.request.get('year')
			
			week = MKWeek()
			week.year = int(this_week_year)
			week.number = i
			week.start_date = datetime.datetime(*time.strptime(this_week_start, "%d/%m/%Y")[0:5])
			week.end_date = datetime.datetime(*time.strptime(this_week_end, "%d/%m/%Y")[0:5])
			week.school = MKSchool.get_by_id(int(school_id))
			week.trivia = (this_week_trivia == "yes")
			week.food_log = (this_week_foodlog == "yes")
			week.todo = (this_week_todo == "yes")
			
			if week.trivia or week.food_log or week.todo:
				week.put()
		values = { 'weeks' : MKWeek().all().filter('year =',int(this_week_year)).filter('school = ' , MKSchool.get_by_id(int(school_id))).order('number')}
		self.render('week_list',template_values= values)
		
class AddSchoolHandler(mkhandler.MKGAEHandler):
	
	def base_directory(self):
		return os.path.dirname(__file__)
	
	def internal_get(self):
		values = {
			'user_count_range':[0,1,2,3,4,5,6,7,8,9],
		}
		
		self.render('add_school',template_values=values)
		#self.base_auth()
		#self.get_internal()
		#user_logout = users.create_logout_url("/eventos/")
		#self.response.out.write("<a href=\"%s\">Logout</a>." %user_logout)
	
	def internal_post(self):
		
		school_name = self.request.get('school_name')
		existing_school = MKSchool.gql("WHERE name = :l",l=school_name).get()
		if not existing_school:
			school = MKSchool()
			school.name = school_name
			school.put()
			flash_message = "El colegio ha sido agregado"
		else:
			flash_message = "El colegio con nombre " + school_name + " ya existe."
		values = { 'flash': flash_message }
		self.render('add_school',template_values=values);


def main():
  application = webapp.WSGIApplication([('/admin/schools/add', AddSchoolHandler),
										('/admin/schools/list',ListSchoolHandler),
										('/admin/schools/(\d*)/weeks',DefineSchoolWeeksHandler)],
                                       debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
