from odoo import fields, models

class BoatLocation(models.Model):
    _name = "boat.location"
    _description = "Boat Location"
    _order = "name"

    name = fields.Char(required=True)
    latitude = fields.Float()
    longitude = fields.Float()
    description = fields.Text()
    image = fields.Image()
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
