import os
from flask import Flask, request
from flask.ext.login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from settings import basedir

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('intercruises.settings')
app.config.from_pyfile('settings.conf')

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

db = SQLAlchemy(app)

Bootstrap(app)

from . import views, models, settings

@lm.user_loader
def load_user(id):
    """
    LoginManager callback to assign `current_user` proxy object.
    :param id: User ID
    :returns: :class:`User`
    """
    return models.User.query.get(int(id))