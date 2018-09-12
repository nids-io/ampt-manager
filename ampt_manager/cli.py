'AMPT Manager CLI invocation'

import os
import sys
import argparse

from .appinit.appinit import initialize_config


LOGLEVEL_CHOICES = ['debug', 'info', 'warning', 'error', 'critical']

def _run_server(args):
    os.environ['AMPT_MANAGER_SETTINGS'] = args.configfile
    if args.debug:
        os.environ['FLASK_DEBUG'] = '1'
    from .web.runserver import run_server
    run_server(args)

def _verify_probe_events(args):
    os.environ['AMPT_MANAGER_SETTINGS'] = args.configfile
    from .verifier import verify_probe_events
    # We exit with the status code of the verification function in order
    # to signal success or any failure in segment verification
    sys.exit(verify_probe_events(args))

def _send_probe_requests(args):
    os.environ['AMPT_MANAGER_SETTINGS'] = args.configfile
    from .dispatcher import send_probe_requests
    send_probe_requests(args)

def valid_configfile(s):
    'Validate that specified argument is a file path that can be opened'
    try:
        with open(s, 'r') as f:
            pass
    except Exception as e:
        msg = 'specified file does not exist'
        raise argparse.ArgumentTypeError(e.strerror)
    return s

def main():
    main_description = 'Manager server for the AMPT passive tools monitor'
    parser = argparse.ArgumentParser(description=main_description)
    parser.add_argument('-V', '--version', action='store_true',
                        help='display version and exit')

    subparsers = parser.add_subparsers()

    init_description = 'Initialize new AMPT manager configuration'
    parser_init = subparsers.add_parser('init', description=init_description,
                                        help='initialize app configuration')
    parser_init.add_argument('path', help='configuration directory path')
    parser_init.add_argument('-f', '--force', action='store_true',
                             help='force configuration initialization in '
                                  'existing directory')
    parser_init.set_defaults(func=initialize_config)

    run_description = 'Run AMPT manager server'
    parser_run = subparsers.add_parser('run', description=run_description,
                                        help='run manager server ')
    parser_run.add_argument('configfile', type=valid_configfile,
                        help='load app configuration from specified file ')
    parser_run.add_argument('-L', '--listen-address',
                        help='listen for connections on specified IP address '
                             '(default: from config file)')
    parser_run.add_argument('-p', '--listen-port', type=int,
                        help='listen for connections on specified port '
                             '(default: from config file)')
    parser_run.add_argument('-l', '--loglevel', choices=LOGLEVEL_CHOICES,
                            help='set logging verbosity level '
                                 '(default: from config file)')
    parser_run.add_argument('-d', '--debug', action='store_true',
                            help='run app in debug mode (enable Flask DEBUG '
                                 '- never run this in production or '
                                 'publicly exposed)')
    parser_run.set_defaults(func=_run_server)

    generate_description = 'Trigger probes to generators for monitored segments'
    parser_generate = subparsers.add_parser('dispatch',
                                            description=generate_description,
                                            help='send probe requests to '
                                                 'generator node(s)')
    parser_generate.add_argument('configfile', type=valid_configfile,
                                 help='load app configuration from specified file')
    parser_generate.add_argument('-l', '--loglevel', choices=LOGLEVEL_CHOICES,
                                 help='set logging verbosity level '
                                      '(default: from config file)')
    parser_generate.set_defaults(func=_send_probe_requests)

    verify_description = ('Verify monitored segments by checking for '
                         'received probe alerts from sensors')
    parser_verify = subparsers.add_parser('verify',
                                        description=verify_description,
                                        help='verify probe alerting on '
                                             'monitored segments')
    parser_verify.add_argument('configfile', type=valid_configfile,
                              help='load app configuration from specified file')
    parser_verify.add_argument('-p', '--period', type=int, default=30,
                               help='check for probe events '
                                    'received within this many minutes '
                                    '(default: %(default)s)')
    parser_verify.add_argument('-l', '--loglevel', choices=LOGLEVEL_CHOICES,
                                 help='set logging verbosity level '
                                      '(default: from config file)')
    parser_verify.set_defaults(func=_verify_probe_events)

    args = parser.parse_args()

    # Handle special case of version output.
    if args.version:
        from . import get_version
        parser.exit(status=0, message=get_version() + '\n')

    # Error handling for no subcommand called.
    if not hasattr(args, 'func'):
        parser.error('Must specify command to invoke (did you mean to run '
                     'the program)?')

    # Call specified command's function.
    try:
        args.func(args)
    except FileExistsError as e:
        parser.error('Refusing to clobber existing path ({err})'.format(err=e))

