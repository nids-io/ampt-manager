'''
AMPT manager probe packet dispatcher.

Dispatches monitoring probe requests to AMPT generators.
'''

import random
import logging
import requests

from .web import app
from .db.models import *


app.config.from_envvar('AMPT_MANAGER_SETTINGS')

class ProbeRequest(object):
    '''
    Probe dispatch request.

    Encapsulates data related to a monitored segment and associated probe
    generator so that a request to the generator can be sent.

    '''
    def __init__(self, segment):
        self.segment = segment
        self.generator = segment.generator

    def dispatch_probe_request(self):
        'Send probe request for monitored segment to generator'
        if not self.generator.active:
            errmsg = ('aborting probe generation for {segment} '
                      '- {generator} is inactive')
            app.logger.warning(errmsg.format(segment=self.segment,
                                             generator=self.generator))
            return

        params = {
            'dest_addr': self.segment.dest_addr,
            'dest_port': self.segment.dest_port,
            'src_port': random.randrange(1024, 65535),
            'proto': self.segment.protocol,
        }
        generator = 'http://{address}:{port}/api/generate_probe'.format(
            address=self.generator.address, port=self.generator.port)
        try:
            r = requests.get(generator, params=params)
        except requests.exceptions.ConnectionError as e:
            errmsg = ('failure dispatching probe request to {generator} '
                      '(id={generator_id}) for {segment} '
                      '(id={segment_id}): {err}')
            app.logger.error(errmsg.format(generator=self.generator,
                                           generator_id=self.generator.id,
                                           segment=self.segment,
                                           segment_id=self.segment.id,
                                           err=e))
            return

        if r.status_code == 200:
            # Likely success, log it as such
            response_data = r.json()
            msg = ('{generator} (id={generator_id}) accepted probe '
                   'submission for {segment} (detail: {detail})')
            app.logger.info(msg.format(generator=self.generator,
                                       generator_id=self.generator.id,
                                       detail=response_data,
                                       segment=self.segment))
            self.log_probe_dispatch()
        else:
            # Likely HTTP error, raise exception for caller
            r.raise_for_status()

    def log_probe_dispatch(self):
        'Log probe request dispatch to generator'
        pl = GeneratedProbeLog()
        pl.probe_generator = self.generator
        pl.monitored_segment = self.segment
        pl.save()


def send_probe_requests(args):
    '''
    Send probe requests for monitored segments to generator nodes

    '''
    # TODO: fix how this is duplicating the Flask app logging configuration from
    # the runserver module; need moar DRY
    app_formatter = app.config['CONSOLE_LOG_FORMATTER']
    file_formatter = app.config['FILE_LOG_FORMATTER']
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel((args.loglevel or app.config.get('LOGLEVEL')).upper())
    stream_handler.setFormatter(app_formatter)
    app.logger.addHandler(stream_handler)
    app.logger.setLevel((args.loglevel or app.config.get('LOGLEVEL')).upper())

    if app.config.get('LOGFILE'):
        file_handler = logging.FileHandler(app.config['LOGFILE'])
        file_handler.setLevel((args.loglevel or app.config.get('LOGLEVEL')).upper())
        file_handler.setFormatter(file_formatter)
        app.logger.addHandler(file_handler)
        app.logger.setLevel((args.loglevel or app.config.get('LOGLEVEL')).upper())

    # Dispatch
    active_segments = MonitoredSegment.select().where(MonitoredSegment.active == True)
    msg = 'preparing to dispatch probe requests for {cnt} monitored segments'
    app.logger.info(msg.format(cnt=active_segments.count()))

    for segment in active_segments:
        pr = ProbeRequest(segment)
        pr.dispatch_probe_request()

