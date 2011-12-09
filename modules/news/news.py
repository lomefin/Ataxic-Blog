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
import sys
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db
from google.appengine.api import datastore_errors
from google.appengine.ext.webapp import template
from lib import llhandler
from lib import errors
from model.models import *
from lib import markdown2
from lib import twitter_wrapper

def bitly_url(url):
	import urllib
	from google.appengine.api import urlfetch
	form_fields = {
		"login": "lomefin",
		"apiKey": "R_ecdc45222b96e2c01a7d7f5856c1f589",
		"longUrl": "http://www.ataxic.org/"+url,
		"format":"txt"
	}
	form_data = urllib.urlencode(form_fields)
	url = "http://api.bitly.com/v3/shorten?"+str(form_data)
	
	result = urlfetch.fetch(url=url,
                    method=urlfetch.GET)
	return str(result.content.replace("\n", ""))

class NewsHandler(llhandler.LLHandler):
	
	def base_directory(self):
		return os.path.dirname(__file__)
	
	def internal_get(self):
		if LLNews.all().count() > 0:
			all_news = LLNews.all().order('-date_created')
			latest_news = all_news.fetch(1)[0]
			latest_news.markdown_html = markdown2.markdown(latest_news.text)
			
			tri_news = all_news.fetch(3,offset=1)
			for news in tri_news:
				news.markdown_html = markdown2.markdown(news.text)			
			
			news_list = all_news.fetch(5,offset=4)
			
			values = {'latest':latest_news,'tri_news':tri_news,'news_list':news_list}
			self.render('index',template_values=values)
		else:
			self.render('index')

class AddNewsHandler(llhandler.LLGAEHandler):
	
	def base_directory(self):
		return os.path.dirname(__file__)
	
	def internal_get(self):
		self.render('create')
		
	def internal_post(self):
		try:
			from django.template import defaultfilters
			
			message = LLNews()
			message.title = self.request.get('title')
			message.text = self.request.get('content')
			right_now = ""
			message.slug = defaultfilters.slugify(right_now + message.title)
			message.creator = self.current_account
			message.short_url = bitly_url("/news/"+message.slug)
			message.put()
			self.set_flash('Noticia agregada ('+right_now+")")
		except:
			self.set_flash('No se pudo agregar la noticia',flash_type='error')
		#try:
		twitter_wrapper.tweet(message.title + " " + message.short_url)
		#except Exception as exc:
		#	self.set_flash('No se pudo publicar la noticia ('+ str(exc) +')',flash_type='warning')
		self.redirect('/news/')

class ViewNewsHandler(llhandler.LLHandler):
	
	def base_directory(self):
		return os.path.dirname(__file__)
	
	def internal_get(self,slug):
		news = LLNews.all().filter('slug =',slug).get()

		if news is not None:
			if news.short_url is None:
				news.short_url = bitly_url("/news/"+slug)
				news.put()
			markdown_html = markdown2.markdown(news.text)
			values = {'news':news,'from':self.request.path,'markdown_html':markdown_html}
			self.render('view',template_values=values)
		else:
			self.set_flash('No existe esa noticia',flash_type='errorFlash')
			self.redirect('/news/')

	def get(self,slug):
		self.auth_check()
		self.internal_get(slug)

class EditNewsHandler(llhandler.LLGAEHandler):
	def base_directory(self):
		return os.path.dirname(__file__)
	
	def internal_get(self,slug):
		post = LLNews.all().filter('slug =',slug).get()

		if post is not None:
			markdown_html = markdown2.markdown(post.text)
			values = {'post':post,'from':self.request.path,'markdown_html':markdown_html}
			self.render('view',template_values=values)
		else:
			self.set_flash('No existe esa noticia',flash_type='errorFlash')
			self.redirect('/news/')

	def get(self,slug):
		self.auth_check()
		self.internal_get(slug)
		

	
def main():
  application = webapp.WSGIApplication([('/news/', NewsHandler),
  										('/news/_new',AddNewsHandler),
  										('/news/([a-zA-Z\-0-9]*)',ViewNewsHandler),
										('/news/([a-zA-Z\-0-9]*)/edit',EditNewsHandler),
  										('.*',errors.NotFoundHandler)],
                                       debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
