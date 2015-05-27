#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import jinja2
from datastore_classes import Account, account_key, Pair, Match, match_key


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

no_match_active_id = '0'
host_char = '0'


def get_or_create_account(user):
    """Called periodically (all pages) to get the current user, or to create a new one if null"""
    account = Account.get_or_insert(user.user_id(), nickname=user.nickname(), active_match=no_match_active_id)
    if not account.active_match:
        account.active_match = no_match_active_id
    return account


def onto_next_match(user_account, old_match):
    pair_key_val = old_match.key.parent()
    pair = Pair.get_or_insert(pair_key_val.id(), parent=pair_key_val.parent(), current_match_number=-1)

    account = user_account

    if pair_key_val.id() == account.key.id():
        partner = account_key(pair_key_val.parent().id()).get()
    else:
        partner = account_key(pair_key_val.id()).get()

    new_match_key_val = match_key(pair.current_match_number + 1, pair_key_val)

    pair.current_match_number += 1
    pair.put()

    partner.active_match = new_match_key_val.urlsafe()
    partner.put()

    account.active_match = new_match_key_val.urlsafe()
    account.put()

    match = Match.get_or_insert(new_match_key_val.id(), parent=new_match_key_val.parent())
    match.user_1_list = []
    match.user_2_list = []
    match.active = True
    match.put()


def display_error_page(self, referrer, message):
    template = JINJA_ENVIRONMENT.get_template('templates/error_page.html')
    self.response.write(template.render({'Message': message, 'Back_Link': referrer}))