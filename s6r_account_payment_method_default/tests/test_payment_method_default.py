# Copyright 2026 Scalizer (<https://www.scalizer.fr>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo.exceptions import ValidationError
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestPaymentMethodDefault(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.journal = cls.company_data["default_journal_bank"]
        cls.inbound = cls.journal.inbound_payment_method_line_ids[:1]
        cls.outbound = cls.journal.outbound_payment_method_line_ids[:1]
        cls.partner = cls.env["res.partner"].create({"name": "Test partner"})

    def _create_move(self, move_type, partner=None):
        return self.env["account.move"].create(
            {
                "move_type": move_type,
                "partner_id": (partner or self.partner).id,
                "invoice_date": "2026-01-01",
                "invoice_line_ids": [
                    (0, 0, {"name": "line", "quantity": 1, "price_unit": 100})
                ],
            }
        )

    def _second_line(self, payment_type):
        journal = self.env["account.journal"].create(
            {
                "name": "Second bank",
                "type": "bank",
                "code": "BNK2",
                "company_id": self.env.company.id,
            }
        )
        return journal[f"{payment_type}_payment_method_line_ids"][:1]

    def test_unique_default_per_company_and_type(self):
        self.outbound.is_default = True
        with self.assertRaises(ValidationError):
            self._second_line("outbound").is_default = True

    def test_inbound_and_outbound_defaults_coexist(self):
        self.outbound.is_default = True
        self.inbound.is_default = True
        self.assertTrue(self.inbound.is_default and self.outbound.is_default)

    def test_other_company_default_allowed(self):
        self.outbound.is_default = True
        other = self.setup_other_company()["default_journal_bank"]
        other.outbound_payment_method_line_ids[:1].is_default = True

    def test_vendor_bill_company_default(self):
        self.outbound.is_default = True
        bill = self._create_move("in_invoice")
        self.assertEqual(bill.preferred_payment_method_line_id, self.outbound)

    def test_customer_invoice_company_default(self):
        self.inbound.is_default = True
        invoice = self._create_move("out_invoice")
        self.assertEqual(invoice.preferred_payment_method_line_id, self.inbound)

    def test_partner_method_has_priority(self):
        self.outbound.is_default = True
        second = self._second_line("outbound")
        self.partner.property_outbound_payment_method_line_id = second
        bill = self._create_move("in_invoice")
        self.assertEqual(bill.preferred_payment_method_line_id, second)

    def test_archived_journal_default_ignored(self):
        second = self._second_line("outbound")
        second.is_default = True
        second.journal_id.active = False
        bill = self._create_move("in_invoice")
        self.assertFalse(bill.preferred_payment_method_line_id)

    def test_mass_write(self):
        bills = self._create_move("in_invoice") | self._create_move("in_invoice")
        bills.preferred_payment_method_line_id = self.outbound
        self.assertEqual(bills.preferred_payment_method_line_id, self.outbound)
