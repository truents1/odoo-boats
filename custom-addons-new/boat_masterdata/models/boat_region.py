from odoo import api, fields, models

class BoatRegion(models.Model):
    _name = "boat.region"
    _description = "Region/Location"

    name = fields.Char(required=True)
    description = fields.Html()
    image_ids = fields.Many2many('ir.attachment', string="Images")
    latitude = fields.Float()
    longitude = fields.Float()
    state = fields.Char()
    country = fields.Char()
    active = fields.Boolean(default=True)
