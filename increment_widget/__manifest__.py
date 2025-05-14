{
    'name': 'Increment Widget',
    'version': '1.0',
    'category': 'Technical',
    'summary': 'A widget to increment field value from 0 to target',
    'depends': ['web'],
    'data': [],
    'qweb': [],
    'assets': {
        'web.assets_backend': [
            'increment_widget/static/src/js/increment_widget.js',
            'increment_widget/static/src/xml/increment_widget.xml'
        ],
    },
    'installable': True,
    'application': False,
}