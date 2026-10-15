# Copyright 2026 Scalizer (<https://www.scalizer.fr>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AccountPaymentMethodLine(models.Model):
    _inherit = "account.payment.method.line"

    is_default = fields.Boolean(
        string="Default Value",
        help="Used as payment method on new invoices and bills when the partner "
        "has no payment method defined for the company.",
    )

    @api.constrains("is_default", "payment_method_id", "journal_id")
    def _check_is_default_unique(self):
        """Ensure a single default line per company and payment type."""
        for line in self.filtered("is_default"):
            other = self.search(
                [
                    ("id", "!=", line.id),
                    ("is_default", "=", True),
                    ("payment_type", "=", line.payment_type),
                    ("company_id", "=", line.company_id.id),
                ],
                limit=1,
            )
            if other:
                raise ValidationError(
                    self.env._(
                        "%(method)s on journal %(journal)s is already the default "
                        "value for company %(company)s",
                        method=other.name,
                        journal=other.journal_id.display_name,
                        company=other.company_id.display_name,
                    )
                )

    @api.model
    def _get_default_for(self, company, payment_type):
        """Return the default payment method line of a company.

        :param company: ``res.company`` record
        :param str payment_type: ``inbound`` or ``outbound``
        :return: ``account.payment.method.line`` record (possibly empty)
        """
        return self.search(
            [
                ("is_default", "=", True),
                ("payment_type", "=", payment_type),
                ("company_id", "=", company.id),
                ("journal_id.active", "=", True),
            ],
            limit=1,
        )
