from odoo import fields, models

class BoatOption(models.Model):
    _name = "boat.option"
    _description = "Generic Option"
    _order = "master_type, sequence, name"

    name = fields.Char(required=True)
    master_type = fields.Selection([
        ("build_type","Build Type"), ("amenity","Amenity"),
        ("meal_type","Meal Type"), ("cuisine_type","Cuisine Type"),
        ("included_meal","Included Meal"), ("safety_check","Safety Check"),
        ("activity","Included Activity"), ("paid_addon","Paid Add-on"),
        ("pricing_period","Pricing Period")
    ], required=True, index=True)
    value_code = fields.Char()
    sequence = fields.Integer()
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('uniq_name_type', 'unique(name, master_type)',
         'Duplicate name for the same master type.')
    ]
