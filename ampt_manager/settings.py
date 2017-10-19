'''
Base/default settings for ampt_manager.

Settings with uppercase names will be set in Flask's config. Lowercase
settings may be used for other purposes.
'''

import logging

DEBUG = False

CONSOLE_LOG_FORMATTER = logging.Formatter('%(asctime)s: [%(levelname)s] %(message)s')
FILE_LOG_FORMATTER = logging.Formatter('%(asctime)s: [%(levelname)s] %(module)s - %(message)s')
DEBUG_LOG_FORMATTER = logging.Formatter('[%(funcName)s-%(levelname)s] %(asctime)s: %(message)s')
DEFAULT_LOG_LEVEL = 'warning'
PAGINATION_CNT_LOGS = 50
# Number of MonitoredSegment items to show on app index page. 0 means unlimited.
SEGMENT_LIMIT_INDEX = 0
# HMAC digest name
# May be set to any supported digest name:
# https://docs.python.org/3/library/hashlib.html#hashlib.new
HMAC_DIGEST = 'sha256'

# Default name for configuration file
default_config_name = 'ampt_manager.conf'
# Default name for database if not specified by user
default_database_name = 'ampt_manager.db'
# Default log file names
default_log_name = 'ampt_manager.log'
default_access_log_name = 'access.log'
# Default server listen address and port
default_listen_address = '127.0.0.1'
default_listen_port = 8443
# Default probe generator listener port
probe_generator_default_port = 5000
# Admin account defaults
default_admin_user = 'admin'
default_admin_pass_length = 10
# Certificate defaults
default_ssl_cert_name = 'ampt_manager.crt'
default_ssl_key_name = 'ampt_manager.key'
default_ssl_key_size = 2048
# Maximum number of Gunicorn workers
gunicorn_workers_max = 5
# Counter database defaults
default_counter_db_name = 'ampt_manager.ctr'
counter_db_init_val = 0
