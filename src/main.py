from wsgiref.handlers import CGIHandler

import settings

from app import app

if __name__ == '__main__':
    if settings.DEBUG:
        # Run debugged app
        from werkzeug_debugger_appengine import get_debugged_app
        app.debug = True
        debugged_app = get_debugged_app(app)
        CGIHandler().run(debugged_app)
    else:
        # Run production app
        from google.appengine.ext.webapp.util import run_wsgi_app
        run_wsgi_app(app)

