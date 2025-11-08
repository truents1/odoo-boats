# -*- coding: utf-8 -*-
{
    'name': 'Houseboat Aggregation Platform',
    'version': '17.0.1.0.0',
    'category': 'Website/Website',
    'summary': 'Complete houseboat booking and listing platform',
    'description': """
        Houseboat Aggregation Platform
        ================================
        
        Features:
        ---------
        * Public boat search and listing
        * Boat owner portal for listing management
        * Guest booking system with payment integration
        * Review and rating system
        * Admin moderation workflow
        * Multi-master data management
        * Email notifications
        * Payment gateway integration (Razorpay, Stripe)
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
        'website',
        'portal',
        'mail',
        'payment',
        'website_payment',
    ],
    'data': [
        # Security
        'security/security.xml',
        'security/ir.model.access.csv',
        
        # Data
        'data/sequence.xml',
        'data/master_data.xml',
        'data/email_templates.xml',
        
        # Views - Backend
        'views/master_data_views.xml',
        'views/boat_listing_views.xml',
        'views/booking_views.xml',
        'views/review_views.xml',
        'views/menu_views.xml',
        
        # Templates - Website
        'templates/website/boat_search.xml',
        'templates/website/boat_detail.xml',
        'templates/website/booking_checkout.xml',
        
        # Templates - Portal
        'templates/portal/owner_dashboard.xml',
        'templates/portal/boat_form.xml',
        'templates/portal/guest_dashboard.xml',
        'templates/portal/portal_templates.xml',
        
        # Assets
        'views/assets.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'odoo_boats/static/src/css/boat_styles.css',
            'odoo_boats/static/src/js/booking_calculator.js',
            'odoo_boats/static/src/js/image_uploader.js',
        ],
    },
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
