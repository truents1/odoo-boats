from odoo import fields, models

class BoatCategory(models.Model):
    _name = "boat.category"
    _description = "Boat Category"

    name = fields.Char(required=True)
    parent_id = fields.Many2one('boat.category', string="Parent")
    active = fields.Boolean(default=True)
