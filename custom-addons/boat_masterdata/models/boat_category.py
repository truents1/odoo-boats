from odoo import fields, models

class BoatCategory(models.Model):
    _name = "boat.category"
    _description = "Boat Category"

    name = fields.Char(required=True)
    parent_id = fields.Many2one('boat.category', string="Parent")
    description = fields.Text()            # <-- add this
    active = fields.Boolean(default=True)
