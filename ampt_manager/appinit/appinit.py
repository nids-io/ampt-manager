'''
New AMPT Manager instance initialization

'''

import os
import os.path
import stat
import random
import string

from jinja2 import Environment, PackageLoader

from .. import settings


def prep_counter_db(db_path, user=None, group=None):
    '''Initialize new counter DB file.

    If user and group are specified, caller is a privileged process specifying
    ownership of file by less privileged user/group.

    '''
    from ..web.validators import persist_counter
    try:
        persist_counter(db_path)
    except FileNotFoundError as e:
        os.makedirs(os.path.dirname(db_path))
        persist_counter(db_path)
    if user is not None and group is not None:
        chown(db_path, user, group)

def get_random_admin_pass(n):
    '''
    Return random alphanumeric string of length `n` for default admin
    account password

    '''
    return ''.join(random.SystemRandom().choice(
        string.ascii_letters + string.digits) for _ in range(n))

def render_template(template, **context):
    'Render requested template with specified context'

    pkg = __name__.rsplit('.', 1)[0]
    env = Environment(loader=PackageLoader(pkg, '.'))
    template = env.get_template(template)
    return template.render(**context)

def initialize_config(args):
    '''
    Initialize new AMPT manager instance.

    Create new ampt_manager configuration directory and database. Populate
    config file with basic settings.
    '''

    configdir = os.path.abspath(args.path)
    try:
        os.makedirs(configdir)
    except FileExistsError as e:
        if not args.force:
            raise

    configfile = os.path.join(configdir, settings.default_config_name)
    dbpath = os.path.join(configdir, settings.default_database_name)
    logpath = os.path.join(configdir, settings.default_log_name)
    access_logpath = os.path.join(configdir, settings.default_access_log_name)
    sslcertpath = os.path.join(configdir, settings.default_ssl_cert_name)
    sslkeypath = os.path.join(configdir, settings.default_ssl_key_name)
    counterpath = os.path.join(configdir, settings.default_counter_db_name)
    secret_key = os.urandom(24)

    # Write out new configuration
    with open(configfile, mode='w', encoding='utf-8') as conf:
        conf.write(render_template('conf.j2',
            dbpath=dbpath,
            secret_key=secret_key,
            logpath=logpath,
            access_logpath=access_logpath,
            loglevel=settings.DEFAULT_LOG_LEVEL,
            listen_address=settings.default_listen_address,
            listen_port=settings.default_listen_port,
            sslcertpath=sslcertpath,
            sslkeypath=sslkeypath,
            counterpath=counterpath))

    # Import done late so that models have a database configuration when loaded
    os.environ['AMPT_MANAGER_SETTINGS'] = configfile

    from ..web import app
    app.config.from_envvar('AMPT_MANAGER_SETTINGS')

    from ..db.database import initialize_database

    admin_user = settings.default_admin_user
    admin_pass = get_random_admin_pass(settings.default_admin_pass_length)
    initialize_database(args, admin_user, admin_pass)

    # Set restrictive permissions to configuration file and database
    for f in (configfile, dbpath):
        os.chmod(f, stat.S_IRUSR|stat.S_IWUSR)

    # Create self-signed certificate and key for SSL support
    from .certificate import create_self_signed_cert
    create_self_signed_cert(configdir)

    # Initialize counter file (used for HMAC verification on AMPT Monitor
    # communications)
    prep_counter_db(counterpath)

    print(render_template('message.j2',
                          config_file=configfile,
                          config_file_basename=settings.default_config_name,
                          username=admin_user,
                          password=admin_pass))

