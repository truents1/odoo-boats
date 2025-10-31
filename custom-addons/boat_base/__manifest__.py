# -*- coding: utf-8 -*-
{
    'name': 'Boat Management Base',
    'version': '17.0.1.0.0',
    'category': 'Services',
    'summary': 'Boat rental and management system with portal and website',
    'description': """
        Boat Management Base Module
        ============================
        This module provides comprehensive boat rental management:
        * Boat registration and details
        * Boat categories and classifications
        * Location management
        * Amenities and features tracking
        * Portal access for boat owners
        * Public website listing for customers
        * Moderation workflow for admins
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'contacts',
        'portal',
        'website',
    ],
    'data': [
        # Security
        'security/boat_security.xml',
        'security/ir.model.access.csv',
        
        # Views (actions must come before menus that reference them)
        'views/boat_views.xml',
        
        # Menus (comes last, after all actions are defined)
        'views/boat_menu.xml',
        
        # Portal & Website Templates
        'views/portal_templates.xml',
        'views/website_templates.xml',
    ],
    'demo': [],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}