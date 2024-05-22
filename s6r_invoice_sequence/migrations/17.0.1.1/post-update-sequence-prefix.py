import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    invoices = env['account.move'].search([('move_type', 'in', ('out_invoice', 'out_refund'))])
    for inv in invoices:
        inv._compute_split_sequence()
