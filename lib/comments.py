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
import time
import datetime
#import controller.sessions.SessionManager
#from appengine_utilities.sessions import Session
from lib.gaesessions import get_current_session
#from controller.appengine_utilities.flash import Flash
#from controller.appengine_utilities.cache import Cache
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db
from google.appengine.api import datastore_errors
from google.appengine.ext.webapp import template
from model.models import *

class LLPostReplyManager():
	
	def __init__(self):
		pass
	
	@staticmethod
	def append_reply(element, replier_name, text):
		try:
			comment = LLPostReply()
			comment.replier_name = replier_name
			comment.reply = cgi.escape(text)
			comment.element_replied = element
			comment.put()
			return comment
		except:
			return None
		
