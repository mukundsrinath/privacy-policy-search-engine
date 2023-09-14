"""
WSGI config for privaseer project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os
import sys
import traceback
import time
import signal
exec(open("/data/privaseer/venv/bin/activate_this.py").read(), {'__file__': "/data/privaseer/venv/bin/activate_this.py"})

path = '/data/privaseer'
if path not in sys.path:
    sys.path.append(path)

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'privaseer.settings')
try:
    application = get_wsgi_application()
    print ('WSGI without exception')
except Exception:
    print ('handling WSGI exception')
    # Error loading applications
    if 'mod_wsgi' in sys.modules:
        traceback.print_exc()
        os.kill(os.getpid(), signal.SIGINT)
        time.sleep(2.5)
