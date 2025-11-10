{
    "name": "Boat Core",
    "summary": "Boat entity and fields",
    "version": "17.0.1.0",
    "license": "LGPL-3",
    "author": "Your Company",
    "website": "https://example.com",
    "depends": ["base", "website", "boat_masterdata"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/boat_backend_menu.xml",
        # "views/menu.xml",  # ← add this
    ],
    "assets": {"web.assets_frontend": [], "web.assets_backend": []},
    "installable": True,
    "application": False,
}
