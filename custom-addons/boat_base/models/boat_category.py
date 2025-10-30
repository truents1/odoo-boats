from odoo import models, fields, api, _

class BoatCategory(models.Model):
    _name = 'boat.category'
    _description = 'Boat Category'
    _parent_name = 'parent_id'
    _parent_store = True
    _rec_name = 'complete_name'
    _order = 'complete_name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Category Name', required=True, tracking=True)
    complete_name = fields.Char('Complete Name', compute='_compute_complete_name', store=True)
    code = fields.Char('Category Code', required=True, copy=False)
    active = fields.Boolean('Active', default=True)
    sequence = fields.Integer('Sequence', default=10)
    
    # Hierarchy
    parent_id = fields.Many2one('boat.category', 'Parent Category', index=True, ondelete='cascade')
    parent_path = fields.Char(index=True)
    child_ids = fields.One2many('boat.category', 'parent_id', 'Child Categories')
    
    # Details
    description = fields.Text('Description')
    characteristics = fields.Text('Characteristics')
    image = fields.Image('Category Image', max_width=1920, max_height=1080)
    
    # Related
    boat_ids = fields.One2many('boat.boat', 'category_id', 'Boats')
    boat_count = fields.Integer('Number of Boats', compute='_compute_boat_count')
    
    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for category in self:
            if category.parent_id:
                category.complete_name = f"{category.parent_id.complete_name} / {category.name}"
            else:
                category.complete_name = category.name
    
    @api.depends('boat_ids')
    def _compute_boat_count(self):
        for category in self:
            category.boat_count = len(category.boat_ids)
    
    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'Category code must be unique!')
    ]