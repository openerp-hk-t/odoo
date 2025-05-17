{
    'name': 'Threshold Color Change',
    'version': '1.0',
    'category': 'Technical',
    'summary': 'A widget to make field text red when value exceeds a threshold',
    'depends': ['web'],
    'data': [],
    'qweb': [],
    'author': "cdn.odoo.red",
    'website': "https://cdn.odoo.red/",
    'assets': {
        'web.assets_backend': [
            'threshold_widget/static/src/js/threshold_widget.js',
            'threshold_widget/static/src/xml/threshold_widget.xml',
            'threshold_widget/static/src/css/threshold_widget.css'
        ],
    },
    'installable': True,
    'application': False,
    'images': ['static/description/icon.gif'],
    'license': 'LGPL-3',
}
