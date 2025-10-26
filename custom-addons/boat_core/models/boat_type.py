from odoo import fields, models

class BoatType(models.Model):
    _name = "boat.type"
    _description = "Boat Type"
    _order = "sequence, name"

    name = fields.Char(required=True)
    code = fields.Char(required=True, index=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ("code_unique", "unique(code)", "Type code must be unique."),
    ]
