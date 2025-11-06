from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Boat(models.Model):
    _name = 'boat.boat'
    _description = 'Boat'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char('Boat Name', required=True, tracking=True)
    
    # Image fields - Main image synced from featured image
    image_1920 = fields.Image('Main Image', max_width=1920, max_height=1920, compute='_compute_main_image', store=True)
    image_512 = fields.Image('Medium Image', related='image_1920', max_width=512, max_height=512, store=True)
    image_256 = fields.Image('Small Image', related='image_1920', max_width=256, max_height=256, store=True)
    image_128 = fields.Image('Thumbnail', related='image_1920', max_width=128, max_height=128, store=True)
    
    # Multiple images support
    image_ids = fields.One2many('boat.image', 'boat_id', 'Images', help="Upload multiple images for this boat")
    image_count = fields.Integer('Image Count', compute='_compute_image_count')
    featured_image_id = fields.Many2one('boat.image', 'Featured Image', compute='_compute_featured_image', store=True)
    
    # Boat details
    category_id = fields.Many2one('boat.category', 'Category', required=True, tracking=True)
    location_id = fields.Many2one('boat.location', 'Location', required=True, tracking=True)
    owner_id = fields.Many2one('res.partner', 'Owner', required=True, tracking=True, domain=[('is_boat_owner', '=', True)])
    
    description = fields.Html('Description')
    guest_capacity = fields.Integer('Guest Capacity', required=True, tracking=True)
    cabins = fields.Integer('Number of Cabins')
    length = fields.Float('Length (meters)')
    year_built = fields.Integer('Year Built')
    
    # Pricing
    base_price_per_day = fields.Float('Base Price Per Day', required=True, tracking=True)
    weekend_price_per_day = fields.Float('Weekend Price Per Day')
    peak_season_price_per_day = fields.Float('Peak Season Price Per Day')
    
    # Features
    has_wifi = fields.Boolean('Has WiFi')
    has_kitchen = fields.Boolean('Has Kitchen')
    has_air_conditioning = fields.Boolean('Has Air Conditioning')
    
    # State management
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('published', 'Published'),
        ('unavailable', 'Unavailable')
    ], 'Status', default='draft', required=True, tracking=True)
    
    # Availability
    available_from = fields.Date('Available From', tracking=True)
    available_to = fields.Date('Available To', tracking=True)
    is_available = fields.Boolean('Currently Available', default=True, tracking=True)

    @api.depends('image_ids.is_featured')
    def _compute_featured_image(self):
        """Get the featured image for the boat"""
        for boat in self:
            featured = boat.image_ids.filtered(lambda img: img.is_featured)
            boat.featured_image_id = featured[:1] if featured else False

    @api.depends('featured_image_id.image_1920')
    def _compute_main_image(self):
        """Sync main image from featured image"""
        for boat in self:
            if boat.featured_image_id:
                boat.image_1920 = boat.featured_image_id.image_1920
            elif boat.image_ids:
                # If no featured image, use the first image
                boat.image_1920 = boat.image_ids[0].image_1920
            else:
                boat.image_1920 = False

    @api.depends('image_ids')
    def _compute_image_count(self):
        """Count total images for the boat"""
        for boat in self:
            boat.image_count = len(boat.image_ids)

    @api.constrains('guest_capacity')
    def _check_guest_capacity(self):
        """Validate guest capacity is positive"""
        for boat in self:
            if boat.guest_capacity <= 0:
                raise ValidationError("Guest capacity must be greater than 0")

    @api.constrains('base_price_per_day')
    def _check_base_price(self):
        """Validate base price is positive"""
        for boat in self:
            if boat.base_price_per_day <= 0:
                raise ValidationError("Base price must be greater than 0")

    def action_submit(self):
        """Submit boat for review"""
        self.write({'state': 'submitted'})

    def action_approve(self):
        """Approve boat"""
        self.write({'state': 'approved'})

    def action_reject(self):
        """Reject boat"""
        self.write({'state': 'rejected'})

    def action_publish(self):
        """Publish boat"""
        self.write({'state': 'published'})

    def action_set_unavailable(self):
        """Set boat as unavailable"""
        self.write({'state': 'unavailable', 'is_available': False})

    def action_view_images(self):
        """Open images gallery view"""
        self.ensure_one()
        return {
            'name': f'{self.name} - Images',
            'type': 'ir.actions.act_window',
            'res_model': 'boat.image',
            'view_mode': 'kanban,tree,form',
            'domain': [('boat_id', '=', self.id)],
            'context': {
                'default_boat_id': self.id,
            },
        }