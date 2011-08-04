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
from model.models import *
import random
import string

class ListStudentHandler(mkhandler.MKHandler):
	
	def base_directory(self):
		return os.path.dirname(__file__)
	
	def get(self,second_argument):
		self.auth_check()
		self.internal_get(second_argument)
	
	def internal_get(self,class_id):
		
		#self.base_auth()
		#self.get_internal()
		#user_logout = users.create_logout_url("/eventos/")
		#self.response.out.write("<a href=\"%s\">Logout</a>." %user_logout)
		classes = MKClass.get_by_id(int(class_id))
		flash_message = ''
		if not self.current_account:
			self.wr('No hay current account')
			if not classes.teacher:
				self.wr('No hay profesor en la clase')
		else:
			if classes.teacher.user.key().id() != self.current_account.key().id():
				flash_message = 'No puedes acceder a este curso, no eres profesor a cargo'
				values = {
					'error_message' : flash_message
				}
				self.render('base_error',template_values=values)
				return
		values = {'class':classes}
		self.render('list_student',template_values=values)
	
	def post(self,second_argument):
		self.auth_check()
		self.internal_post(second_argument)
	
	def internal_post(self,class_id):
		
		flash_message = ''

class AddStudentHandler(mkhandler.MKHandler):
	
	def base_directory(self):
		return os.path.dirname(__file__)
	
	def get(self,second_argument):
		self.auth_check()
		self.internal_get(second_argument)
	
	def internal_get(self,class_id):
		
		#self.base_auth()
		#self.get_internal()
		#user_logout = users.create_logout_url("/eventos/")
		#self.response.out.write("<a href=\"%s\">Logout</a>." %user_logout)
		classes = MKClass.get_by_id(int(class_id))
		
		values = {
			'user_count_range':range(1,51),
			'class' : classes
		}
		
		self.render('add_student',template_values=values)
	
	def post(self,second_argument):
		self.auth_check()
		self.internal_post(second_argument)
	
	def internal_post(self,class_id):
		
		flash_message = ''
		mkclass = MKClass.get_by_id(int(class_id))
		users_created = []
		for i in range(1,51):
			student_name = self.request.get('student_name'+str(i))
			student_surname = self.request.get('student_surname' + str(i))
			
			if len(student_name) == 0 or len(student_surname) == 0:
				continue
			#Generate a username
			username = student_name[0] + student_surname.replace(' ','')[:8]
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
			
			student = MKAccount()
			student.name = student_name.capitalize()
			student.surname = student_surname.capitalize()
			student.system_login = username;
			
			#random password
			student.system_password = ''.join(random.sample(string.lowercase,6))
			student.put()
			
			mkstudent = MKStudent()
			mkstudent.student_account = student
			mkstudent.attending_class = mkclass
			mkstudent.put()
			
			users_created.append(student)
			
				
			
		flash_message = 'Usuarios creados exitosamente'
			
		values = {
					'flash' : flash_message,
					'created_users' : users_created,
					'class' : mkclass
					
				}
		
		self.render('added_student',template_values=values)

class TeacherAdminHandler(mkhandler.MKHandler):
	
	def base_directory(self):
		return os.path.dirname(__file__)
	
	def internal_get(self):
		teacher = MKTeacher.all().filter('user = ', self.current_account).get()
		values = {'teacher':teacher}
		self.render('index',template_values=values)
		#self.base_auth()
		#self.get_internal()
		#user_logout = users.create_logout_url("/eventos/")
		#self.response.out.write("<a href=\"%s\">Logout</a>." %user_logout)
	
	def internal_post(self):
		self.internal_get()

class TeacherClassesHandler(mkhandler.MKHandler):
	
	def base_directory(self):
		return os.path.dirname(__file__)
	
	def internal_get(self):
		teacher = MKTeacher.all().filter('user = ', self.current_account).get()
		values = {'teacher':teacher}
		self.render('list_classes',template_values=values)
		#self.base_auth()
		#self.get_internal()
		#user_logout = users.create_logout_url("/eventos/")
		#self.response.out.write("<a href=\"%s\">Logout</a>." %user_logout)
	
	def internal_post(self):
		self.internal_get()

class ViewStudentDetailsHandler(mkhandler.MKHandler):

	def base_directory(self):
		return os.path.dirname(__file__)
	
	def get(self, arg):
		self.auth_check()
		self.internal_get(arg)
	
	def internal_get(self,student_id):
		student = MKStudent.get_by_id(int(student_id))
		goals = MKGoal.all().filter('created_by =',student.student_account).order('date_completed')
		values = {'student':student,'goals':goals}
		self.render('detail_student',template_values=values)
		#self.base_auth()
		#self.get_internal()
		#user_logout = users.create_logout_url("/eventos/")
		#self.response.out.write("<a href=\"%s\">Logout</a>." %user_logout)
	
	def internal_post(self):
		self.internal_get()
		
def main():
  application = webapp.WSGIApplication([('/teacher_panel/students/(\d*)/details',ViewStudentDetailsHandler),
										('/teacher_panel/students/(\d*)/add', AddStudentHandler),
										('/teacher_panel/students/(\d*)/list',ListStudentHandler),
										('/teacher_panel/myClasses', TeacherClassesHandler),
										('/teacher_panel/.*', TeacherAdminHandler)],
                                       debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
