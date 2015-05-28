#!/usr/bin/env python

import logging
import webapp2
import jinja2
import os
import globals

from datastore_classes import pair_key, match_key, account_key, Account, Pair, Match

from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
from google.appengine.ext import ndb



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

            user_wordlist = None
            partner_wordlist = None
            match_won = None
            if match_key_id == globals.no_match_active_id:
                match_active = False
            else:
                match_active = True
                match = ndb.Key(urlsafe=match_key_id).get()
                match_won = match.won
                if match.key.parent().parent().id() == account.key.id():
                    user_wordlist = match.user_1_list
                    partner_wordlist = match.user_2_list
                else:
                    partner_wordlist = match.user_1_list
                    user_wordlist = match.user_2_list

                if len(user_wordlist) != len(partner_wordlist):
                    if len(user_wordlist) > len(partner_wordlist):
                        partner_wordlist.append("Waiting...")
                    else:
                        partner_wordlist[-1] = "*******"
                        user_wordlist.append("-")

                user_wordlist = reversed(user_wordlist)
                partner_wordlist = reversed(partner_wordlist)

            update_text = self.request.get('updated')

            #Send html data to browser
            template_values = {'user': user.nickname(),
                               'logout_url': logout_url,
                               'match_key': match_key_id,
                               'match_active': match_active,
                               'match_won': match_won,
                               'update_text': update_text,
                               'user_wordlist': user_wordlist,
                               'partner_wordlist': partner_wordlist,
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
        match_key_id = self.request.get('match_key')

        match = ndb.Key(urlsafe=match_key_id).get()

        if match.active and not match.won:
            user_is_host = match.key.parent().parent().id() == account.key.id()

            if user_is_host:
                user_word_list = match.user_1_list
                partner_word_list = match.user_2_list
            else:
                user_word_list = match.user_2_list
                partner_word_list = match.user_1_list

            if len(user_word_list) <= len(partner_word_list):
                user_word_list.append(word)

            if len(user_word_list) == len(partner_word_list):
                if str.lower(str(user_word_list[-1])) == str.lower(str(partner_word_list[-1])):
                    match.active = False
                    match.won = True

            match.put()

        self.redirect('/')

    def handle_exception(self, exception, debug_mode):
        if debug_mode:
            super(type(self), self).handle_exception(exception, debug_mode)
        else:
            template = JINJA_ENVIRONMENT.get_template('templates/500.html')
            self.response.write(template.render())


class MatchStart(webapp2.RequestHandler):
    def post(self):
        """Handles the start of a partner connection"""
        user = users.get_current_user()
        account = globals.get_or_create_account(user)
        partner_name = self.request.get('partner_nickname')

        partner_name = partner_name.replace("@gmail.com", "")

        partner = Account.query(Account.nickname == partner_name).fetch()

        if partner:
            if partner[0].active_match == globals.no_match_active_id:
                pair_key_val = pair_key(account.key.id(), partner[0].key.id())
                pair = Pair.get_or_insert(pair_key_val.id(), parent=pair_key_val.parent(), current_match_number=-1)
                pair.put()

                match_key_val = match_key(pair.current_match_number + 1, pair_key_val)

                partner[0].active_match = match_key_val.urlsafe()
                partner[0].put()

                account.active_match = match_key_val.urlsafe()
                account.put()

                match = Match.get_or_insert(match_key_val.id(), parent=match_key_val.parent())
                match.put()

                past_match = Match.get_or_insert(str(pair.current_match_number), parent=pair_key_val)

                globals.onto_next_match(account, past_match)

                self.redirect('/')
            else:
                self.redirect("/?updated=User in Game Already")
        else:
            self.redirect("/?updated=Bad Email Address")

    def handle_exception(self, exception, debug_mode):
        if debug_mode:
            super(type(self), self).handle_exception(exception, debug_mode)
        else:
            template = JINJA_ENVIRONMENT.get_template('templates/500.html')
            self.response.write(template.render())


class NewGame(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        account = globals.get_or_create_account(user)
        match_key_id = self.request.get('match_key')
        match = ndb.Key(urlsafe=match_key_id).get()

        pair = match.key.parent().get()

        match.active = False
        if match.won != True:
            match.won = False

        match.put()
        pair.current_match_number += 1
        pair.put()

        globals.onto_next_match(account, match)

        self.redirect('/')

    def handle_exception(self, exception, debug_mode):
        if debug_mode:
            super(type(self), self).handle_exception(exception, debug_mode)
        else:
            template = JINJA_ENVIRONMENT.get_template('templates/500.html')
            self.response.write(template.render())



class PageNotFoundHandler(webapp2.RequestHandler):
    def get(self):
        self.error(404)
        template = JINJA_ENVIRONMENT.get_template('templates/404.html')
        self.response.write(template.render())

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/startMatch', MatchStart),
    ('/playMatch', MatchSubmit),
    ('/newMatch', NewGame),
    ('/.*', PageNotFoundHandler)
], debug=True)


def main():
    logging.getLogger().setLevel(logging.DEBUG)
    run_wsgi_app(app)

if __name__ == "__main__":
    main()