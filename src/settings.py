import os
DEBUG = os.environ.get('SERVER_SOFTWARE', 'Dev').startswith('Dev')


# *** override these in local_settings.py ***
BITCOIN_HOST = '127.0.0.1'
BITCOIN_PORT = 8332
BITCOIN_USER = "test"
BITCOIN_PASS = "test"
BITCOIN_ACCOUNT = DEBUG and "test_debug" or "test"


from local_settings import *
