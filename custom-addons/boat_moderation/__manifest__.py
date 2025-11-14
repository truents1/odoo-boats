{
  'name': 'Boat Moderation',
  'summary': 'Admin moderation views',
  'version': '17.0.1.0',
  'license': 'LGPL-3',
  'author': 'Your Company',
  'website': 'https://example.com',
  'depends': ['base', 'boat_core'],
     'data': [
        'security/ir.model.access.csv',
        'views/boat_moderation_views.xml',
        'views/boat_moderation_menu.xml',
    ],
  'assets': {
    'web.assets_frontend': [],
    'web.assets_backend': []
  },
  'installable': True,
  'application': False
}
