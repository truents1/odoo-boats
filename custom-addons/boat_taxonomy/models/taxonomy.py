from odoo import fields, models

class BoatTaxonomyCategory(models.Model):
    _name = "boat.taxonomy.category"
    _description = "Boat Taxonomy Category"
    _order = "name"

    name = fields.Char(required=True)
    code = fields.Char(required=True, index=True)
    allow_tree = fields.Boolean(default=True)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ("code_unique", "unique(code)", "Category code must be unique."),
    ]


class BoatTaxonomy(models.Model):
    _name = "boat.taxonomy"
    _description = "Boat Taxonomy Value"
    _order = "category_id, sequence, name"

    name = fields.Char(required=True)
    code = fields.Char()
    category_id = fields.Many2one("boat.taxonomy.category", required=True, ondelete="cascade")
    category_code = fields.Char(related="category_id.code", store=True, index=True)
    parent_id = fields.Many2one("boat.taxonomy", domain="[('category_id','=',category_id)]", ondelete="cascade")
    child_ids = fields.One2many("boat.taxonomy", "parent_id")
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ("name_per_cat_unique", "unique(category_id, name)", "Name must be unique per category."),
    ]
