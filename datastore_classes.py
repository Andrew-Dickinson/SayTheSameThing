from google.appengine.ext import ndb


def pair_key(user_id_1, user_id_2):
    """League keys are based off of the id of the person who commissions them"""
    return ndb.Key(Pair, str(user_id_2), parent=account_key(str(user_id_1)))


def account_key(account_id):
    """Constructs a Datastore key for a account entity with a user id."""
    return ndb.Key(Account, str(account_id))


def match_key(match_id, pair_key_val):
    """Constructs the Datastore key for a match given its match_id"""
    return ndb.Key(Match, str(match_id), parent=pair_key_val)


class Pair(ndb.Model):
    """Stores players in the pair and references to the pair's matches"""
    current_match_number = ndb.IntegerProperty()


class Account(ndb.Model):
    """Stores data for an individual account"""
    nickname = ndb.StringProperty()
    active_match = ndb.StringProperty()


class Match(ndb.Model):
    """Stores all the data for an active or past match"""
    active = ndb.BooleanProperty()
    won = ndb.BooleanProperty()
    user_1_list = ndb.StringProperty(repeated=True)
    user_2_list = ndb.StringProperty(repeated=True)