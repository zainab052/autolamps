# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from openerp import models, api, _


class print_commission_summary_template(models.AbstractModel):
    _name = 'report.aspl_pos_sales_commission.print_commission_summary_template'
    _table = 'report_pos_commission_print_commission_summary_template'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('aspl_pos_sales_commission.print_commission_summary_template')
        docargs = {
            'doc_ids': self.env['wizard.commission.summary'].search([('id', 'in', list(data["ids"]))]),
            'doc_model': report.model,
            'docs': self,
            'data': data,
            'get_sorted_summary': self._get_sorted_summary
        }
        return report_obj.render('aspl_pos_sales_commission.print_commission_summary_template', docargs)

    def _get_sorted_summary(self, summary):
        return sorted(summary.items(), key=lambda item: item[1], reverse=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: