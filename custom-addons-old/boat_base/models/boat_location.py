from odoo import models, fields, api


class BoatLocation(models.Model):
    """Boat Locations - Where boats are stationed"""
    _name = 'boat.location'
    _description = 'Boat Location'
    _order = 'name'

    name = fields.Char('Location Name', required=True, translate=True)
    description = fields.Text('Description', translate=True)
    active = fields.Boolean('Active', default=True, help="Uncheck to archive the location")
    
    # Address details
    street = fields.Char('Street')
    street2 = fields.Char('Street2')
    city = fields.Char('City')
    state_id = fields.Many2one('res.country.state', 'State')
    zip = fields.Char('ZIP Code')
    country_id = fields.Many2one('res.country', 'Country')
    
    # Coordinates
    latitude = fields.Float('Latitude', digits=(10, 7))
    longitude = fields.Float('Longitude', digits=(10, 7))
    
    # Contact
    phone = fields.Char('Phone')
    email = fields.Char('Email')
    website = fields.Char('Website')
    
    # Image
    image = fields.Image('Location Image', max_width=512, max_height=512)
    
    # Related boats
    boat_ids = fields.One2many('boat.boat', 'location_id', 'Boats at this Location')
    boat_count = fields.Integer('Number of Boats', compute='_compute_boat_count')

    @api.depends('boat_ids')
    def _compute_boat_count(self):
        """Count boats at this location"""
        for location in self:
            location.boat_count = len(location.boat_ids)

    def action_view_boats(self):
        """View boats at this location"""
        self.ensure_one()
        return {
            'name': f'{self.name} - Boats',
            'type': 'ir.actions.act_window',
            'res_model': 'boat.boat',
            'view_mode': 'kanban,tree,form',
            'domain': [('location_id', '=', self.id)],
            'context': {
                'default_location_id': self.id,
            },
        }

    def name_get(self):
        """Display name with city if available"""
        result = []
        for location in self:
            if location.city:
                name = f"{location.name} ({location.city})"
            else:
                name = location.name
            result.append((location.id, name))
        return result