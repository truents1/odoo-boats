from odoo import models, fields, api, _

class BoatAmenity(models.Model):
    _name = 'boat.amenity'
    _description = 'Boat Amenity'
    _order = 'category, sequence, name'

    name = fields.Char('Amenity Name', required=True)
    code = fields.Char('Code', required=True, copy=False)
    sequence = fields.Integer('Sequence', default=10)
    active = fields.Boolean('Active', default=True)
    
    category = fields.Selection([
        ('comfort', 'Comfort'),
        ('entertainment', 'Entertainment'),
        ('safety', 'Safety'),
        ('dining', 'Dining'),
        ('connectivity', 'Connectivity'),
        ('outdoor', 'Outdoor'),
        ('other', 'Other')
    ], string='Category', default='comfort', required=True)
    
    icon = fields.Char('Icon Class', help='Font Awesome icon class (e.g., fa-wifi)')
    description = fields.Text('Description')
    is_premium = fields.Boolean('Premium Amenity', default=False)
    
    # Related
    boat_ids = fields.Many2many('boat.boat', 'boat_amenity_rel', 'amenity_id', 'boat_id', 'Boats')
    
    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'Amenity code must be unique!')
    ]