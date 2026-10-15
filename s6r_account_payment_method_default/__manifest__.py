# Copyright 2026 Scalizer (<https://www.scalizer.fr>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    "name": "Scalizer Account Payment Method Default",
    "version": "19.0.1.0.0",
    "author": "Scalizer, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "category": "Accounting/Accounting",
    "summary": "Default payment method per company, applied on new invoices and "
    "bills, and mass-editable on invoice lists.",
    "sequence": 100,
    "license": "LGPL-3",
    "depends": ["account"],
    "complexity": "easy",
    "qweb": [],
    "demo": [],
    "images": ["static/description/icon.png"],
    "data": [
        "views/account_journal_views.xml",
        "views/account_move_views.xml",
    ],
    "auto_install": False,
    "installable": True,
    "application": False,
}
