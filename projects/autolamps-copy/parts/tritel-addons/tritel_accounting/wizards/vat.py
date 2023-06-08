# -*- coding: utf-8 -*-

from openerp import api, fields, models, exceptions 

class VATReportWizard(models.TransientModel):
    _name = "vat.report.wizard"

    start_date = fields.Date()
    end_date = fields.Date()

    @api.multi
    def print_xlsx_report(self):
        datas = {
            # 'ids': [],
            # 'model': 'account.move.line',
            'form': self.read()[0]
        } 

        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'vat.xlsx',
            'datas': datas,
            'name': 'VAT Report'
        }