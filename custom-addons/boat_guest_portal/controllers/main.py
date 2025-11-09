from datetime import datetime, timedelta
from odoo import http
from odoo.http import request


class BoatWebsite(http.Controller):

    @http.route(["/boats"], type="http", auth="public", website=True)
    def boats(self, **kw):
        domain = [("state", "=", "approved")]
        if kw.get("region_id"):
            domain.append(("region_id", "=", int(kw["region_id"])))
        if kw.get("category_id"):
            domain.append(("category_id", "=", int(kw["category_id"])))
        boats = request.env["boat.boat"].sudo().search(domain, limit=24)
        return request.render("boat_guest_portal.boat_list", {"boats": boats, "kw": kw})


    @http.route(
        ['/boats/<model("boat.boat"):boat>'], type="http", auth="public", website=True
    )
    def boat_detail(self, boat, **kw):
        return request.render("boat_guest_portal.boat_detail", {"boat": boat})

    @http.route(["/book/<int:boat_id>"], type="http", auth="user", website=True)
    def book_form(self, boat_id, **kw):
        boat = request.env["boat.boat"].sudo().browse(boat_id)
        if not boat or boat.state != "approved":
            return request.not_found()
        return request.render("boat_guest_portal.book_form", {"boat": boat})

    @http.route(
        ["/book/create"],
        type="http",
        auth="user",
        methods=["POST"],
        website=True,
        csrf=True,
    )
    def book_create(self, **post):
        uid = request.env.user.id
        env = request.env["boat.booking"].sudo()
        boat_id = int(post.get("boat_id"))
        date_from = post.get("date_from")
        date_to = post.get("date_to")
        guests = int(post.get("guest_count") or 2)
        bk = env.create(
            {
                "boat_id": boat_id,
                "guest_id": uid,
                "date_from": date_from,
                "date_to": date_to,
                "guest_count": guests,
            }
        )
        bk.compute_pricing()
        return request.redirect("/payment/boat/%s" % bk.id)
