#!/usr/bin/env python

import logging
import webapp2
import jinja2
import os
import globals

from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class MainHandler(webapp2.RequestHandler):
    def get(self):
        # Checks for active Google account session
        user = users.get_current_user()

        #Check if user is logged in
        if user is None:
            #Send html data to browser
            template_values = {'logged_out': users.create_login_url('/')}
            template = JINJA_ENVIRONMENT.get_template('templates/index.html')
            self.response.write(template.render(template_values))
        else:
            logout_url = users.create_logout_url('/')
            account = globals.get_or_create_account(user)
            match_key_id = account.active_match

            # if match_key_id == globals.no_match_active_id:
            #     # User should be prompted to start a match
            # else:
            #     # Display the match screen


            #Send html data to browser
            template_values = {'user': user.nickname(),
                               'logout_url': logout_url
                               }
            template = JINJA_ENVIRONMENT.get_template('templates/index.html')
            self.response.write(template.render(template_values))

    def handle_exception(self, exception, debug_mode):
        if debug_mode:
            super(type(self), self).handle_exception(exception, debug_mode)
        else:
            template = JINJA_ENVIRONMENT.get_template('templates/500.html')
            self.response.write(template.render())


class MatchSubmit(webapp2.RequestHandler):
    def post(self):
        """Handles incoming form data"""
        user = users.get_current_user()
        account = globals.get_or_create_account(user)
        word = self.request.get('word')
        partner = self.request.get('partner_id')



class PageNotFoundHandler(webapp2.RequestHandler):
    def get(self):
        self.error(404)
        template = JINJA_ENVIRONMENT.get_template('templates/404.html')
        self.response.write(template.render())

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/.*', PageNotFoundHandler)
], debug=True)


def main():
    logging.getLogger().setLevel(logging.DEBUG)
    run_wsgi_app(app)

if __name__ == "__main__":
    main()