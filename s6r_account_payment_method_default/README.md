# Scalizer Account Payment Method Default

## Features

- Adds a **Default Value** flag on the payment methods of a journal (incoming and
  outgoing payments tabs). Only one default per company and per payment direction.
- On new customer invoices / vendor bills, if the partner has no payment method for the
  company, the company default is used (incoming for customer documents, outgoing for
  vendor documents).
- The **Payment Method** field is available (hidden by default) on the invoice, bill and
  refund lists and can be mass-edited. Only payment methods of active journals are
  proposed.

## Usage

1. Go to _Accounting > Configuration > Journals_, open a bank journal.
2. In _Incoming Payments_ / _Outgoing Payments_, tick **Default Value** on a line.
3. Create an invoice or a bill: the payment method is pre-filled when the partner has
   none.
4. In an invoice/bill list, enable the _Payment Method_ column, select records and edit
   the value in bulk.

## Authors

- Scalizer

## Maintainers

This module is maintained by [Scalizer](https://www.scalizer.fr).

![Scalizer](./static/description/logo.png)
