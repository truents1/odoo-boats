from odoo import fields, models

class BoatMasterAmenity(models.Model):
    _name = "boat.master.amenity"
    _description = "Boat Amenity"
    _order = "sequence, name"

    name = fields.Char(required=True)
    code = fields.Char()
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)