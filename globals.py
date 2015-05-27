#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import jinja2
from datastore_classes import Account

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

no_match_active_id = '0'
host_char = '0'

def get_or_create_account(user):
    """Called periodically (all pages) to get the current user, or to create a new one if null"""
    account = Account.get_or_insert(user.user_id(), nickname=user.nickname())
    return account


def display_error_page(self, referrer, message):
    template = JINJA_ENVIRONMENT.get_template('templates/error_page.html')
    self.response.write(template.render({'Message': message, 'Back_Link': referrer}))