{
    "name": "Boat Core",
    "summary": "Core boat master data and states",
    "version": "17.0.1.0.0",
    "license": "LGPL-3",
    "author": "Anil Nair",
    "depends": ["base", "website", "portal", "boat_taxonomy", "boat_masterdata"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/sequence.xml",
        "views/core_menus.xml",
        "views/boat_views.xml",
        "views/master_data_views.xml",
    ],
    "application": False,
}
