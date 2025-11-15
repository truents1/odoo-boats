# custom/boat_owner_portal/controllers/owner.py
from odoo import http
from odoo.http import request


class BoatWebsite(http.Controller):

    @http.route(
        ["/boats", "/boats/page/<int:page>"],
        type="http",
        auth="public",
        website=True,
        sitemap=True,
    )
    def boats(self, page=1, **kw):
        Boats = request.env["boat.boat"].sudo()
        boats = Boats.search(
            [], order="create_date desc", limit=60, offset=(page - 1) * 60
        )
        return request.render("boat_guest_portal.boat_list", {"boats": boats})

    @http.route("/boats/new", type="http", auth="user", website=True)
    def new_boat(self, **post):
        # GET: render form
        if request.httprequest.method == "GET":
            return request.render(
                "boat_owner_portal.owner_boat_form_page",
                {
                    "categories": request.env["boat.category"].sudo().search([]),
                    "build_types": request.env["boat.build.type"].sudo().search([]),
                },
            )
        # POST: create record
        vals = {
            "name": post.get("name"),
            "owner_id": request.env.user.partner_id.id,
            "brand_name": post.get("brand_name") or False,
            "registration_no": post.get("registration_no") or False,
            "category_id": (
                int(post["category_id"]) if post.get("category_id") else False
            ),
            "year_built": post.get("year_built") or False,
            "build_type_id": (
                int(post["build_type_id"]) if post.get("build_type_id") else False
            ),
            "decks": int(post["decks"]) if post.get("decks") else 0,
            "guest_capacity": (
                int(post["guest_capacity"]) if post.get("guest_capacity") else 0
            ),
            "bedrooms": int(post["bedrooms"]) if post.get("bedrooms") else 0,
            "bathrooms": int(post["bathrooms"]) if post.get("bathrooms") else 0,
            "onboat_staff": (
                int(post["onboat_staff"]) if post.get("onboat_staff") else 0
            ),
            "description": post.get("description") or "",
            "video_url": post.get("video_url") or False,
            "website_url": post.get("website_url") or False,
            "active": True if post.get("active") == "on" else False,
        }
        boat = request.env["boat.boat"].sudo().create(vals)
        # TODO: handle images (see step 5)
        return request.redirect("/boats")  # or owner dashboard
