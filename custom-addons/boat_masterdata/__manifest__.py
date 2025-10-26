{
    "name": "Boat Master Data",
    "summary": "Static, admin-managed dropdowns used on website and back-office",
    "version": "17.0.1.0.0",
    "license": "LGPL-3",
    "depends": ["base"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/masterdata_menus.xml",
        "views/location_views.xml",
        "views/amenity_views.xml",
        "views/boat_type_views.xml",
        "data/boat_type_data.xml",
    ],
    "application": False,
}
