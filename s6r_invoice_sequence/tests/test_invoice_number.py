import logging

from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestInvoiceNumber(TransactionCase):

    def setUp(self):
        super(TestInvoiceNumber, self).setUp()
        # invoices = self.env['account.move'].search([('move_type', '=', 'out_invoice')])
        # for inv in invoices:
        #     inv.button_draft()
        #     inv.write({'name': False})
        #     inv.button_cancel()
        #     inv.unlink()
        # Setup environment and records
        self.account_move = self.env['account.move'].with_context(sequence_test=True)

        # Create a test invoice
        self.test_invoice_1 = self.account_move.create({
            'move_type': 'out_invoice',
            'partner_id': self.env.ref('base.res_partner_2').id,
            'invoice_date': '2024-01-01',
            'invoice_line_ids': [(0, 0, {
                'product_id': self.env.ref('product.product_product_1').id,
                'quantity': 1,
                'price_unit': 100,
            })]
        })
        self.test_invoice_2 = self.account_move.create({
            'move_type': 'out_invoice',
            'partner_id': self.env.ref('base.res_partner_1').id,
            'invoice_date': '2024-02-01',
            'invoice_line_ids': [(0, 0, {
                'product_id': self.env.ref('product.product_product_1').id,
                'quantity': 1,
                'price_unit': 100,
            })]
        })
        self.test_invoice_3 = self.account_move.create({
            'move_type': 'out_invoice',
            'partner_id': self.env.ref('base.res_partner_1').id,
            'invoice_date': '2024-01-02',
            'invoice_line_ids': [(0, 0, {
                'product_id': self.env.ref('product.product_product_1').id,
                'quantity': 1,
                'price_unit': 100,
            })]
        })

    def test_invoice_number_format(self):
        # Confirm the invoices to generate the invoice numbers
        self.test_invoice_1.with_context(sequence_test=True).action_post()
        self.test_invoice_2.with_context(sequence_test=True).action_post()
        self.test_invoice_3.with_context(sequence_test=True).action_post()

        # Retrieve the generated invoice numbers
        invoice_number_1 = self.test_invoice_1.name
        invoice_number_2 = self.test_invoice_2.name
        invoice_number_3 = self.test_invoice_3.name
        journal = self.test_invoice_1.journal_id
        self.assertEqual(invoice_number_1, '2024-01-{}001'.format(journal.code))
        self.assertEqual(invoice_number_2, '2024-02-{}002'.format(journal.code))
        self.assertEqual(invoice_number_3, '2024-01-{}003'.format(journal.code))
