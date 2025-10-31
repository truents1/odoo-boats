{
    'name': 'Boat Management Base',
    'version': '17.0.1.0.0',
    'category': 'Services',
    'summary': 'Boat rental and management system',
    'description': """
        Boat Management Base Module
        ============================
        This module provides the base functionality for managing boats, including:
        * Boat registration and details
        * Boat categories and classifications
        * Location management
        * Amenities and features tracking
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'contacts',
    ],
    'data': [
        # Security
        'security/boat_security.xml',
        'security/ir.model.access.csv',
        
        # Views (actions must come before menus that reference them)
        'views/boat_views.xml',
        
        # Menus (comes last, after all actions are defined)
        'views/boat_menu.xml',
    ],
    'demo': [],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}