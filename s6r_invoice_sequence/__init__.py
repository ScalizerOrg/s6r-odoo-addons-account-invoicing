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
    return True