import os
DEBUG = os.environ.get('SERVER_SOFTWARE', 'Dev').startswith('Dev')
