# -*- coding: utf-8 -*-
{
    'name': "OpenerpHk_login_log",

    'summary': "Login log",

    'description': """
        Logs user login time, ID, IP, and browser info for clear tracking and improved security management.
    """,
    'author': "cdn.odoo.red",
    'website': "https://cdn.odoo.red/",

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/login_log.xml',
        'views/menu.xml'
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'images': ['static/description/abstract.png']

}
