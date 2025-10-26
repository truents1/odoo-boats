from odoo import fields, models

class BoatMasterBoatType(models.Model):
    _name = "boat.master.boat_type"
    _description = "Boat Type"
    _order = "sequence, name"

    name = fields.Char(required=True)
    parent_id = fields.Many2one("boat.master.boat_type", ondelete="restrict")
    child_ids = fields.One2many("boat.master.boat_type", "parent_id")
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
