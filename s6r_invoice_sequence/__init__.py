from . import models
from odoo.tools import config


def _update_journal_regex(env):
    if not config['test_enable']:
        sale_journal = env['account.journal'].sudo().search([
            ('type', '=', 'sale')
        ])
        regex =  r'^(?P<year>((?<=\D)|(?<=^))((19|20|21)?\d{2}))(?P<prefix1>\D+?)(?P<prefix2>\d{2})(?P<prefix3>\D+?)(?P<seq>\d*)$'
        sale_journal.sudo().write({
            'sequence_override_regex': regex
        })
        invoices = env['account.move'].search([('move_type', 'in', ('out_invoice', 'out_refund'))])
        for inv in invoices:
            inv._compute_split_sequence()
    return True