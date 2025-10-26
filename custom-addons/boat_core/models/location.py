from odoo import fields, models

class BoatLocation(models.Model):
    _name = "boat.location"
    _description = "Boat Location"
    _order = "sequence, name"

    name = fields.Char(required=True)
    code = fields.Char(required=True, index=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ("code_unique", "unique(code)", "Location code must be unique."),
    ]
