# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Scalizer Invoice Sequence',
    'version' : '17.0.1.1',
    'summary': 'Invoice sequence for Scalizer' ,
    'description': """
This module customize the invoice sequence for Scalizer """,
    'website': 'https://scalizer.fr',
    'depends': ['account'],
    'data': [
    ],
    'post_init_hook': '_update_journal_regex',
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
