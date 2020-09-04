'''
Forms for AMPT Manager

'''
from flask_wtf import FlaskForm
from wtforms import (Form, BooleanField, StringField, IntegerField,
                     PasswordField, DecimalField)
from wtforms import SelectField, SubmitField, DateTimeField
from wtforms.validators import (InputRequired, IPAddress, NumberRange, required)

from .. import settings
from ..db.models import PROBE_PROTOCOLS, LOG_PROBE_PROTOCOLS, MONITOR_TYPES
from .validators import VerifiedHMAC, VerifiedCounter


__all__ = ['LoginForm', 'MonitoredSegmentCreateModifyForm',
           'EventMonitorCreateModifyForm', 'ProbeGeneratorCreateModifyForm',
           'AMPTObjectDeleteForm', 'ReceivedProbeLogForm']


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password',
                             validators=[InputRequired()])


class MonitoredSegmentCreateModifyForm(FlaskForm):
    name = StringField(
        'Segment Name',
        [InputRequired()],
        description='Name of monitored segment',
        render_kw={'autofocus': 'autofocus'})
    description = StringField(
        'Description',
        [InputRequired()],
        description='Description of monitored segment',
        render_kw={'size': 45})
    dest_addr = StringField(
        'Destination Address',
        [InputRequired(), IPAddress()],
        description='Destination IP address for target of probe packet',
        render_kw={'size': 15})
    dest_port = IntegerField(
        'Destination Port',
        [InputRequired(), NumberRange(0, 65535)],
        description='Destination port for target of probe packet',
        render_kw={'size': 5})
    protocol = SelectField(
        'Protocol',
        [InputRequired()],
        choices=PROBE_PROTOCOLS,
        description='IP protocol for probe packet')
    # Uses a `choices` keyword, but this is set in the view handler.
    # https://wtforms.readthedocs.io/en/2.3.x/fields/#wtforms.fields.SelectField
    generator = SelectField(
        'Probe Generator',
        [InputRequired(), NumberRange(1)],
        description='Generator from which to emit probe packet',
        coerce=int)
    active = BooleanField(
        'Enable Segment',
        default=True)


class EventMonitorCreateModifyForm(FlaskForm):
    hostname = StringField(
        'Hostname',
        [InputRequired()],
        description='Hostname of event monitor node',
        render_kw={'autofocus': 'autofocus'})
    description = StringField(
        'Description',
        [InputRequired()],
        description='Description of event monitor system',
        render_kw={'size': 45})
    type = SelectField(
        'Monitor Type',
        [required()],
        choices=MONITOR_TYPES,
        description='Type of Monitor')
    auth_key = StringField(
        'Auth Key',
        [InputRequired()],
        description='Authentication key for monitor node',
        render_kw={'size': 35})
    active = BooleanField(
        'Enable Monitor',
        default=True)


class ProbeGeneratorCreateModifyForm(FlaskForm):
    name = StringField(
        'Name',
        [InputRequired()],
        description='Name of probe generator',
        render_kw={'autofocus': 'autofocus'})
    address = StringField(
        'Address',
        [InputRequired()],
        description='Address (hostname or IP) of generator node',
        render_kw={'size': 35})
    port = IntegerField(
        'Port',
        [InputRequired(), NumberRange(0, 65535)],
        default=settings.probe_generator_default_port,
        description='Listener port for probe generator',
        render_kw={'size': 5})
    auth_key = StringField(
        'Auth Key',
        [InputRequired()],
        description='Authentication key for generator node',
        render_kw={'size': 35})
    active = BooleanField(
        'Enable Generator',
        default=True)


class AMPTObjectDeleteForm(FlaskForm):
    submitted = SubmitField('Delete Me')


class ReceivedProbeLogForm(FlaskForm):
    # Form functions as a data submission endpoint so no CSRF needed
    class Meta:
        csrf = False

    monitor = IntegerField(
        'Event Monitor',
        [InputRequired(), NumberRange(1)],
        description='Monitor which delivered probe event')
    src_addr = StringField(
        'Source IP',
        [InputRequired(), IPAddress()],
        description='Source IP in observed probe packet')
    dest_addr = StringField(
        'Destination IP',
        [InputRequired(), IPAddress()],
        description='Destination IP in observed probe packet')
    src_port = IntegerField(
        'Source Port',
        [InputRequired(), NumberRange(0, 65535)],
        description='Source port in observed probe packet')
    dest_port = IntegerField(
        'Destination Port',
        [InputRequired(), NumberRange(0, 65535)],
        description='Destination port in observed probe packet')
    protocol = SelectField(
        'Protocol',
        [InputRequired()],
        choices=LOG_PROBE_PROTOCOLS,
        description='IP protocol in observed probe packet')
    alert_time = DateTimeField(
        'Alert Time',
        [InputRequired()],
        format='%Y-%m-%dT%H:%M:%S',
        description='Timestamp of probe alert on remote sensor')
    hostname = StringField(
        'Monitor Hostname',
        [InputRequired()],
        description='Hostname of remote AMPT monitor')
    plugin_name = StringField(
        'Monitor Plugin Name',
        [InputRequired()],
        description='Name of plugin handling event on remote AMPT monitor')
    h = StringField(
        'HMAC Digest',
        [InputRequired(), VerifiedHMAC(exclude_fields=['h'])],
        description='HMAC digest of received log message')
    ts = StringField(
        'Timestamp Counter',
        [InputRequired(), VerifiedCounter()],
        description='Timestamp counter for received log message')


