from odoo import models, fields, api


class BoatCategory(models.Model):
    """Boat Categories - Types of boats available"""
    _name = 'boat.category'
    _description = 'Boat Category'
    _order = 'sequence, name'

    name = fields.Char('Category Name', required=True, translate=True)
    description = fields.Text('Description', translate=True)
    sequence = fields.Integer('Sequence', default=10, help="Display order")
    active = fields.Boolean('Active', default=True, help="Uncheck to archive the category")
    
    # Image for category
    image = fields.Image('Category Image', max_width=512, max_height=512)
    
    # Related boats
    boat_ids = fields.One2many('boat.boat', 'category_id', 'Boats')
    boat_count = fields.Integer('Number of Boats', compute='_compute_boat_count')

    @api.depends('boat_ids')
    def _compute_boat_count(self):
        """Count boats in this category"""
        for category in self:
            category.boat_count = len(category.boat_ids)

    def action_view_boats(self):
        """View boats in this category"""
        self.ensure_one()
        return {
            'name': f'{self.name} - Boats',
            'type': 'ir.actions.act_window',
            'res_model': 'boat.boat',
            'view_mode': 'kanban,tree,form',
            'domain': [('category_id', '=', self.id)],
            'context': {
                'default_category_id': self.id,
            },
        }