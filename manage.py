#!/usr/bin/env python
import os
import sys


VIRTUAL_ENV = os.getenv('VIRTUAL_ENV')

if os.environ.get('DJANGO_SETTINGS_MODULE',None) is None:
  os.environ['DJANGO_SETTINGS_MODULE']='settings.development'
  print "Using settings development"

if len(sys.argv) == 1:
    sys.argv.append('runserver')

sys.path.append(os.getenv('VIRTUAL_ENV'))



from django.core.management import execute_from_command_line

import imp
try:
    imp.find_module('settings') # Assumed to be in the same directory.
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n" % __file__)
    sys.exit(1)

if __name__ == "__main__":
    execute_from_command_line()
