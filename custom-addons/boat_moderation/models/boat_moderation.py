from odoo import models, fields

class BoatModeration(models.Model):
    _name = "boat.moderation"
    _description = "Boat Moderation"

    name = fields.Char(required=True)
    state = fields.Selection(
        [("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")],
        default="pending",
    )
