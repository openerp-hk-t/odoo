# -*- coding: utf-8 -*-
{
    'name': "WhatsApp ChatBot",

    'summary': "By integrating a large language model with your local database, it enables your chatbot to deliver accurate and intelligent responses to customer inquiries. Whether it’s sales questions, shipment tracking, product specifications, or accounting information, the system provides fast, context-aware answers—streamlining communication and enhancing customer satisfaction ",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'mail_bot', 'web'],

    'author': "cdn.odoo.red",
    'website': "https://cdn.odoo.red/",

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron_data.xml',
        'views/llm_config.xml',
        'views/res_config_setting.xml',
        'views/prompt_config.xml',
        'views/menu.xml',
    ],

    'installable': True,
    'application': False,
    'images': ['static/description/icon.gif'],
    'license': 'LGPL-3',
}
