import os
import shlex
from os.path import join, dirname, abspath


def location(path):
    return abspath(join(dirname(abspath(__file__)), path))


ADMINS = shlex.split(os.environ.get('ADMINS', 'mariocesar.c50@gmail.com'))

GOOGLE_SECRET = os.environ.get('GOOGLE_SECRET', None)
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', None)

GOOGLE_AUTHORIZE_URL = 'https://accounts.google.com/o/oauth2/auth'
GOOGLE_ACCESS_TOKEN_URL = 'https://accounts.google.com/o/oauth2/token'
GOOGLE_ENDPOINT_USERINFO = 'https://www.googleapis.com/oauth2/v3/userinfo'

MONGODB_DSN = 'mongodb://localhost:27017'

WIKIPY_MONGODB_DSN = 'mongodb://localhost:27017/{{ cookiecutter.project_module }}'

AUTH_LOGIN_URL = '/auth/login/'
AUTH_LOGIN_REDIRECT = '/'

ALLOWED_HOSTS = shlex.split(os.environ.get('ALLOWED_HOSTS', '127.0.0.1:8000'))

TEMPLATES_DIRS = (
    location('templates'),
)

STATIC_ROOT = location('../../public/static')
MEDIA_ROOT = location('../../public/media')
