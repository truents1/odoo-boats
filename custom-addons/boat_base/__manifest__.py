# -*- coding: utf-8 -*-
{
    'name': 'Boat Management Base',
    'version': '17.0.1.0.0',
    'category': 'Boat Management',
    'summary': 'Base module for boat rental management system',
    'description': """
        YayBoat - Boat Rental Management System
        ========================================
        Base module providing core functionality for boat rental platform:
        - Master data management (locations, categories, amenities)
        - Boat listing management
        - Owner and guest management
        - Commission configuration
    """,
    'author': 'YayBoat',
    'website': 'https://yayboat.com',
    'depends': [
        'base',
        'mail',
        'portal',
        'website',
        'contacts',
    ],
    'data': [
        # Security
        'security/boat_security.xml',
        'security/ir.model.access.csv',
        
        # Data
        'data/boat_data.xml',
        
        # Views
        'views/boat_menu.xml',
        'views/boat_location_views.xml',
        'views/boat_category_views.xml',
        'views/boat_amenity_views.xml',
        'views/boat_views.xml',
        'views/res_partner_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'boat_base/static/src/css/boat_backend.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
