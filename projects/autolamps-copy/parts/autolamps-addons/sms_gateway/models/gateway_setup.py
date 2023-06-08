import datetime
import json
from openerp import _, api, fields, models, tools, exceptions
# from openerp.exceptions import except_orm, UserError, Warning
import requests
import urllib
import re
import logging

_logger = logging.getLogger(__name__)


class GateWaySetup(models.Model):
    _name = "gateway.setup"
    _description = "GateWay Setup"
    _order = 'sequence'

    sequence = fields.Integer(default=10)
    name = fields.Char(required=True, string='Name')
    gateway = fields.Selection(
        [('africastalking', "AfricasTalking"), ('sasasms', "Sasa SMS")],
        default='sasasms', required=True, string="Gateway")
    gateway_username = fields.Char('Username')
    gateway_api = fields.Char('API Key')

    # SASA SMS
    gateway_url = fields.Char(string='GateWay Endpoint')
    token = fields.Char("X-Token")
    sender = fields.Char("Sender", default="AUTOLAMPS")
    message = fields.Text('Message')
    mobile = fields.Char('Mobile')
    environment = fields.Selection(
        [('test', "Test"), ('production', "Production")], default='test',
        required=True)

    @api.one
    def sms_test_action(self):
        active_model = 'gateway.setup'
        message = self.env['sms.template'].render_template(self.message, active_model, self.id)
        if self.gateway == 'africastalking':
            phone = self.mobile
            # TODO: disabled for now
            # self._africastalking_send_sms(phone, message)
        else:
            self._sasasms_send_sms(False, self.mobile, message)

    def _sasasms_send_sms(self, partner_id, phone, message):
        if not message:
            return
        if len(phone) < 5:
            return

        # sanitize phone numbers
        if self.environment == 'test':
            phone = self.mobile

        phone = phone.strip('-')
        phone = phone.replace(" ", "")

        if phone.startswith("7"):
            phone = "0%s" % phone
        if phone.startswith('+254'):
            phone = "0%s" % phone[4:]
        if phone.startswith('254'):
            phone = "0%s" % phone[3:]

        # Gather values
        payload = {
            "msisdn": phone,
            "sms": message,
            "sender": self.sender
        }

        try:
            headers = {'content-type': 'application/json', 'X-TOKEN': self.token}
            response = requests.post(
                self.gateway_url, data=json.dumps(payload), headers=headers)

            status = 'pending'
            if response.status_code == 200:
                # SMS send successfully
                status = 'sent'

            vals = {
                'provider_id': self.id,
                'phone': phone,
                'name': phone,
                'message': message,
                'date': datetime.datetime.now(),
                'state': status
            }
            if partner_id:
                vals.update({
                    'name': partner_id.name,
                    'partner_id': partner_id.id
                })
            self.env['sms.history'].create(vals)

        except requests.exceptions.ConnectionError as e:
            return False
        except requests.exceptions.Timeout as e:
            return False

    def _africastalking_send_sms(self, phone, message):
        # africastalking.initialize(str(self.gateway_username), str(self.gateway_api))
        #gateway = africastalking.SMS
        gateway = False

        if phone and not phone.startswith('254'):
            to_num = '+254' + phone[1:]  # assume it starts with '0'
        else:
            to_num = phone

        # send the sms using the initialized service
        # TODO: use try here
        results = gateway.send(message, [to_num], enqueue=True)

        vals = {
            'phone': to_num,
            'name': "Uknown",
            'message': message,
            'date': datetime.datetime.now(),
        }
        # search partner
        partner = self.env['res.partner'].search(
            ['|', ('phone', '=', to_num), ('mobile', '=', to_num)], limit=1)
        if partner:
            vals['name'] = partner.name
            vals['partner_id'] = partner.id
        for recipient in results['SMSMessageData']['Recipients']:
            if recipient['status'] == 'Success':
                status = 'sent'
            else:
                status = 'error'
            vals['state'] = status
        # TODO: create sms history if send successfully
        self.env['sms.history'].create(vals)
