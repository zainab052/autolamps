# -*- coding: utf-8 -*-
from openerp import api, fields, models, exceptions


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.onchange('credit_limit')
    def onchange_credit_limit(self):
        if not self.user_has_groups('autolamps_base.group_edit_credit_limit'):
            old_limit = self._origin.credit_limit
            new_limit = self.credit_limit
            if old_limit != new_limit:
                raise exceptions.AccessError(
                    'You don\'t have Rights to change the Credit Limit. '
                    'Contact Administrator!')

    @api.multi
    def write(self, vals):
        if 'credit_limit' in vals:
            if not self.user_has_groups('autolamps_base.group_edit_credit_limit'):
                old_limit = self.credit_limit
                new_limit = vals.get('credit_limit', 0)
                if old_limit != new_limit:
                    raise exceptions.AccessError(
                        'You don\'t have Rights to change the Credit Limit. '
                        'Contact Administrator!')
        res = super(ResPartner, self).write(vals)
        return res
