'''AMPT manager database models'''

import datetime
from peewee import *
from flask import Flask
from flask_login import UserMixin
from playhouse.flask_utils import FlaskDB

from ..web import app
from .. import settings
from ..web.crypt import bcrypt

__all__ = ['User', 'ProbeGenerator', 'EventMonitor', 'MonitoredSegment',
           'ReceivedProbeLog', 'GeneratedProbeLog']

# List of supported EventMonitor types
MONITOR_TYPES = [
    ('bro', 'Bro sensor'),
    ('snort', 'Snort sensor'),
    ('suricata', 'Suricata sensor'),
]
# List of supported probe IP protocols
PROBE_PROTOCOLS = [
    ('tcp', 'TCP'),
    ('udp', 'UDP'),
]
# Support logs from event monitors that don't include IP protocol
LOG_PROBE_PROTOCOLS = PROBE_PROTOCOLS + [('unspecified', 'Unspecified')]

ampt_db = SqliteDatabase(app.config['DATABASE'])
database = FlaskDB(app, ampt_db)

class BaseModel(database.Model):
    pass

class User(BaseModel, UserMixin):
    username = CharField(max_length=75, unique=True, help_text='User name')
    display_name = CharField(max_length=75, help_text='User name')
    password = CharField(max_length=255, help_text='Password')
    email = CharField(max_length=150, unique=True, help_text='User email address')
    active = BooleanField(default=True)

    def check_password(self, password):
        'Verify supplied user password against stored hash'
        return bcrypt.check_password_hash(self.password, password)

    def __unicode__(self):
        return '%s (%s)' % (self.username, self.display_name)

class ProbeGenerator(BaseModel):
    name = CharField(max_length=75, unique=True,
                     help_text='Name of generator node')
    address = CharField(max_length=150,
                        help_text='Address (hostname or IP) of generator node')
    port = IntegerField(default=settings.probe_generator_default_port)
    auth_key = CharField(max_length=150,
                         help_text='Authentication key for generator node')
    active = BooleanField(default=True)
    created_date = DateField(default=datetime.datetime.utcnow,
                             help_text='Date generator was added '
                                       'to configuration')
    modified_date = DateField(default=datetime.datetime.utcnow,
                              help_text='Date generator was last modified')
    created_by       = ForeignKeyField(
                           User,
                           related_name='created_probegenerator_set',
                           help_text='User that added generator'
                       )
    last_modified_by = ForeignKeyField(
                           User,
                           related_name='modified_probegenerator_set',
                           help_text='User that modified generator'
                       )

    class Meta:
        # Unique multi-column index on generator address/port
        indexes = (
            (('address', 'port'), True),
        )

    def __unicode__(self):
        return '%s (%s:%s)' % (self.name, self.address, self.port)

class EventMonitor(BaseModel):
    hostname = CharField(max_length=150, help_text='Hostname of event monitor system')
    description = CharField(max_length=150, help_text='Description of event monitor system')
    type = CharField(choices=MONITOR_TYPES, help_text='Sensor type')
    auth_key = CharField(max_length=150,
                         help_text='Authentication key for monitor node')
    active = BooleanField(default=True)
    created_date = DateField(default=datetime.datetime.utcnow, help_text='Date monitor was added to configuration')
    modified_date = DateField(default=datetime.datetime.utcnow, help_text='Date monitor was last modified')
    created_by = ForeignKeyField(User, related_name='created_eventmonitor_set', help_text='User that added monitor')
    last_modified_by = ForeignKeyField(User, related_name='modified_eventmonitor_set', help_text='User that modified monitor')

    class Meta:
        # Unique multi-column index on generator hostname/type
        indexes = (
            (('hostname', 'type'), True),
        )

    def get_type_label(self):
        'Return display value for monitor type choice field'
        return dict(MONITOR_TYPES)[self.type]

    def __unicode__(self):
        return '%s (%s)' % (self.hostname, self.get_type_label())

class MonitoredSegment(BaseModel):
    name = CharField(max_length=75, unique=True, help_text='Name of monitored segment')
    description = CharField(max_length=150, help_text='Description of monitored segment')
    dest_addr = CharField(verbose_name='destination address', help_text='Destination address for target of probe packet')
    dest_port = IntegerField(verbose_name='destination port', help_text='Destination port for target of probe packet')
    protocol = CharField(max_length=3, choices=PROBE_PROTOCOLS, help_text='IP protocol for probe packet')
    generator = ForeignKeyField(ProbeGenerator, help_text='Generator from which to emit probes')
    active = BooleanField(default=True)
    created_date = DateField(default=datetime.datetime.utcnow, help_text='Date segment was added to configuration')
    modified_date = DateField(default=datetime.datetime.utcnow, help_text='Date segment was last modified')
    created_by = ForeignKeyField(User, related_name='created_monitoredsegment_set', help_text='User that added segment to configuration')
    last_modified_by = ForeignKeyField(User, related_name='modified_monitoredsegment_set', help_text='User that modified configuration')

    class Meta:
        # Unique multi-column index on segment dest_addr/dest_port
        indexes = (
            (('dest_addr', 'dest_port'), True),
        )

    def get_protocol_label(self):
        'Return display value for protocol choice field'
        return dict(PROBE_PROTOCOLS)[self.protocol]

    def __unicode__(self):
        return '%s (%s/%s/%s)' % (self.name, self.dest_addr,
                                  self.dest_port, self.protocol)

class ReceivedProbeLog(BaseModel):
    monitor = ForeignKeyField(EventMonitor, help_text='Event Monitor that delivered probe log')
    src_addr = CharField(help_text='Source IP address from probe packet alert')
    dest_addr = CharField(help_text='Destination IP address from probe packet alert')
    src_port = IntegerField(help_text='Source port from probe packet alert')
    dest_port = IntegerField(help_text='Destination port from probe packet alert')
    protocol = CharField(choices=LOG_PROBE_PROTOCOLS, help_text='IP protocol from probe packet alert')
    hostname = CharField(help_text='Hostname of remote AMPT monitor')
    plugin_name = CharField(help_text='Name of plugin handling event on remote AMPT monitor')
    recv_time = DateTimeField(default=datetime.datetime.utcnow, help_text='Timestamp for event log receipt by manager')
    alert_time = DateTimeField(help_text='Timestamp for probe alert creation on reporting sensor device')
    segment = ForeignKeyField(MonitoredSegment, help_text='Monitored Segment match for probe log')

    def get_protocol_label(self):
        'Return display value for protocol choice field'
        return dict(LOG_PROBE_PROTOCOLS)[self.protocol]

class GeneratedProbeLog(BaseModel):
    probe_generator = ForeignKeyField(ProbeGenerator)
    monitored_segment = ForeignKeyField(MonitoredSegment)
    send_time = DateTimeField(default=datetime.datetime.utcnow)

