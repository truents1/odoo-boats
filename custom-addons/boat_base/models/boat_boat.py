from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class BoatBoat(models.Model):
    _name = 'boat.boat'
    _description = 'Boat'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'featured desc, sequence, name'

    name = fields.Char('Boat Name', required=True, tracking=True)
    code = fields.Char('Boat Code', required=True, copy=False, default='New')
    active = fields.Boolean('Active', default=True, tracking=True)
    sequence = fields.Integer('Sequence', default=10)
    
    # Owner Information
    owner_id = fields.Many2one('res.partner', 'Boat Owner', required=True, 
                               domain=[('is_boat_owner', '=', True)], tracking=True)
    company_id = fields.Many2one('res.company', 'Company', 
                                 default=lambda self: self.env.company)
    
    # Location and Category
    location_id = fields.Many2one('boat.location', 'Location', required=True, tracking=True)
    category_id = fields.Many2one('boat.category', 'Category', required=True, tracking=True)
    
    # State Management
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended')
    ], string='Status', default='draft', tracking=True, copy=False)
    
    # Capacity and Specifications
    guest_capacity = fields.Integer('Guest Capacity', required=True, tracking=True)
    sleeping_capacity = fields.Integer('Sleeping Capacity', required=True)
    num_decks = fields.Integer('Number of Decks', default=1)
    num_bedrooms = fields.Integer('Number of Bedrooms', required=True)
    num_bathrooms = fields.Integer('Number of Bathrooms', required=True)
    onboard_staff = fields.Integer('Onboard Staff Count')
    boat_length = fields.Float('Length (meters)')
    boat_width = fields.Float('Width (meters)')
    build_year = fields.Integer('Build Year')
    
    # Features
    amenity_ids = fields.Many2many('boat.amenity', 'boat_amenity_rel', 
                                   'boat_id', 'amenity_id', 'Amenities')
    
    # Operating Details
    operating_routes = fields.Text('Operating Routes')
    check_in_time = fields.Float('Check-in Time', default=12.0)
    check_out_time = fields.Float('Check-out Time', default=10.0)
    min_booking_days = fields.Integer('Minimum Booking Days', default=1)
    advance_booking_days = fields.Integer('Advance Booking Required (Days)', default=2)
    
    # Pricing
    base_price_per_day = fields.Float('Base Price per Day', required=True, tracking=True)
    base_price_per_person = fields.Float('Price per Person')
    booking_advance_percentage = fields.Float('Booking Advance %', default=30.0)
    
    # Descriptions
    description = fields.Html('Description', sanitize=True)
    meal_options = fields.Text('Meal Options')
    safety_rules = fields.Text('Safety Rules & Policies')
    cancellation_policy = fields.Text('Cancellation Policy')
    
    # Address
    street = fields.Char('Street')
    street2 = fields.Char('Street2')
    city = fields.Char('City')
    state_id = fields.Many2one('res.country.state', 'State')
    country_id = fields.Many2one('res.country', 'Country')
    zip = fields.Char('ZIP')
    
    # Premium Features
    featured = fields.Boolean('Featured Boat', default=False, tracking=True)
    featured_until = fields.Date('Featured Until')
    max_images = fields.Integer('Max Images Allowed', default=10)
    
    # Statistics (computed)
    total_bookings = fields.Integer('Total Bookings', compute='_compute_statistics')
    total_revenue = fields.Float('Total Revenue', compute='_compute_statistics')
    avg_rating = fields.Float('Average Rating', compute='_compute_statistics')
    
    # Images
    image_main = fields.Image('Main Image', max_width=1920, max_height=1080)
    
    @api.model
    def create(self, vals):
        if vals.get('code', 'New') == 'New':
            vals['code'] = self.env['ir.sequence'].next_by_code('boat.boat') or 'New'
        return super().create(vals)
    
    @api.constrains('guest_capacity', 'sleeping_capacity')
    def _check_capacity(self):
        for boat in self:
            if boat.sleeping_capacity > boat.guest_capacity:
                raise ValidationError(_("Sleeping capacity cannot exceed guest capacity!"))
    
    @api.depends('featured', 'featured_until')
    def _compute_featured_status(self):
        today = fields.Date.today()
        for boat in self:
            if boat.featured and boat.featured_until:
                boat.featured = boat.featured_until >= today
    
    def _compute_statistics(self):
        for boat in self:
            # Placeholder for booking statistics
            boat.total_bookings = 0
            boat.total_revenue = 0.0
            boat.avg_rating = 0.0
    
    def action_submit_review(self):
        self.ensure_one()
        if self.state == 'draft':
            self.state = 'pending'
    
    def action_approve(self):
        self.ensure_one()
        if self.state == 'pending':
            self.state = 'approved'
    
    def action_reject(self):
        self.ensure_one()
        if self.state == 'pending':
            self.state = 'rejected'
    
    def action_suspend(self):
        self.ensure_one()
        if self.state == 'approved':
            self.state = 'suspended'
    
    def action_reactivate(self):
        self.ensure_one()
        if self.state == 'suspended':
            self.state = 'approved'