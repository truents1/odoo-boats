{
  'name': 'Boat Guest Portal',
  'summary': 'Public search and boat detail pages',
  'version': '17.0.1.0',
  'license': 'LGPL-3',
  'author': 'Your Company',
  'website': 'https://example.com',
  'depends': ['website', 'portal', 'boat_core', 'boat_masterdata'],
  'data': [
        'views/boat_guest_templates.xml', 'views/owner_portal_templates.xml',
    ],
  'assets': {
    'web.assets_frontend': [],
    'web.assets_backend': []
  },
  'installable': True,
  'application': False
}
