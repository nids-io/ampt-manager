'''
ampt-manager Flask app and management commands

'''
import pkg_resources


__version__ = pkg_resources.get_distribution('ampt_manager').version
__url__ = 'https://github.com/nids-io/ampt-manager'
__pkgtitle__ = 'AMPT Manager'

def get_version():
    'Return software version info'
    return u'{} {}'.format(__pkgtitle__, __version__)
