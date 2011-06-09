import os
DEBUG = os.environ.get('SERVER_SOFTWARE', 'Dev').startswith('Dev')


from google.appengine.ext import db
class Settings(db.Expando):
    @classmethod
    def get_settings(cls, name='default'):
        s = cls.get_by_key_name(name)
        if not s:
            s = cls(key_name=name)
            s.put()        
        return s


# *** override these in local_settings.py ***
BITCOIN_HOST = '127.0.0.1'
BITCOIN_PORT = 8332
BITCOIN_USER = "test"
BITCOIN_PASS = "test"
BITCOIN_ACCOUNT = DEBUG and "test_debug" or "test"


from local_settings import *
