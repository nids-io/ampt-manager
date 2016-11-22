'''
Bcrypt password hashing for Flask app.
'''

from flask_bcrypt import Bcrypt

from . import app

bcrypt = Bcrypt(app)

