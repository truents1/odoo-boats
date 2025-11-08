{
    'name': 'Boats Module',
    'version': '17.0.1.0.0',
    'category': 'Website',
    'summary': 'Boat listing platform',
    'depends': ['base', 'web', 'website', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/boat_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
