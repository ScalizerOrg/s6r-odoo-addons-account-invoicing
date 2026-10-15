# Copyright 2026 Scalizer (<https://www.scalizer.fr>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.depends("partner_id", "company_id")
    def _compute_preferred_payment_method_line_id(self):
        """Fall back on the company default when the partner has none."""
        res = super()._compute_preferred_payment_method_line_id()
        line_model = self.env["account.payment.method.line"]
        for move in self:
            if move.preferred_payment_method_line_id or not move.is_invoice(
                include_receipts=True
            ):
                continue
            payment_type = "inbound" if move.is_sale_document() else "outbound"
            move.preferred_payment_method_line_id = line_model._get_default_for(
                move.company_id, payment_type
            )
        return res
