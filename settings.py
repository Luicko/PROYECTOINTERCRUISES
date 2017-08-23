import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

DEBUG = False
DEBUG_TB_ENABLED = False

SECRET_KEY = 'z\xd1\xdcoR\xff\x1bR%U\x95T\x10\x0b20\xf8\xc136D\x89\xb5\x19'