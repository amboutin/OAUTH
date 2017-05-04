# Programmer: Aaron Boutin, ONID: boutina
# Cites: Much help came from WebApp2 documentation, StackOverFlow, and developers.google.com

from google.appengine.ext import ndb
import webapp2
import json
import logging
from random import randint
from google.appengine.api import urlfetch
import urllib
from webapp2_extras import sessions

class BaseHandler(webapp2.RequestHandler):
    def dispatch(self):
        self.session_store = sessions.get_store(request=self.request)

        try:
            webapp2.RequestHandler.dispatch(self)
        finally:
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        return self.session_store.get_session()

#################################################################################################################
class MainPage(BaseHandler):
    def get(self):
    	destination = "https://accounts.google.com/o/oauth2/v2/auth"
    	amp = "&"
    	eq = "="
    	clientID = "client_id=548315109344-jacnggnkqf6n8l5t03jcusfti0gjno7b.apps.googleusercontent.com"
    	secretCode = "TotesASecret" + str(randint(0,99999999))
    	state = "state=" + secretCode
    	self.session['state'] = secretCode
    	redirect = "redirect_uri=http://localhost:8080/redirect"
    	uri = destination + "?" + "response_type=code" + amp + "scope=email" + amp + state + amp + clientID + amp + redirect
        self.response.out.write("""
          <html>
          <head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/></head>
				<body style="background-color:#13a880;margin-left:30px;text-align:center;position: absolute;top: 50%;left: 50%;margin-right: -50%;transform: translate(-50%, -50%)">
   
              	<div><p>Welcome to a page testing OAUTH 2.0, where I will take you on a journey away to Google's OAUTH endpoint and back.<br> 
              	If it is alright with you, I will request access to your mail. PLEASE!?!?</p></div>
                <div></div>
                <p>Now, let's get this show on the road! --Click THERE -->><a href=""" + uri + """>To Google OAUTH</a></p>

            </body>
          </html>""")

class RedirectPage(BaseHandler):
	def get(self):
		code = self.request.get('code')
		stateVer = self.request.get('state')
		if self.session.get('state') == stateVer:
			logging.warning(self.session.get('state'))
			string = "hello"
			if code != '':
				payload = {'grant_type': 'authorization_code',
				 'code': code,
				 'client_id': '548315109344-jacnggnkqf6n8l5t03jcusfti0gjno7b.apps.googleusercontent.com',
				 'client_secret': '7wZEjBrf1NQWzNyTfiQ25ZPu',
				 'redirect_uri': 'http://localhost:8080/redirect'}

				try:
					form_data = urllib.urlencode(payload)
					headers = {'Content-Type': 'application/x-www-form-urlencoded'}
					result = urlfetch.fetch(url='https://www.googleapis.com/oauth2/v4/token',payload=form_data,method=urlfetch.POST,headers=headers)
					string = json.loads(result.content)

				except urlfetch.Error:
					logging.exception('Caught exception fetching url')

				logging.warning("Are we getting here?")
				logging.warning(string["access_token"])			
				url = 'https://www.googleapis.com/plus/v1/people/me'
				token = "Bearer " + string["access_token"]
				try:
					logging.warning("In Try")
					result = urlfetch.fetch(url=url, headers={"Authorization" : token})
					string = json.loads(result.content)
					#self.response.write(result.content)
					logging.warning(result.status_code)				
					if result.status_code == 200:
						logging.warning("Are we getting here?")
						self.response.out.write("""
				          <html>
				          	<head>
								<meta http-equiv="content-type" content="text/html; charset=utf-8" />
				          	</head>
				            <body style="background-color:#13a880;margin-left:30px;text-align:center;position: absolute;top: 50%;left: 50%;margin-right: -50%;transform: translate(-50%, -50%)">				   
				              	<div><p>Welcome back from the OAUTH Process!<br> 
				              	When you got back, behind the scenes I quickly took a secret code, reconfirmed myself with Google,<br>
				              	then took the recieved token and finally requested some of your info regarding your mail:<br>
				              	<span style="color:white">Name:</span> <span style="color:blue">""" + string["displayName"] + """</span><br>
				              	<span style="color:white">URL:</span> <span style="color:blue">""" + string["url"] + """</span><br>
				              	I also am letting you know the inital state code I used for my own further verification in the process<br>
				              	<span style="color:white">state:</span> <span style="color:blue">""" + self.session.get('state') + """</span><br>
				              	Don't worry about this being exposed as the state value is randomly generated with each request. <br>
				              	Thank you for participating in my learning experience!</p></div>
				                <div></div>
				                <p></p>

				            </body>
				          </html>""")
				except urlfetch.Error:
					logging.exception('Caught exception fetching url')
		else:
			self.response.out.write("Incorrect state")

config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'boutina',
}
allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods
app = webapp2.WSGIApplication([
	('/', MainPage),
	('/redirect', RedirectPage)
], debug=True, config=config)		