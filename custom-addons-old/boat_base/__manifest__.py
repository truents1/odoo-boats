{
    'name': 'Boat Base',
    'version': '1.0',
    'category': 'Services',
    'summary': 'Boat rental management system with multi-image gallery support',
    'description': """
        Boat Base Module
        =================
        Core module for boat rental platform featuring:
        - Boat management with multiple images
        - Featured image selection
        - Image gallery with drag-and-drop ordering
        - Boat categories and locations
        - Owner and guest management
        - Booking workflow
        - State management (draft, submitted, approved, published)
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'mail',
        'web',
    ],
    'data': [
        # Security
        'security/ir.model.access.csv',
        
        # Data
        'data/boat_category_data.xml',
        'data/boat_location_data.xml',
        
        # Views
        'views/boat_views.xml',
        'views/boat_image_views.xml',
        'views/boat_category_views.xml',
        'views/boat_location_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'boat_base/static/src/css/boat_image.css',
        ],
    },
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}