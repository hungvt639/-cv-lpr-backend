"""
WSGI config for Main project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""
# from Users.permissions import createGroup
# from API.function.addlocationdatabase import add_location
import os

# from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Main.settings')

# application = get_wsgi_application()

# try:
#     createGroup()
# except:
#     pass

# add_location()