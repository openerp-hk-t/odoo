# -*- coding: utf-8 -*-
{
    'name': "OpenerpHk_widget",

    'summary': "A left-list and right-form layout",

    'description': "A left-list and right-form layout streamlines navigation and displays real-time details, enhancing user efficiency and experience."
        
    """,
    'author': "cdn.odoo.red",
    'website': "https://cdn.odoo.red/",
    'version': '17.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/security.xml',
        # 'security/ir.model.access.csv',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'assets': {
        'web.assets_backend': [
            "openerphk_widget/static/src/views/list/*.*",
            "openerphk_widget/static/src/views/tree_form_view/*.*",
            "openerphk_widget/static/src/views/fields/*/*.*",
            "openerphk_widget/static/src/core/pager/*.*",
            "openerphk_widget/static/src/core/l10n/*.*",
        ],
    },
    'images': ['static/description/abstract.png'],
}
