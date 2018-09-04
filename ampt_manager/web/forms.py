'''
Forms for AMPT Manager

'''
from wtforms import (Form, BooleanField, StringField, IntegerField,
                     PasswordField, DecimalField)
from wtforms import SelectField, SubmitField, DateTimeField, validators
from flask_wtf import FlaskForm

from .. import settings
from ..db.models import PROBE_PROTOCOLS, LOG_PROBE_PROTOCOLS, MONITOR_TYPES
from . import validators as ampt_validators
from ..db.database import get_generator_choices


__all__ = ['LoginForm', 'MonitoredSegmentCreateModifyForm',
           'EventMonitorCreateModifyForm', 'ProbeGeneratorCreateModifyForm',
           'AMPTObjectDeleteForm', 'ReceivedProbeLogForm']

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[validators.InputRequired()])
    password = PasswordField('Password', validators=[validators.InputRequired()])

class MonitoredSegmentCreateModifyForm(FlaskForm):
    name = StringField('Segment Name', [validators.InputRequired()], description='Name of monitored segment', render_kw={'autofocus': 'autofocus'})
    description = StringField('Description', [validators.InputRequired()], description='Description of monitored segment', render_kw={'size': 45})
    dest_addr = StringField('Destination Address', [validators.InputRequired(), validators.IPAddress()], description='Destination IP address for target of probe packet', render_kw={'size': 15})
    dest_port = IntegerField('Destination Port', [validators.InputRequired(), validators.NumberRange(0, 65535)], description='Destination port for target of probe packet', render_kw={'size': 5})
    protocol = SelectField('Protocol', [validators.InputRequired()], choices=PROBE_PROTOCOLS, description='IP protocol for probe packet')
    generator = SelectField('Probe Generator', [validators.InputRequired(), validators.NumberRange(1)], choices=get_generator_choices(), description='Generator from which to emit probe packet')
    active = BooleanField('Enable Segment', default=True)

class EventMonitorCreateModifyForm(FlaskForm):
    hostname = StringField('Hostname', [validators.InputRequired()], description='Hostname of event monitor node', render_kw={'autofocus': 'autofocus'})
    description = StringField('Description', [validators.InputRequired()], description='Description of event monitor system', render_kw={'size': 45})
    type = SelectField('Monitor Type', [validators.required()], choices=MONITOR_TYPES, description='Type of Monitor')
    auth_key = StringField('Auth Key', [validators.InputRequired()], description='Authentication key for monitor node', render_kw={'size': 35})
    active = BooleanField('Enable Monitor', default=True)

class ProbeGeneratorCreateModifyForm(FlaskForm):
    name = StringField('Name', [validators.InputRequired()], description='Name of probe generator', render_kw={'autofocus': 'autofocus'})
    address = StringField('Address', [validators.InputRequired()], description='Address (hostname or IP) of generator node', render_kw={'size': 35})
    port = IntegerField('Port', [validators.InputRequired(), validators.NumberRange(0, 65535)], default=settings.probe_generator_default_port, description='Listener port for probe generator', render_kw={'size': 5})
    auth_key = StringField('Auth Key', [validators.InputRequired()], description='Authentication key for generator node', render_kw={'size': 35})
    active = BooleanField('Enable Generator', default=True)

class AMPTObjectDeleteForm(FlaskForm):
    submitted = SubmitField('Delete Me')

class ReceivedProbeLogForm(FlaskForm):
    # Form functions as a data submission endpoint so no CSRF needed
    class Meta:
        csrf = False

    monitor = IntegerField('Event Monitor', [validators.InputRequired(), validators.NumberRange(1)], description='Monitor which delivered probe event')
    src_addr = StringField('Source IP', [validators.InputRequired(), validators.IPAddress()], description='Source IP in observed probe packet')
    dest_addr = StringField('Destination IP', [validators.InputRequired(), validators.IPAddress()], description='Destination IP in observed probe packet')
    src_port = IntegerField('Source Port', [validators.InputRequired(), validators.NumberRange(0, 65535)], description='Source port in observed probe packet')
    dest_port = IntegerField('Destination Port', [validators.InputRequired(), validators.NumberRange(0, 65535)], description='Destination port in observed probe packet')
    protocol = SelectField('Protocol', [validators.InputRequired()], choices=LOG_PROBE_PROTOCOLS, description='IP protocol in observed probe packet')
    alert_time = DateTimeField('Alert Time', [validators.InputRequired()], format='%Y-%m-%dT%H:%M:%S', description='Timestamp of probe alert on remote sensor')
    hostname = StringField('Monitor Hostname', [validators.InputRequired()], description='Hostname of remote AMPT monitor')
    plugin_name = StringField('Monitor Plugin Name', [validators.InputRequired()], description='Name of plugin handling event on remote AMPT monitor')
    h = StringField('HMAC Digest', [validators.InputRequired(), ampt_validators.VerifiedHMAC(exclude_fields=['h'])], description='HMAC digest of received log message')
    ts = StringField('Timestamp Counter', [validators.InputRequired(), ampt_validators.VerifiedCounter()], description='Timestamp counter for received log message')

