from odoo import fields, models

class BoatImage(models.Model):
    _name = "boat.boat.image"
    _description = "Boat image"
    _order = "id"

    boat_id = fields.Many2one("boat.boat", required=True, ondelete="cascade", index=True)
    name = fields.Char()
    image = fields.Image(required=True, attachment=True)

