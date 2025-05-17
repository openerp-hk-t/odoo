# -*- coding: utf-8 -*-
{
    'name': "Graphical Access Control",

    'summary': "Graphical Access Control",

    'description': """
        Easily manage permissions with our intuitive graphical interface—no coding needed. Just drag, drop, and configure visually.
    """,
    'author': "cdn.odoo.red",
    'website': "https://cdn.odoo.red/",
    'version': '17.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/openerphk_authority.xml',
        'views/res_users.xml',
        'wizard/import_authority_wizard.xml',
        # 'views/menu.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'assets': {
        'web.assets_backend': [
            'openerphk_authority/static/src/**/*',
            'openerphk_authority/static/src/**/**/*',
        ]
    },
    'images': ['static/description/abstract.png'],

}
