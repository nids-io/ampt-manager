import os
import logging
from logging import StreamHandler, FileHandler

from flask import Flask, render_template, jsonify
from flask_login import LoginManager
from flask_debugtoolbar import DebugToolbarExtension
from flask_misaka import Misaka
from flask_moment import Moment

from ..exceptions import InvalidUsage

app = Flask('ampt_manager')
app.config.from_object('ampt_manager.settings')
app.config.from_envvar('AMPT_MANAGER_SETTINGS', silent=True)

# Set up debug mode if enabled
if os.environ.get('FLASK_DEBUG'):
    app.debug = True
    warn_msg = ('Debug mode is enabled! This is not recommended when running '
                'in production or when the server is exposed to '
                'untrusted clients.')
    app.logger.warning(warn_msg)

# Install local error handlers
@app.errorhandler(404)
def page_not_found(e):
    'Supply custom 404 page'
    return render_template('404.html'), 404

@app.errorhandler(500)
def page_not_found(e):
    'Supply custom 500 page'
    return render_template('500.html'), 500

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    'Supply useful error message to remote ampt-monitor clients sending logs'
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message = False
login_manager.init_app(app)

# Activate the debug toolbar (only active when in debug mode).
# No SQLAlchemy here so disable panel.
toolbar = DebugToolbarExtension()
toolbar.init_app(app)
app.config['DEBUG_TB_PANELS'] = tuple(x for x in app.config['DEBUG_TB_PANELS'] if x not in
    'flask_debugtoolbar.panels.sqlalchemy.SQLAlchemyDebugPanel',
)

# Activate Flask-Moment
moment = Moment(app)

# Activate Flask-Misaka
Misaka(app,
       autolink=True,
       fenced_code=True,
       xhtml=True)

@login_manager.user_loader
def load_user(userid):
    from ..db.models import User
    try:
        return User.get(User.id==userid)
    except User.DoesNotExist:
        return None


from . import views
