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

class TeacherAssignerHandler(mkhandler.MKGAEHandler):
	def base_directory(self):
		return os.path.dirname(__file__)
		
	def get(self, class_id,teacher_id):
		self.auth_check()
		self.internal_get(class_id,teacher_id)
	
	def internal_get(self,class_id,teacher_id):
		
		mkclass = MKClass.get_by_id(int(class_id))
		teacher = MKTeacher.get_by_id(int(teacher_id))
		#if not mkclass:
		#	self.render('base_error',template_values={'error_title':'Colegio no existente','error_message':'El colegio que se busca para ver sus cursos no existe en la base de datos'})
		#	return
		
		mkclass.teacher = teacher
		mkclass.put()
		
		values = {
			'flash':'El profesor ha sido asignado',
			'class':mkclass,
		}
		self.render('assign_teacher',template_values=values)

class AssignTeacherToClassHandler(mkhandler.MKGAEHandler):
	def base_directory(self):
		return os.path.dirname(__file__)
		
	def get(self, class_id):
		self.auth_check()
		self.internal_get(class_id)
	
	def internal_get(self,class_id):
		
		mkclass = MKClass.get_by_id(int(class_id))
		#if not mkclass:
		#	self.render('base_error',template_values={'error_title':'Colegio no existente','error_message':'El colegio que se busca para ver sus cursos no existe en la base de datos'})
		#	return
		
		
		values = {
			'class':mkclass,
		}
		self.render('assign_teacher',template_values=values)

class ListClassBySchoolIDHandler(mkhandler.MKGAEHandler):
	def base_directory(self):
		return os.path.dirname(__file__)
		
	def get(self, school_id):
		self.auth_check()
		self.internal_get(school_id)
	
	def internal_get(self,school_id):
		school_id = int(school_id)
		school = MKSchool.get_by_id(school_id)
		
		if not school:
			self.render('base_error',template_values={'error_title':'Colegio no existente','error_message':'El colegio que se busca para ver sus cursos no existe en la base de datos'})
			return
		
		classes = school.school_classes.order('-year').order('name')
		
		values = {
			'school':school,
			'classes':classes
		}
		self.render('list_class',template_values=values)
	
class ListClassHandler(mkhandler.MKGAEHandler):
	def base_directory(self):
		return os.path.dirname(__file__)
	
	def internal_get(self):
		self.wr('ListClass')

class AddClassHandler(mkhandler.MKGAEHandler):
	
	def base_directory(self):
		return os.path.dirname(__file__)
	
	def internal_get(self):
		
		schools = MKSchool.all().order("name")
		
		values = {
			'school_list':schools,
			'letters':string.uppercase,
			'current_year':datetime.date.today().year,
		}
		self.render('add_class',template_values=values)
		#self.base_auth()
		#self.get_internal()
		#user_logout = users.create_logout_url("/eventos/")
		#self.response.out.write("<a href=\"%s\">Logout</a>." %user_logout)

	def internal_post(self):
	
		school_id = self.request.get('school_id')
		class_name = self.request.get('class_level') + self.request.get('class_letter')
		class_year = self.request.get('class_year')
		existing_school = MKSchool.get_by_id(int(school_id))
		schools = MKSchool.all().order("name")
		
		if not existing_school:
			flash_message = "El colegio no existe " 
		else:
			flash_message = "El colegio existe y la clase es la " + class_name + " del year " + str(datetime.date.today().year)
			existing_class = existing_school.get_by_id(int(school_id)).school_classes.filter('name =',class_name).filter('year =',datetime.date.today().year).get()
			
			if existing_class:
				flash_message = "El curso " + class_name + " ya esta creada para el a&ntilde;o seleccionado"
			else:
				new_class = MKClass()
				new_class.name = class_name
				new_class.year = int(class_year)
				new_class.school = existing_school
				new_class.put()
				flash_message = "El curso ha sido agregado exitosamente"
			
		values = { 
				'flash': flash_message,
				'school_list':schools,
				'letters':string.uppercase,
				'current_year':datetime.date.today().year,		
				}
		self.render('add_class',template_values=values);


def main():
  application = webapp.WSGIApplication([('/admin/classes/add', AddClassHandler),
										('/admin/classes/list/(\d*)',ListClassBySchoolIDHandler),
										('/admin/classes/(\d*)/assign',AssignTeacherToClassHandler),
										('/admin/classes/(\d*)/assign/(\d*)',TeacherAssignerHandler)],
                                       debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
