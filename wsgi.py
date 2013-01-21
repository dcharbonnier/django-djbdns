import os
import django.core.handlers.wsgi
from path import path
import sys
sys.path.append(path(__file__).abspath().dirname())
os.environ["CELERY_LOADER"] = "django"
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings.production'
application = django.core.handlers.wsgi.WSGIHandler()

applications = {'/':'application', }
