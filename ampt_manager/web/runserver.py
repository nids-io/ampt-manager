'''
Run the application server.

Start Flask app in standalone Gunicorn container using parameters from
configuration file and arguments passed at command line.
'''

from __future__ import unicode_literals
import os
import ssl
import sys
import logging
import multiprocessing

import gunicorn.app.base
from six import iteritems
from flask import __version__ as flask_version

from . import app
from .. import settings
from .. import get_version


MAX_WORKERS = settings.gunicorn_workers_max
CPU_WORKERS = multiprocessing.cpu_count() * 2 + 1

class StandaloneApplication(gunicorn.app.base.BaseApplication):

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super(StandaloneApplication, self).__init__()

        # XXX doesn't quite work as desired - it gets us the new AMPT handler
        # log we do want, as well as the old Gunicorn handler log we don't want.
        gunicorn_err_logger = logging.getLogger('gunicorn.error')
        gunicorn_err_logger.handlers = app.logger.handlers
        gunicorn_err_logger.propagate = False

    def load_config(self):
        config = dict([(key, value) for key, value in iteritems(self.options)
                       if key in self.cfg.settings and value is not None])
        for key, value in iteritems(config):
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


def run_server(args):
    'Load app in a standalone Gunicorn container'

    # XXX
    from flask.logging import default_handler
    app.logger.removeHandler(default_handler)

    # Flask has default stream logging configuration in debug mode, so set
    # log parameters here only for production mode
    app_formatter = app.config['LOG_FORMATTER']
    if not app.debug:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel((args.loglevel or app.config.get('LOGLEVEL')).upper())
        stream_handler.setFormatter(app_formatter)
        app.logger.addHandler(stream_handler)
        app.logger.setLevel((args.loglevel or app.config.get('LOGLEVEL')).upper())
    # Logging to the application logfile occurs regardless of debug mode
    if app.config.get('LOGFILE'):
        file_handler = logging.FileHandler(app.config['LOGFILE'])
        file_handler.setLevel((args.loglevel or app.config.get('LOGLEVEL')).upper())
        file_handler.setFormatter(app_formatter)
        app.logger.addHandler(file_handler)
        app.logger.setLevel((args.loglevel or app.config.get('LOGLEVEL')).upper())

    # Gunicorn options
    # Logging options: these settings apply to Gunicorn and not the application.
    # The server's access logs are always written to the app instance's
    # access logs and not sent to stdout. Error/etc. logs are always sent
    # to stdout.
    # Workers option: allow the number of workers to scale based on available
    # CPU count, but no more than a conservative MAX_WORKERS
    options = {
        'bind': '%s:%s' % (args.listen_address or app.config['LISTEN_ADDRESS'],
                           args.listen_port or app.config['LISTEN_PORT']),
        'workers': CPU_WORKERS if CPU_WORKERS < MAX_WORKERS else MAX_WORKERS,
        'proc_name': 'ampt-manager',
        'certfile': app.config['SERVER_CERTIFICATE'],
        'keyfile': app.config['SERVER_PRIVATE_KEY'],
        'ssl_version': ssl.PROTOCOL_TLS,
        'accesslog': app.config.get('ACCESS_LOGFILE') or '-',
        'errorlog': '-',
        'loglevel': args.loglevel or app.config['LOGLEVEL'],
    }

    sa = StandaloneApplication(app, options)

    ver_dep_msg = ('running on Python %s using Flask %s')
    py_version = '.'.join([str(x) for x in sys.version_info[:3]])
    crypto_msg = ('configuring server for TLS using %s (%s)')
    ssl_version = ssl.get_protocol_name(sa.cfg.ssl_options.get('ssl_version'))
    ciphers = sa.cfg.ssl_options.get('ciphers')
    app.logger.info('starting %s', get_version())
    app.logger.debug(ver_dep_msg, py_version, flask_version)
    app.logger.info(crypto_msg, ssl_version, ssl.OPENSSL_VERSION)

    sa.run()
