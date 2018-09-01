'''
AMPT Manager application views

'''

import datetime

from peewee import fn, JOIN, IntegrityError
from playhouse.flask_utils import get_object_or_404, object_list
from flask import render_template, request, url_for, redirect, flash
from flask import abort, jsonify
from flask.views import View
from flask_login import login_required, login_user, logout_user
from flask_login import current_user
from flask_classy import FlaskView, route

from . import app
from .. import __version__ as ampt_mgr_version
from .forms import *
from .. import settings
from ..db.models import *
from .crypt import bcrypt
from .validators import persist_counter
from ..exceptions import InvalidUsage


class GeneratorView(FlaskView):
    decorators = [login_required]
    def index(self):
        objects = ProbeGenerator.select().order_by(ProbeGenerator.name)
        return render_template('probegenerator_list.html', objects=objects)

    def get(self, id):
        id = int(id)
        object = get_object_or_404(ProbeGenerator, ProbeGenerator.id==id)
        return render_template('probegenerator_detail.html', object=object)

    @route('/create/', methods=['GET', 'POST'])
    def create(self):
        form = ProbeGeneratorCreateModifyForm()
        if form.validate_on_submit():
            generator = ProbeGenerator()
            form.populate_obj(generator)
            generator.created_date = generator.modified_date = datetime.datetime.utcnow()
            generator.created_by = generator.last_modified_by = current_user.id
            try:
                generator.save()
                msg = 'Added probe generator "{name}"'
                flash(msg.format(name=generator.name), 'success')
                logmsg = 'ProbeGenerator {generator} (ID: {generator_id}) added by user {user}'
                app.logger.info(logmsg.format(generator=generator.name,
                                              generator_id=generator.id,
                                              user=current_user.username))
            except IntegrityError as e:
                msg = 'Error adding probe generator: {err}'
                flash(msg.format(err=e), 'danger')
                return render_template('probegenerator_create_modify.html',
                                       form=form,
                                       form_action='Add')
            return redirect(url_for('GeneratorView:index'))
        return render_template('probegenerator_create_modify.html',
                               form=form,
                               form_action='Add')

    @route('/edit/<int:id>', methods=['GET', 'POST'])
    def edit(self, id):
        generator = get_object_or_404(ProbeGenerator, ProbeGenerator.id==id)
        form = ProbeGeneratorCreateModifyForm(obj=generator)
        if form.validate_on_submit():
            form.populate_obj(generator)
            generator.modified_date = datetime.datetime.utcnow()
            generator.last_modified_by = current_user.id
            generator.save()
            msg = 'Updated probe generator "{name}"'
            flash(msg.format(name=generator.name), 'success')
            logmsg = 'ProbeGenerator {generator} (ID: {generator_id}) modified by user {user}'
            app.logger.info(logmsg.format(generator=generator.name,
                                          generator_id=generator.id,
                                          addr=generator.address,
                                          port=generator.port,
                                          user=current_user.username))
            return redirect(url_for('GeneratorView:get', id=id))
        return render_template('probegenerator_create_modify.html',
                               form=form,
                               form_action='Update')

    @route('/delete/<int:id>', methods=['GET', 'POST'])
    def delete(self, id):
        generator = get_object_or_404(ProbeGenerator, ProbeGenerator.id==id)
        form = AMPTObjectDeleteForm()
        if form.validate_on_submit():
            generator.delete_instance()
            msg = 'Deleted probe generator "{name}"'
            flash(msg.format(name=generator.name), 'success')
            logmsg = 'ProbeGenerator {generator} (ID: {generator_id}) deleted by user {user}'
            app.logger.info(logmsg.format(generator=generator.name,
                                          generator_id=generator.id,
                                          user=current_user.username))
            return redirect(url_for('GeneratorView:index'))
        return render_template('probegenerator_delete.html',
                               form=form,
                               generator=generator)


class SegmentView(FlaskView):
    decorators = [login_required]

    def index(self):
        objects = MonitoredSegment.select().order_by(MonitoredSegment.name)
        return render_template('monitoredsegment_list.html', objects=objects)

    def get(self, id):
        id = int(id)
        object = get_object_or_404(MonitoredSegment, MonitoredSegment.id==id)
        return render_template('monitoredsegment_detail.html', object=object)

    @route('/create/', methods=['GET', 'POST'])
    def create(self):
        form = MonitoredSegmentCreateModifyForm()
        # XXX bug
	# For some reason data from form submission sets the generator and dest_port
	# fields to a str type instead of int and leads to these types of exceptions
	# in form.validate_on_submit():
        #   TypeError: unorderable types: str() < int()
        #   TypeError: '<' not supported between instances of 'str' and 'int'
	# So we make them an int explicitly:
        if request.method == 'POST':
            form.generator.data = int(form.generator.data)
            form.dest_port.data = int(form.dest_port.data)
        if form.validate_on_submit():
            segment = MonitoredSegment()
            form.populate_obj(segment)
            segment.created_date = segment.modified_date = datetime.datetime.utcnow()
            segment.created_by = segment.last_modified_by = current_user.id
            try:
                segment.save()
                msg = 'Added segment "{segment}"'
                flash(msg.format(segment=segment.name), 'success')
                logmsg = 'MonitoredSegment {segment} (ID: {segment_id}) added by user {user}'
                app.logger.info(logmsg.format(segment=segment.name,
                                              segment_id=segment.id,
                                              user=current_user.username))
            except IntegrityError as e:
                msg = 'Error adding segment: {err}'
                flash(msg.format(err=e), 'danger')
                return render_template('monitoredsegment_create_modify.html',
                                       form=form,
                                       form_action='Add')
            return redirect(url_for('SegmentView:index'))
        return render_template('monitoredsegment_create_modify.html',
                               form=form,
                               form_action='Add')

    @route('/edit/<int:id>', methods=['GET', 'POST'])
    def edit(self, id):
        segment = get_object_or_404(MonitoredSegment, MonitoredSegment.id==id)
        form = MonitoredSegmentCreateModifyForm(obj=segment)
        # XXX bug
	# For some reason data from form submission sets the generator and dest_port
	# fields to a str type instead of int and leads to this exception
	# in form.validate_on_submit():
        #   TypeError: '<' not supported between instances of 'str' and 'int'
	# So we make them ints explicitly:
        if request.method == 'POST':
            form.generator.data = int(form.generator.data)
            form.dest_port.data = int(form.dest_port.data)
        if form.validate_on_submit():
            form.populate_obj(segment)
            segment.modified_date = datetime.datetime.utcnow()
            segment.last_modified_by = current_user.id
            segment.save()
            msg = 'Updated monitored segment "{name}"'
            flash(msg.format(name=segment.name), 'success')
            logmsg = 'MonitoredSegment {segment} (ID: {segment_id}) modified by user {user}'
            app.logger.info(logmsg.format(segment=segment.name,
                                          segment_id=segment.id,
                                          user=current_user.username))
            return redirect(url_for('SegmentView:get', id=id))
        return render_template('monitoredsegment_create_modify.html',
                               form=form,
                               form_action='Update')

    @route('/delete/<int:id>', methods=['GET', 'POST'])
    def delete(self, id):
        segment = get_object_or_404(MonitoredSegment, MonitoredSegment.id==id)
        form = AMPTObjectDeleteForm()
        if form.validate_on_submit():
            segment.delete_instance()
            msg = 'Deleted monitored segment "{name}"'
            flash(msg.format(name=segment.name), 'success')
            logmsg = 'MonitoredSegment {segment} (ID: {segment_id}) deleted by user {user}'
            app.logger.info(logmsg.format(segment=segment.name,
                                          segment_id=segment.id,
                                          user=current_user.username))
            return redirect(url_for('SegmentView:index'))
        return render_template('monitoredsegment_delete.html',
                               form=form,
                               segment=segment)


class MonitorView(FlaskView):
    decorators = [login_required]

    def index(self):
        objects = EventMonitor.select().order_by(EventMonitor.hostname,
                                                 EventMonitor.id)
        return render_template('eventmonitor_list.html', objects=objects)

    def get(self, id):
        id = int(id)
        object = get_object_or_404(EventMonitor, EventMonitor.id==id)
        return render_template('eventmonitor_detail.html', object=object)

    @route('/create/', methods=['GET', 'POST'])
    def create(self):
        form = EventMonitorCreateModifyForm()
        if form.validate_on_submit():
            monitor = EventMonitor()
            form.populate_obj(monitor)
            monitor.created_date = monitor.modified_date = datetime.datetime.utcnow()
            monitor.created_by = monitor.last_modified_by = current_user.id
            try:
                monitor.save()
                msg = 'Added event monitor "{monitor}" ({type})'
                flash(msg.format(monitor=monitor.hostname, type=monitor.type), 'success')
                logmsg = 'EventMonitor {monitor} (ID: {monitor_id}) added by user {user}'
                app.logger.info(logmsg.format(monitor=monitor.hostname,
                                              monitor_id=monitor.id,
                                              user=current_user.username))
            except IntegrityError as e:
                msg = 'Error adding event monitor: {err}'
                flash(msg.format(err=e), 'danger')
                return render_template('eventmonitor_create_modify.html',
                                       form=form, form_action='Add')
            return redirect(url_for('MonitorView:index'))
        return render_template('eventmonitor_create_modify.html',
                               form=form,
                               form_action='Add')

    @route('/edit/<int:id>', methods=['GET', 'POST'])
    def edit(self, id):
        monitor = get_object_or_404(EventMonitor, EventMonitor.id==id)
        form = EventMonitorCreateModifyForm(obj=monitor)
        if form.validate_on_submit():
            form.populate_obj(monitor)
            monitor.modified_date = datetime.datetime.utcnow()
            monitor.last_modified_by = current_user.id
            monitor.save()
            msg = 'Updated event monitor "{name}"'
            flash(msg.format(name=monitor.hostname), 'success')
            logmsg = 'EventMonitor {monitor} (ID: {monitor_id}) modified by user {user}'
            app.logger.info(logmsg.format(monitor=monitor.hostname,
                                          monitor_id=monitor.id,
                                          user=current_user.username))
            return redirect(url_for('MonitorView:get', id=id))
        return render_template('eventmonitor_create_modify.html',
                               form=form,
                               form_action='Update')

    @route('/delete/<int:id>', methods=['GET', 'POST'])
    def delete(self, id):
        monitor = get_object_or_404(EventMonitor, EventMonitor.id==id)
        form = AMPTObjectDeleteForm()
        if form.validate_on_submit():
            monitor.delete_instance()
            msg = 'Deleted event monitor "{name}"'
            flash(msg.format(name=monitor.hostname), 'success')
            logmsg = 'EventMonitor {monitor} (ID: {monitor_id}) deleted by user {user}'
            app.logger.info(logmsg.format(monitor=monitor.hostname,
                                          monitor_id=monitor.id,
                                          user=current_user.username))
            return redirect(url_for('MonitorView:index'))
        return render_template('eventmonitor_delete.html',
                               form=form,
                               monitor=monitor)


class GeneratedLogView(FlaskView):
    route_prefix = '/log/'
    decorators = [login_required]

    def index(self):
        objects = GeneratedProbeLog.select().order_by(
                  GeneratedProbeLog.send_time.desc())
        total_objects = objects.count()
        # flask_utils' object_list raises 404 if the queryset has 0 records,
        # so short circuit pagination
        if not total_objects:
            return render_template('generatedprobelog_list.html',
                                   objects=objects,
                                   total_objects=total_objects)
        return object_list('generatedprobelog_list.html',
                           query=objects,
                           context_variable='objects',
                           paginate_by=settings.PAGINATION_CNT_LOGS,
                           total_objects=total_objects)


class ReceivedLogView(FlaskView):
    route_prefix = '/log/'

    @login_required
    def index(self):
        objects = ReceivedProbeLog.select().order_by(
                  ReceivedProbeLog.recv_time.desc())
        total_objects = objects.count()
        # flask_utils' object_list raises 404 if the queryset has 0 records,
        # so short circuit pagination
        if not total_objects:
            return render_template('receivedprobelog_list.html',
                                   objects=objects,
                                   total_objects=total_objects)
        return object_list('receivedprobelog_list.html',
                           query=objects,
                           context_variable='objects',
                           paginate_by=settings.PAGINATION_CNT_LOGS,
                           total_objects=total_objects)

    def post(self):
        '''
        Receive and create event logs from event monitors.

        Submission requires a form POST containing the 5-tuple of protocol
        header data for the model as well as the integer ID of the remote
        event monitor.

        This view does not require a login session to access (handled in
        respective form class).

        '''
        app.logger.debug('new inbound probe log submission request')
        form = ReceivedProbeLogForm()
        if form.validate_on_submit():
            # Submitted data passed validation, update counter file
            persist_counter(app.config['COUNTER_PATH'], ctr=form.ts.data)

            # Match the monitor ID to a configured Event Monitor instance
            try:
                matched_monitor = EventMonitor.get(
                    EventMonitor.id == int(form.monitor.data))
            except EventMonitor.DoesNotExist:
                logmsg = ('rejected probe log received from {host} [{ip}] '
                          'with unknown monitor ID {id}')
                app.logger.warning(logmsg.format(host=form.hostname.data,
                                                 ip=request.remote_addr,
                                                 id=form.monitor.data))
                errmsg = 'rejected probe log from unknown monitor ID {id}'
                raise InvalidUsage(errmsg.format(id=form.monitor.data))
            # Match the destination IP and port to a configured Monitored
            # Segment instance
            try:
                matched_segment = MonitoredSegment.get(
                    MonitoredSegment.dest_addr == form.dest_addr.data,
                    MonitoredSegment.dest_port == form.dest_port.data)
            except MonitoredSegment.DoesNotExist:
                logmsg = ('rejected probe log from {host} [{ip}] with unknown '
                          'monitored segment parameters (dest_addr={dest_addr} '
                          'and dest_port={dest_port})')
                logmsg = logmsg.format(dest_addr=form.dest_addr.data,
                                       dest_port=form.dest_port.data,
                                       ip=request.remote_addr,
                                       host=form.hostname.data)
                app.logger.warn(logmsg)
                errmsg = ('rejected probe log with unknown monitored segment '
                          'destination {dest_addr}:{dest_port}')
                errmsg = errmsg.format(dest_addr=form.dest_addr.data,
                                       dest_port=form.dest_port.data)
                raise InvalidUsage(errmsg)

            eventlog = ReceivedProbeLog()
            form.populate_obj(eventlog)
            eventlog.monitor = matched_monitor
            eventlog.segment = matched_segment

            # Store new received event log instance
            try:
                eventlog.save()
                logmsg = 'probe log event accepted from {plugin} on {host} [{ip}] {monitor}'
                app.logger.info(logmsg.format(host=form.hostname.data,
                                              ip=request.remote_addr,
                                              monitor=matched_monitor,
                                              plugin=form.plugin_name.data))
                response_msg = 'accepted event log (id={id})'.format(id=eventlog.id)
                return jsonify({
                    'message': response_msg,
                })
            except Exception as e:
                # Log exception but let response fall through to end of view
                # without exception details
                logmsg = ('failed to record probe log event from {host} [{ip}] '
                          '{monitor} due to error: {err}')
                app.logger.error(logmsg.format(host=form.hostname.data,
                                               ip=request.remote_addr,
                                               monitor=matched_monitor,
                                               err=e))
        else:
            # Submitted form did not validate
            errmsg = ('errors occurred in validating submission '
                      'from {host} [{ip}]: {errors}')
            errmsg = errmsg.format(host=form.hostname.data,
                                   ip=request.remote_addr,
                                   errors=form.errors)
            app.logger.warning(errmsg)
            raise InvalidUsage(errmsg)

        raise InvalidUsage('Error processing probe log submission',
                           status_code=500)

GeneratorView.register(app)
SegmentView.register(app)
MonitorView.register(app)
GeneratedLogView.register(app)
ReceivedLogView.register(app)


@app.route('/')
@login_required
def index():
    # Segments for which we have not yet received probe events from
    # monitors will have None set for the 'latest_log_time' annotated field
    # due to the join. See Jinja template for specifics.
    # Update 2018-08-21: .annotate() dropped in 3.x, query restructured
    monitored_segments = (MonitoredSegment
                          .select(MonitoredSegment,
                                  fn.MAX(ReceivedProbeLog.recv_time)
                                  .alias('latest_log_time'))
                          .join(ReceivedProbeLog, JOIN.LEFT_OUTER)
                          .group_by(MonitoredSegment)
                          .order_by(MonitoredSegment.name))
    # Apply configured limit on number of monitored segments rendered on
    # index page. By default no limit is imposed to allow the user to see
    # information about all segments. As the number of configured segments
    # increases, it may be desirable to limit the number of segments, which
    # can be done in the configuration file.
    segment_limit = app.config.get('SEGMENT_LIMIT_INDEX')
    if segment_limit is not None:
        segment_limit = int(segment_limit)
        if segment_limit > 0:
            monitored_segments = monitored_segments.limit(segment_limit)
    total_monitored_segments = MonitoredSegment.select().count()

    probe_generators = (ProbeGenerator
                        .select()
                        .order_by(ProbeGenerator.name)
                        .limit(5))
    total_probe_generators = ProbeGenerator.select().count()

    event_monitors = (EventMonitor
                      .select()
                      .order_by(EventMonitor.hostname)
                      .limit(5))
    total_event_monitors = EventMonitor.select().count()

    received_logs = (ReceivedProbeLog
                     .select()
                     .order_by(ReceivedProbeLog.recv_time.desc())
                     .limit(5))
    total_received_logs = ReceivedProbeLog.select().count()

    return render_template('index_page.html',
                           received_logs=received_logs,
                           total_received_logs=total_received_logs,
                           monitored_segments=monitored_segments,
                           total_monitored_segments=total_monitored_segments,
                           probe_generators=probe_generators,
                           total_probe_generators=total_probe_generators,
                           event_monitors=event_monitors,
                           total_event_monitors=total_event_monitors,
                           ampt_mgr_version=ampt_mgr_version,
                          )

@app.route('/login/', methods=['GET', 'POST'])
def login():
    '''
    Authenticate the user.

    Authenticate the user logging in and log authentication-related events:
      - user logged in
      - user failed to authenticate (password verification failure)
      - invalid/unknown user attempted login

    '''
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.select().where(User.username == form.username.data).first()
        if user:
            if user.check_password(form.password.data):
                user.authenticated = True
                login_user(user, remember=True)
                msg = 'user {username} successfully authenticated from {ip}'
                app.logger.info(msg.format(username=current_user.username,
                                           ip=request.remote_addr))

                next = request.args.get('next')
                return redirect(next or url_for('index'))
            else:
                flash('Failed to authenticate: bad username or password', 'danger')
                msg = 'user {username} failed authentication from {ip}'
                app.logger.warning(msg.format(username=user.username,
                                              ip=request.remote_addr))
        else:
            flash('Failed to authenticate: bad username or password', 'danger')
            msg = 'invalid user {username} attempted authentication from {ip}'
            app.logger.warning(msg.format(username=form.username.data,
                                          ip=request.remote_addr))
    return render_template('login.html', form=form)

@app.route('/logout/')
@login_required
def logout():
    'Log out the logged in user'

    username = current_user.username
    logout_user()
    msg = 'user {username} logged out from {ip}'
    app.logger.info(msg.format(username=username,
                               ip=request.remote_addr))
    return redirect(url_for('index'))

@app.route('/about/')
@login_required
def show_about():
    'Render about template'
    return render_template('about.html')

