# -*- coding: utf-8 -*-
import pytz

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    state = fields.Selection(selection_add=[('cancel', 'Canceled')])
    appointment_id = fields.Many2one('calendar.appointment', 'Appointment', ondelete='cascade')
    type = fields.Selection([
        ('audience', 'Audience'),
        ('conference', 'Video conference'),
        ('streaming', 'Streaming')], 'Request type', default='audience')
    applicant_id = fields.Many2one('res.partner', 'Applicant', ondelete='set null')
    declarant_id = fields.Many2one('res.partner', 'Declarant', ondelete='set null')
    declarant_text = fields.Text('Declarant input')
    indicted_id = fields.Many2one('res.partner', 'Indicted', ondelete='set null')
    indicted_text = fields.Text('Indicted input')
    destination_id = fields.Many2one('res.partner', 'Destination', ondelete='set null')
    class_id = fields.Many2one('calendar.class', 'Calendar class', ondelete='set null')
    help_support = fields.Many2one('calendar.help', 'Calendar help', ondelete='set null', domain="[('type','=','support')]")  # Ayuda
    help_type_p = fields.Many2one('calendar.help', 'Calendar help', ondelete='set null', domain="[('type','=','type_p')]")
    help_type_c = fields.Many2one('calendar.help', 'Calendar help', ondelete='set null', domain="[('type','=','type_c')]")
    request_type = fields.Selection([('l', 'Free'), ('r', 'Reserved')], 'Request type', default='r')
    process_number = fields.Char('Process number')
    reception_id = fields.Many2one('calendar.reception', 'Reception medium', ondelete='set null')

    @api.model
    def create(self, vals):
        vals.update(self.create_appointment(vals))
        vals.pop('types', None)
        vals.pop('room_id', None)
        res = super(CalendarEvent, self).create(vals)
        res.appointment_id.write({'event_id': res.id})
        return res

    def write(self, vals):
        self.cancel_calendar_event(vals)
        # self.write_appointment(vals)
        # vals.pop('cw_bool', None)
        return super(CalendarEvent, self).write(vals)

    def unlink(self):
        # vals = {'state': 'cancel'}
        # self.cancel_calendar_event(vals)
        return super(CalendarEvent, self).unlink()

    def create_appointment(self, vals):
        dic = {}
        # appointment_type = self.env['calendar.appointment.type'].sudo().browse(vals.get('appointment_type_id'))
        # room_id = appointment_type.judged_id.rooms_id[0].id if appointment_type.judged_id.rooms_id else False
        if vals.get('types'):
            if vals.get('types')[0] == 'V':
                types = 'conference'
            elif vals.get('types')[0] == 'A':
                types = 'audience'
            else:
                types = 'streaming'
        else:
            types = False
        appointment = self.env['calendar.appointment'].sudo().create({
            'state': vals.get('state'),
            'calendar_datetime': vals.get('start_datetime'),
            'calendar_duration': vals.get('duration'),
            'observations': vals.get('description'),
            'partners_ids': vals.get('partner_ids'),
            'appointment_type_id': vals.get('appointment_type_id'),
            'class_id' : vals.get('class_id'),
            'help_support': vals.get('help_support'),
            'help_type_p': vals.get('help_type_p'),
            'help_type_c': vals.get('help_type_c'),
            'reception_id' : vals.get('reception_id'),
            'indicted_text' : vals.get('indicted_text'),
            'declarant_text' : vals.get('declarant_text'),
            'applicant_id' : vals.get('applicant_id'),
            'process_number' : vals.get('process_number'),
            'room_id': vals.get('room_id'),
            'type': types,
            'request_type' : vals.get('request_type'),
        })
        dic.update(appointment_id=appointment.id)
        return dic

    def write_appointment(self, vals):
        flag = vals.get('cw_bool') or False
        if vals.get('start_datetime') and not flag:
            for record in self:
                if record.appointment_id:
                    dic = {
                        'calendar_datetime': vals.get('start_datetime'),
                        'cw_bool': True,
                    }
                    record.appointment_id.write(dic)
            record.appointment_id.write(dic)

    def cancel_calendar_event(self, vals):
        if vals.get('state') and vals.get('state') == 'cancel':
            for record in self:
                attendee_to_email = record.attendee_ids
                if attendee_to_email:
                    attendee_to_email._send_mail_to_attendees('calendar_csj.calendar_csj_template_meeting_cancel')

    # def _get_ics_file(self):
    #     """ Returns iCalendar file for the event invitation.
    #         :returns a dict of .ics file content for each meeting
    #     """
    #     result = {}

    #     def ics_datetime(idate, allday=False):
    #         if idate:
    #             if allday:
    #                 return idate
    #             else:
    #                 return idate.replace(tzinfo=pytz.timezone('UTC'))
    #         return False

    #     try:
    #         # FIXME: why isn't this in CalDAV?
    #         import vobject
    #     except ImportError:
    #         _logger.warning("The `vobject` Python module is not installed, so iCal file generation is unavailable. Please install the `vobject` Python module")
    #         return result

    #     for meeting in self:
    #         cal = vobject.iCalendar()
    #         event = cal.add('vevent')

    #         if not meeting.start or not meeting.stop:
    #             raise UserError(_("First you have to specify the date of the invitation."))
    #         event.add('created').value = ics_datetime(fields.Datetime.now())
    #         event.add('dtstart').value = ics_datetime(meeting.start, meeting.allday)
    #         event.add('dtend').value = ics_datetime(meeting.stop, meeting.allday)
    #         event.add('summary').value = meeting.name
    #         if meeting.description:
    #             event.add('description').value = meeting.description
    #         if meeting.location:
    #             event.add('location').value = meeting.location
    #         if meeting.rrule:
    #             event.add('rrule').value = meeting.rrule

    #         if meeting.alarm_ids:
    #             for alarm in meeting.alarm_ids:
    #                 valarm = event.add('valarm')
    #                 interval = alarm.interval
    #                 duration = alarm.duration
    #                 trigger = valarm.add('TRIGGER')
    #                 trigger.params['related'] = ["START"]
    #                 if interval == 'days':
    #                     delta = timedelta(days=duration)
    #                 elif interval == 'hours':
    #                     delta = timedelta(hours=duration)
    #                 elif interval == 'minutes':
    #                     delta = timedelta(minutes=duration)
    #                 trigger.value = delta
    #                 valarm.add('DESCRIPTION').value = alarm.name or u'Odoo'
    #         for attendee in meeting.attendee_ids:
    #             attendee_add = event.add('attendee')
    #             attendee_add.value = u'MAILTO:' + (attendee.email or u'')
    #         result[meeting.id] = cal.serialize().encode('utf-8')

    #     return result