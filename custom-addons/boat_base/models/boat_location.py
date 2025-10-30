from odoo import models, fields, api, _

class BoatLocation(models.Model):
    _name = 'boat.location'
    _description = 'Boat Location'
    _order = 'sequence, name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Location Name', required=True, tracking=True)
    code = fields.Char('Location Code', required=True, copy=False)
    sequence = fields.Integer('Sequence', default=10)
    active = fields.Boolean('Active', default=True, tracking=True)
    
    # Geographic data
    street = fields.Char('Street')
    street2 = fields.Char('Street2')
    city = fields.Char('City')
    state_id = fields.Many2one('res.country.state', 'State')
    country_id = fields.Many2one('res.country', 'Country', required=True)
    zip = fields.Char('ZIP')
    latitude = fields.Float('Latitude', digits=(16, 8))
    longitude = fields.Float('Longitude', digits=(16, 8))
    
    # Media
    image = fields.Image('Location Image', max_width=1920, max_height=1080)
    description = fields.Html('Description', sanitize=True)
    highlights = fields.Text('Highlights')
    
    # Related
    boat_ids = fields.One2many('boat.boat', 'location_id', 'Boats')
    boat_count = fields.Integer('Number of Boats', compute='_compute_boat_count')
    
    # SEO
    website_meta_title = fields.Char('Website Meta Title')
    website_meta_description = fields.Text('Website Meta Description')
    website_meta_keywords = fields.Char('Website Meta Keywords')
    
    @api.depends('boat_ids')
    def _compute_boat_count(self):
        for location in self:
            location.boat_count = len(location.boat_ids)
    
    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'Location code must be unique!')
    ]
    
    def name_get(self):
        result = []
        for location in self:
            name = location.name
            if location.city:
                name = f"{name} ({location.city})"
            result.append((location.id, name))
        return result