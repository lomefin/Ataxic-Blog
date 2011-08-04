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

class TriviaIndexHandler(mkhandler.MKHandler):
	
	def base_directory(self):
		return os.path.dirname(__file__)
	
	def render_question_or_no_trivia(self):
		available_questions = 5
	
		if(available_questions > 0):
			self.render('index')
		else:
			kid_face = self.current_student_user.student_avatar.sex + "-" + self.current_student_user.student_avatar.prefix + "-ok"
			values = { 'kid_face': kid_face}
		
			self.render('notrivia', template_values=values)
			
	
	def user_has_questions_remaining(self):
		current_user = self.current_student_user
		answered_questions = MKTriviaAnswer.all().filter('answered_by =' , current_user)
		questions_answered = []
		
		for answer in answered_questions:
			questions_answered.append(answer.question.key())
		
		possible_questions = db.Query(MKTriviaQuestion,keys_only=True).order('last_displayed')
		
		selected_question = None
		
		for question_key in possible_questions:
			
			if question_key not in questions_answered:
				selected_question = question_key
				break
		
		if selected_question is None:
			return None
		
		selected_question = MKTriviaQuestion.get(selected_question)
		selected_question.last_displayed = datetime.datetime.now()
		selected_question.put()
		
		return selected_question
	
	def internal_get(self):
	
		next_question = self.user_has_questions_remaining()
		
		flash = ''
		if not next_question:
			kid_face = self.current_student_user.student_avatar.sex + "-" + self.current_student_user.student_avatar.prefix + "-ok"
			values = { 'kid_face': kid_face}
		
			self.render('notrivia', template_values=values)
			return
		
		
		
		values = { 'flash' : flash , 'question' : next_question}
		
		self.render('index', template_values=values)
		
		#self.base_auth()
		#self.get_internal()
		#user_logout = users.create_logout_url("/eventos/")
		#self.response.out.write("<a href=\"%s\">Logout</a>." %user_logout)

class TriviaAnswerHandler(mkhandler.MKHandler):
	
	def base_directory(self):
		return os.path.dirname(__file__)
	
	def internal_post(self):
		
		question_code = self.request.get('triviaQuestion')
		answer_code = self.request.get('triviaAnswer')
		answer = MKTriviaAnswer()
		question = MKTriviaQuestion.get_by_id(int(question_code))
		question_answer = MKTriviaPossibleAnswer.get_by_id(int(answer_code))
		answer.answered_by = self.current_student_user
		answer.question = question
		answer.answered = question_answer
		answer.put()
		
		#result_icon = 'ok'
		
		feedback = question_answer.question.trivia.default_wrong_feedback
		
		if(question_answer.is_correct):
			result_icon = 'ok'
			
			feedback = question_answer.question.trivia.default_correct_feedback
		
		if(question_answer.feedback_text):
			feedback = question_answer.feedback_text
		
		if(question.general_feedback):
			feedback = question.general_feedback
				
			
		kid_data = ''
		kid_face = ''
		if self.current_student_user.student_avatar:
		 	kid_data = self.current_student_user.student_avatar.sex + "-" + self.current_student_user.student_avatar.prefix + "-stand"
			if(question_answer.is_correct):
				kid_face = self.current_student_user.student_avatar.sex + "-" + self.current_student_user.student_avatar.prefix + "-ok"
		values = { 'bubble_data' : 	question.phrase,'feedback' : feedback, 'flash' : self.flash , 'answer': answer, 'kid_data' : kid_data, 'kid_face' :kid_face}
		
		self.render('answer', template_values=values)

def main():
  application = webapp.WSGIApplication([('/trivia/answer/', TriviaAnswerHandler),
										('/trivia/*', TriviaIndexHandler)],
                                       debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
