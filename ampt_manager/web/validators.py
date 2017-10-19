'''
AMPT Manager form custom validators

'''
import os
import copy
import hmac
import json
import os.path
from shutil import chown
from datetime import date, datetime

from wtforms.validators import ValidationError

from . import app
from .. import settings
from ..db.models import EventMonitor


class VerifiedHMAC():
    '''Verify the HMAC on AMPT Monitor event log messages.

    Validation is performed as follows:

    Requests are handled as messages and are required to carry an HMAC
    digest allowing the server to verify the message and validate that
    client is a trusted AMPT monitor node using the same shared secret.
    The parameters in the submitted request are serialized to a JSON structure
    and the computed HMAC of this data is compared to the HMAC accompanying
    the client's request.

    :param exclude_fields:
        A list of field names on the form to exclude from HMAC verification.
        Typically the HMAC digest field itself must be excluded.
    :param message:
        Error message to raise in case of a validation error. If not provided,
        a default message is used.

    '''
    def __init__(self, exclude_fields=[], message=None):
        self.exclude_fields = exclude_fields
        self.message = message

    def __call__(self, form, field):
        req_digest = field.data
        monitor_id = int(form['monitor'].data)
        hmac_hash = app.config['HMAC_DIGEST']

        monitor_auth_key = EventMonitor.get(EventMonitor.id == monitor_id).auth_key

        if self.message is None:
            self.message = 'HMAC digest failed verification'

        # Construct message from form data and compute digest.
        # Copy and adjust form dict to serialize to JSON.
        _form_data = copy.deepcopy(form.data)
        for f in self.exclude_fields:
            if f in _form_data:
                del _form_data[f]
            else:
                app.logger.warning('field name %s specified in exclude_fields '
                                   'not present in form data', f)
        j = json.dumps(_form_data, default=json_serial, sort_keys=True)

        computed_digest = (hmac.new(bytes(monitor_auth_key.encode('utf-8')),
                                    j.encode('utf-8'), hmac_hash)
                                    .hexdigest())

        # Fail out if HMAC comparison unsuccessful
        if not hmac.compare_digest(req_digest, computed_digest):
            raise ValidationError(self.message)
        app.logger.debug('received event log HMAC verified successfully')

class VerifiedCounter():
    '''Verify the replay counter on AMPT Monitor event log messages.

    Verification is performed as follows:

    Request messages contain the core packet dispatch parameters as well as
    a per-request counter in the form of a timestamp, included to allow for
    a basic level of replay protection. After a request is validated, the
    counter (a decimal timestamp value) is stored in the counter
    database. Future requests ensure that the counter in the validated
    message is greater than the stored counter from the previous message.

    :param message:
        Error message to raise in case of a validation error. If not provided,
        a default message will be used.

    '''
    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        'Validate timestamp counter on request'

        req_ts = field.data

        if self.message is None:
            self.message = 'Replay counter comparison failed verification'

        # Compare stored counter to request counter. The counter is valid if it is
        # greater than the previously stored one.
        with open(app.config['COUNTER_PATH'], 'r') as f:
            if not float(req_ts) > float(f.read()):
                raise ValidationError(self.message)
            app.logger.debug('received event log replay counter verified '
                             'successfully')

def persist_counter(db_path, ctr=settings.counter_db_init_val):
    '''Store value into counter file.

    :param ctr:
        Counter value to write to file. This value should increase with every
        request, so a numeric timestamp is used. May be omitted to write an
        initialization value to the file (typically 0).

    '''
    with open(db_path, 'w') as f:
        f.write(str(ctr))
        if ctr == settings.counter_db_init_val:
            app.logger.debug('initialized counter database with base '
                             'value of %d', settings.counter_db_init_val)

def json_serial(obj):
    '''JSON serializer for objects not serializable by default.

    Used to ensure that coerced datetime objects from form serialize without
    issue.

    '''
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

