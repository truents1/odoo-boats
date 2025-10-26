from odoo import http
from odoo.http import request


class BoatPortalSubmit(http.Controller):

    @http.route(["/boats/new"], type="http", auth="user", website=True)
    def boat_new(self, **kw):
        # Require active portal user
        if not request.env.user.active or not request.env.user.has_group(
            "base.group_portal"
        ):
            return request.redirect("/web/login")

        locations = (
            request.env["boat.taxonomy"]
            .sudo()
            .search(
                [("category_code", "=", "location"), ("active", "=", True)],
                order="sequence, name",
            )
        )

        return request.render(
            "boat_portal_submit.boat_new_template",
            {
                "locations": locations,
            },
        )

    @http.route(
        ["/boats/create"],
        type="http",
        auth="user",
        website=True,
        csrf=True,
        methods=["POST"],
    )
    def boat_create(self, **post):
        user = request.env.user
        if not user.active or not user.has_group("base.group_portal"):
            return request.redirect("/web/login")

        name = (post.get("name") or "").strip()
        description = (post.get("description") or "").strip()
        locations = (
            request.env["boat.location"]
            .sudo()
            .search([("active", "=", True)], order="name")
        )
        types = (
            request.env["boat.type"]
            .sudo()
            .search([("active", "=", True)], order="parent_left, name")
        )
        amenities = (
            request.env["boat.amenity"]
            .sudo()
            .search([("active", "=", True)], order="name")
        )

        files = request.httprequest.files.getlist("images")

        if not name or not description or not location_id or not files:
            return request.redirect("/boats/new?error=missing")

        Boat = request.env["boat.boat"].sudo()
        location_id = post.get('location_id')
        type_id = post.get('type_id')
        amenity_ids = request.httprequest.form.getlist('amenity_ids')
        vals = {
        'name': name,
        'description': description,
        'location_id': int(location_id),
        'type_id': int(type_id) if type_id else False,
        'amenity_ids': [(6, 0, list(map(int, amenity_ids)))],
        'owner_id': user.id,
        'state': 'draft',
        'is_published': False,
        }
        boat = Boat.create(vals)
        Image = request.env["boat.boat.image"].sudo()
        for f in files:
            content = f.read()
            if content:
                Image.create({"boat_id": boat.id, "name": f.filename, "image": content})

        return request.redirect("/boats/submitted")
    
        return request.render(
            "boat_portal_submit.boat_new_template",
            {
                "locations": locations,
                "types": types,
                "amenities": amenities,
            },
        )

    @http.route(["/boats/submitted"], type="http", auth="user", website=True)
    def boat_submitted(self, **kw):
        return request.render("boat_portal_submit.boat_submitted_template")
