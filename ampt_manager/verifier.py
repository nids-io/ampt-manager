'''
AMPT probe event segment health verification

'''
import logging
import datetime

from .web import app
from .db.models import MonitoredSegment, ReceivedProbeLog


from flask.logging import default_handler
app.logger.removeHandler(default_handler)

def verify_probe_events(args):
    '''
    Verify receipt of probe logs for monitored segments

    Check all active monitored segments for probe events received within
    specified timeframe and trigger alerting for segments with no event
    logs on record.

    '''
    retval = 0

    # XXX: fix how this is duplicating the Flask app logging configuration from
    # the runserver module; need moar DRY
    app_formatter = app.config['LOG_FORMATTER']
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel((args.loglevel or app.config.get('LOGLEVEL')).upper())
    stream_handler.setFormatter(app_formatter)
    app.logger.addHandler(stream_handler)
    app.logger.setLevel((args.loglevel or app.config.get('LOGLEVEL')).upper())

    if app.config.get('LOGFILE'):
        file_handler = logging.FileHandler(app.config['LOGFILE'])
        file_handler.setLevel((args.loglevel or app.config.get('LOGLEVEL')).upper())
        file_handler.setFormatter(app_formatter)
        app.logger.addHandler(file_handler)
        app.logger.setLevel((args.loglevel or app.config.get('LOGLEVEL')).upper())

    active_segments = (MonitoredSegment.select()
                                       .where(MonitoredSegment.active == True)
                                       .order_by(MonitoredSegment.name))
    active_segments_count = active_segments.count()
    msg = 'active segments: {segments}'
    app.logger.debug(msg.format(segments=', '.join(['id={id}/{name}'
                     .format(id=s.id, name=s.name) for s in active_segments])))
    if not active_segments_count:
        app.logger.warning('no active monitored segments are configured')
        return 1
    else:
        msg = ('verifying {count} monitored {s} for alerts '
               'over previous {period} {m}')
        app.logger.info(msg.format(count=active_segments_count,
                                   period=args.period,
                                   s='segment' if active_segments_count == 1 else 'segments',
                                   m='minute' if args.period == 1 else 'minutes'))

    # Check each segment for any probe alert events occuring between the
    # specified period and now. Because we consult the alert time for the
    # event (the timestamp from the sensor/device that observed the probe),
    # factors such as time delays in event delivery may make it so that very
    # recent alerts that are in the manager's DB but have an alert timestamp
    # that is older than the requested period aren't returned by this query.
    # AMPT admins should adjust (increase) requested periods accordingly.
    #
    # XXX: should attempt to refactor and collect all data in one query
    # rather than querying for each segment individually.
    #
    for segment in active_segments:
        start_time = (datetime.datetime.utcnow()
                      - datetime.timedelta(minutes=args.period))
        end_time = datetime.datetime.utcnow()
        app.logger.debug('alert time period between {start} - {end}'
                         .format(start=start_time, end=end_time))
        app.logger.debug('verifying segment id={id}/{name}'
                         .format(id=segment.id, name=segment.name))
        recent_events = (segment.receivedprobelog_set
                         .where(ReceivedProbeLog.alert_time
                                .between(datetime.datetime.utcnow() - datetime.timedelta(minutes=args.period),
                                         datetime.datetime.utcnow())))
        if not recent_events:
            msg = ('no probe logs received for {segment} segment '
                   'within previous {m} minute period')
            app.logger.warning(msg.format(segment=segment.name,
                                          m=args.period))
            retval = 1
        else:
            msg = ('{count} probe logs received for {segment} segment within '
                   'previous {period} minute period')
            app.logger.info(msg.format(count=recent_events.count(),
                                       segment=segment.name,
                                       period=args.period))
    return retval
