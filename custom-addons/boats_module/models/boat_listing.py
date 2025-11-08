from odoo import models, fields, api, exceptions

class BoatListing(models.Model):
    """Core model for boat listings - MINIMAL VERSION"""
    _name = 'boat.listing'
    _description = 'Boat Listing'
    _order = 'create_date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    MODERATION_STATUS = [
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
    ]
    
    PRICING_PERIOD = [
        ('hourly_person', 'Hourly per Person'),
        ('daily_person', 'Daily per Person'),
        ('hourly_boat', 'Hourly for Entire Boat'),
        ('daily_boat', 'Daily for Entire Boat'),
    ]
    
    # Basic Information
    name = fields.Char(string='Boat Name', required=True, tracking=True)
    business_name = fields.Char(string='Business/Brand Name')
    registration_number = fields.Char(string='Registration Number')
    owner_id = fields.Many2one('res.users', string='Owner', required=True, 
                                default=lambda self: self.env.user,
                                domain="[('user_type', '=', 'boat_owner')]")
    
    # Classification
    category_id = fields.Many2one('boat.category', string='Category', required=True)
    build_type_id = fields.Many2one('boat.generic.master', string='Build Type',
                                     domain="[('master_type', '=', 'build_type')]")
    year_built = fields.Integer(string='Year Built/Renovated')
    num_decks = fields.Integer(string='Number of Decks', default=1)
    
    # Capacity
    guest_capacity = fields.Integer(string='Guest Capacity', required=True)
    num_bedrooms = fields.Integer(string='Bedrooms')
    num_bathrooms = fields.Integer(string='Bathrooms')
    onboat_staff = fields.Integer(string='Onboard Staff')
    
    # Description
    description = fields.Html(string='Description')
    
    # Media
    image_ids = fields.Many2many('ir.attachment', 'boat_listing_image_rel',
                                  'listing_id', 'attachment_id', string='Images')
    featured_image_id = fields.Many2one('ir.attachment', string='Featured Image')
    video_url = fields.Char(string='Video URL')
    website_url = fields.Char(string='Website URL')
    
    # Location
    region_id = fields.Many2one('boat.region', string='Region/Location', required=True)
    boarding_point = fields.Char(string='Boarding Jetty/Dock Name', required=True)
    service_area = fields.Text(string='Service Area/Routes')
    
    # Pricing
    currency_id = fields.Many2one('boat.generic.master', string='Currency',
                                   domain="[('master_type', '=', 'currency')]")
    pricing_period = fields.Selection(PRICING_PERIOD, string='Pricing Period', 
                                       required=True, default='daily_boat')
    rent_amount = fields.Float(string='Rent Amount', required=True)
    advance_payment_percent = fields.Float(string='Advance Payment %', default=30.0)
    extra_guest_charge = fields.Float(string='Extra Guest Charge')
    min_booking_hours = fields.Integer(string='Minimum Booking Duration (Hours)', default=1)
    max_booking_hours = fields.Integer(string='Maximum Booking Duration (Hours)', default=720)
    advance_notice_hours = fields.Integer(string='Advance Notice Period (Hours)', default=24)
    
    # Features & Amenities
    amenity_ids = fields.Many2many('boat.generic.master', 'boat_amenity_rel',
                                    domain="[('master_type', '=', 'amenity')]",
                                    string='Amenities')
    meal_type_ids = fields.Many2many('boat.generic.master', 'boat_meal_type_rel',
                                      domain="[('master_type', '=', 'meal_type')]",
                                      string='Meal Types Available')
    cuisine_ids = fields.Many2many('boat.generic.master', 'boat_cuisine_rel',
                                    domain="[('master_type', '=', 'cuisine')]",
                                    string='Cuisine Types')
    included_meals = fields.Text(string='Included Meals Description')
    
    # Safety
    safety_certification = fields.Text(string='Safety Certification Details')
    safety_checklist_ids = fields.Many2many('boat.generic.master', 'boat_safety_rel',
                                             domain="[('master_type', '=', 'safety_item')]",
                                             string='Safety Checklist')
    emergency_number = fields.Char(string='Emergency Contact Number', required=True)
    is_certified = fields.Boolean(string='Is Certified', default=False)
    
    # Activities - SIMPLIFIED WITHOUT RELATED FIELDS
    activity_ids = fields.Many2many('boat.generic.master', 'boat_activity_rel',
                                     domain="[('master_type', '=', 'activity')]",
                                     string='Included Activities')
    addon_ids = fields.Many2many('boat.generic.master', 'boat_addon_rel',
                                  domain="[('master_type', '=', 'addon')]",
                                  string='Paid Add-ons')
    
    # Status
    active = fields.Boolean(string='Active in Service', default=True)
    moderation_status = fields.Selection(MODERATION_STATUS, string='Status',
                                          default='draft', required=True, tracking=True)
    rejection_reason = fields.Text(string='Rejection Reason')
    
    # Computed Fields
    booking_ids = fields.One2many('boat.booking', 'boat_id', string='Bookings')
    review_ids = fields.One2many('boat.review', 'boat_id', string='Reviews')
    average_rating = fields.Float(compute='_compute_ratings', string='Average Rating', store=True)
    review_count = fields.Integer(compute='_compute_ratings', string='Number of Reviews', store=True)
    
    @api.depends('review_ids.rating')
    def _compute_ratings(self):
        for boat in self:
            if boat.review_ids:
                boat.average_rating = sum(boat.review_ids.mapped('rating')) / len(boat.review_ids)
                boat.review_count = len(boat.review_ids)
            else:
                boat.average_rating = 0.0
                boat.review_count = 0
    
    def action_submit_for_approval(self):
        """Boat owner submits listing for admin review"""
        self.ensure_one()
        if self.moderation_status == 'draft':
            self.moderation_status = 'pending'
    
    def action_approve(self):
        """Admin approves the listing"""
        self.ensure_one()
        self.moderation_status = 'approved'
    
    def action_reject(self):
        """Admin rejects the listing"""
        self.ensure_one()
        if not self.rejection_reason:
            raise exceptions.UserError('Please provide a rejection reason.')
        self.moderation_status = 'rejected'