from odoo import fields, models

class Boat(models.Model):
    _name = "boat.boat"
    _description = "Boat"

    name = fields.Char(required=True)
    description = fields.Text(required=True)
    owner_id = fields.Many2one("res.partner", string="Owner", required=True)

    location_id = fields.Many2one(
        "boat.location", required=True, ondelete="restrict", tracking=True
    )
    type_id = fields.Many2one(
        "boat.type", ondelete="restrict", tracking=True
    )
    amenity_ids = fields.Many2many(
        "boat.amenity", "boat_boat_amenity_rel", "boat_id", "amenity_id",
        string="Amenities"
    )

    image_ids = fields.One2many("boat.boat.image", "boat_id")
    is_published = fields.Boolean(default=False)

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("under_review", "Under Review"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        default="draft",
        required=True,
        ondelete={
            "draft": "set default",
            "under_review": "set default",
            "approved": "set default",
            "rejected": "set default",
        },
    )
