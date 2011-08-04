from lib.gaesessions import SessionMiddleware
import datetime
# suggestion: generate your own random key using os.urandom(64)
# WARNING: Make sure you run os.urandom(64) OFFLINE and copy/paste the output to
# this file.  If you use os.urandom() to *dynamically* generate your key at
# runtime then any existing sessions will become junk every time you start,
# deploy, or update your app!
import os
COOKIE_KEY = ',\xf2\x07\x07\xfcc\xaf\xba,\xf1\xe9\xb7\x9dj\xa3\x08\x0c\xe63f\xf9b\xd9\xe0\x87\x83;g\x1aX\xb5\tN\xb0b\xe8\xb3\x1c\xa8H1\xc6[\x11\x05\xc6\x94\xad\x81r!\x16\x9d\xd8\xca\xf8`0\xfc\x879\xf2\xc2'

def webapp_add_wsgi_middleware(app):
  from google.appengine.ext.appstats import recording
  app = SessionMiddleware(app, cookie_key=COOKIE_KEY)
  app = recording.appstats_wsgi_middleware(app)
  return app
