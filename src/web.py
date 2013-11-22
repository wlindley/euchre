import webapp2
from webapp2_extras import sessions

#untested
class SessionRequestHandler(webapp2.RequestHandler):
	def dispatch(self):
		self.sessionStore = sessions.get_store(request=self.request)
		try:
			webapp2.RequestHandler.dispatch(self)
		finally:
			self.sessionStore.save_sessions(self.response)

	@webapp2.cached_property
	def session(self):
		return self.sessionStore.get_session()