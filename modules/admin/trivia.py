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

class AddQuestionHandler(mkhandler.MKGAEHandler):
	
	def base_directory(self):
		return os.path.dirname(__file__)
	
	def get(self, second_argument):
		self.internal_get(second_argument)
	
	def internal_get(self,trivia_code):
		values = {
			'range3' : range(3),
			'trivia_code' : trivia_code,
		}
		self.render('add_trivia_question',template_values=values)
		#self.base_auth()
		#self.get_internal()
		#user_logout = users.create_logout_url("/eventos/")
		#self.response.out.write("<a href=\"%s\">Logout</a>." %user_logout)

	def post(self, second_argument):
		self.auth_check()
		self.internal_post(second_argument)
		
	def internal_post(self,trivia_code):
	
		trivia = MKTrivia.get_by_id(int(trivia_code))
		
		question = MKTriviaQuestion()
		question.question_text = self.request.get('question_text')
		question.general_feedback = self.request.get('feedback_text')
		question.phrase = self.request.get('phrase_text')
		question.trivia = trivia
		question.last_displayed = datetime.datetime.now()
		question.put()
		self.flash = 'Pregunta Agregada'
		for i in range(3):
			possible_answer = MKTriviaPossibleAnswer()
			possible_answer.possible_answer_text = self.request.get('alternative'+str(i)+'_text')
			possible_answer.feedback_text = self.request.get('feedback'+str(i)+'_text')
			possible_answer.is_correct = self.request.get('correct_alternative'+str(i)) == "True"
			possible_answer.question = question
			possible_answer.put()
		values = { 
					'flash' : self.flash,
					'trivia_code' : trivia_code
				}
		self.render('added_trivia_question',template_values=values);
class ListTriviaHandler(mkhandler.MKGAEHandler):
	def base_directory(self):
		return os.path.dirname(__file__)
		
	def internal_get(self):
		questions = MKTriviaQuestion.all()
		
		self.render('trivia_list', template_values={'questions':questions})

class AddTriviaHandler(mkhandler.MKGAEHandler):
	
	def base_directory(self):
		return os.path.dirname(__file__)
	
	def internal_get(self):
	 
		self.render('add_trivia')
		#self.base_auth()
		#self.get_internal()
		#user_logout = users.create_logout_url("/eventos/")
		#self.response.out.write("<a href=\"%s\">Logout</a>." %user_logout)

	def internal_post(self):
		
		trivia_name = self.request.get('trivia_name')
		
		existing_trivia = MKTrivia.all().filter('trivia_name = ',trivia_name).get()
		
		if existing_trivia:
			flash_message = 'La trivia ya existe'
			values = { 'flash' : flash_message, 'flash_type' : 'error'}
			self.render('add_trivia',template_values=values)
			return 
		
		trivia = MKTrivia()
		trivia.trivia_name = trivia_name
		trivia.default_general_feedback = self.request.get('default_general_feedback')
		trivia.default_correct_feedback  = self.request.get('default_correct_feedback')
		trivia.default_wrong_feedback  = self.request.get('default_wrong_feedback')
		trivia.put()
		values = { 
				'trivia_code' : str(trivia.key().id())
				}
		self.render('added_trivia',template_values=values)
		


def main():
  application = webapp.WSGIApplication([('/admin/trivia/(\d*?)/addQuestion', AddQuestionHandler),
										('/admin/trivia/add',AddTriviaHandler),
										('/admin/trivia/listQuestions',ListTriviaHandler)
										],
                                       debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
