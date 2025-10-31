from odoo import models, fields, api


class BoatCategory(models.Model):
    _name = 'boat.category'
    _description = 'Boat Category'
    _parent_name = 'parent_id'
    _parent_store = True
    _order = 'complete_name'

    name = fields.Char(string='Name', required=True, translate=True)
    complete_name = fields.Char(
        string='Complete Name',
        compute='_compute_complete_name',
        recursive=True,
        store=True
    )
    parent_id = fields.Many2one('boat.category', string='Parent Category', ondelete='cascade')
    parent_path = fields.Char(index=True, unaccent=False)
    child_ids = fields.One2many('boat.category', 'parent_id', string='Child Categories')
    description = fields.Text(string='Description')

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for category in self:
            if category.parent_id:
                category.complete_name = f'{category.parent_id.complete_name} / {category.name}'
            else:
                category.complete_name = category.name


class BoatLocation(models.Model):
    _name = 'boat.location'
    _description = 'Boat Location'
    _order = 'name'

    name = fields.Char(string='Location Name', required=True)
    code = fields.Char(string='Location Code', size=10)
    address = fields.Text(string='Address')
    city = fields.Char(string='City')
    country_id = fields.Many2one('res.country', string='Country')
    latitude = fields.Float(string='Latitude', digits=(10, 7))
    longitude = fields.Float(string='Longitude', digits=(10, 7))
    active = fields.Boolean(string='Active', default=True)

    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Location code must be unique!')
    ]


class BoatAmenity(models.Model):
    _name = 'boat.amenity'
    _description = 'Boat Amenity'
    _order = 'name'

    name = fields.Char(string='Amenity Name', required=True, translate=True)
    code = fields.Char(string='Code', size=20)
    description = fields.Text(string='Description', translate=True)

    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Amenity code must be unique!')
    ]


class BoatBoat(models.Model):
    _name = 'boat.boat'
    _description = 'Boat'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    # Basic Information
    name = fields.Char(string='Boat Name', required=True, tracking=True)
    category_id = fields.Many2one('boat.category', string='Category', tracking=True)
    owner_id = fields.Many2one('res.partner', string='Owner', tracking=True)
    location_id = fields.Many2one('boat.location', string='Location', tracking=True)
    active = fields.Boolean(string='Active', default=True)

    # Specifications
    guest_capacity = fields.Integer(string='Guest Capacity', default=1)
    sleeping_capacity = fields.Integer(string='Sleeping Capacity', default=1)
    num_bedrooms = fields.Integer(string='Number of Bedrooms', default=0)
    num_bathrooms = fields.Integer(string='Number of Bathrooms', default=0)
    length = fields.Float(string='Length (m)', digits=(10, 2))
    year_built = fields.Integer(string='Year Built')

    # Technical Details
    engine_type = fields.Char(string='Engine Type')
    fuel_capacity = fields.Float(string='Fuel Capacity (L)', digits=(10, 2))
    max_speed = fields.Float(string='Max Speed (knots)', digits=(10, 2))

    # Pricing
    base_price_per_day = fields.Monetary(string='Base Price per Day', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency', 
                                   default=lambda self: self.env.company.currency_id)

    # Description & Features
    description = fields.Html(string='Description', translate=True)
    feature_ids = fields.Many2many('boat.amenity', string='Features & Amenities')

    # State Management
    state = fields.Selection([
        ('draft', 'Draft'),
        ('available', 'Available'),
        ('booked', 'Booked'),
        ('maintenance', 'Maintenance'),
    ], string='State', default='draft', required=True, tracking=True)

    # State transition methods
    def action_set_available(self):
        """Set boat state to available"""
        self.write({'state': 'available'})
        return True

    def action_set_maintenance(self):
        """Set boat state to maintenance"""
        self.write({'state': 'maintenance'})
        return True

    def action_set_draft(self):
        """Set boat state to draft"""
        self.write({'state': 'draft'})
        return True

    def action_set_booked(self):
        """Set boat state to booked"""
        self.write({'state': 'booked'})
        return True

    # Constraints
    _sql_constraints = [
        ('guest_capacity_positive', 'CHECK(guest_capacity > 0)', 
         'Guest capacity must be positive!'),
        ('sleeping_capacity_positive', 'CHECK(sleeping_capacity > 0)', 
         'Sleeping capacity must be positive!'),
        ('base_price_positive', 'CHECK(base_price_per_day >= 0)', 
         'Base price must be positive or zero!'),
    ]

    @api.constrains('guest_capacity', 'sleeping_capacity')
    def _check_capacities(self):
        """Ensure sleeping capacity doesn't exceed guest capacity"""
        for boat in self:
            if boat.sleeping_capacity > boat.guest_capacity:
                from odoo.exceptions import ValidationError
                raise ValidationError(
                    'Sleeping capacity cannot exceed guest capacity!'
                )