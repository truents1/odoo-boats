from odoo import fields, models

class BoatAmenity(models.Model):
    _name = "boat.amenity"
    _description = "Boat Amenity"
    _order = "name"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
