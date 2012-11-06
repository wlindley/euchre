import cgi
import webapp2
import jinja2
import os

jinjaEnvironment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class IndexPage(webapp2.RequestHandler):
	def get(self):
		templateValues = {}
		template = jinjaEnvironment.get_template('index.html')
		self.response.out.write(template.render(templateValues))

app = webapp2.WSGIApplication([('/', IndexPage)], debug=True)
