# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


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
    icon = fields.Char(string='Icon Class', help='CSS icon class (e.g., fa-wifi)')

    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Amenity code must be unique!')
    ]


class BoatBoat(models.Model):
    _name = 'boat.boat'
    _description = 'Boat'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
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

    # Images
    image_1920 = fields.Image(string='Main Image', max_width=1920, max_height=1920)
    image_512 = fields.Image(string='Image 512', related='image_1920', max_width=512, max_height=512, store=True)
    image_256 = fields.Image(string='Image 256', related='image_1920', max_width=256, max_height=256, store=True)
    image_128 = fields.Image(string='Image 128', related='image_1920', max_width=128, max_height=128, store=True)

    # Workflow State
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('published', 'Published'),
    ], string='State', default='draft', required=True, tracking=True)

    # SEO & Website Fields (for admin moderation)
    website_published = fields.Boolean(string='Visible on Website', default=False, tracking=True)
    website_meta_title = fields.Char(string='Website Meta Title')
    website_meta_description = fields.Text(string='Website Meta Description')
    website_meta_keywords = fields.Char(string='Website Meta Keywords')
    website_tag_ids = fields.Many2many('boat.tag', string='Website Tags')
    
    # Moderation fields
    moderation_notes = fields.Text(string='Moderation Notes', 
                                   help='Internal notes for moderation team')
    approved_by = fields.Many2one('res.users', string='Approved By', readonly=True)
    approved_date = fields.Datetime(string='Approval Date', readonly=True)
    rejected_reason = fields.Text(string='Rejection Reason')

    # Computed fields
    is_owner = fields.Boolean(string='Is Owner', compute='_compute_is_owner')

    @api.depends('owner_id')
    def _compute_is_owner(self):
        """Check if current user is the owner"""
        for boat in self:
            boat.is_owner = boat.owner_id.id == self.env.user.partner_id.id

    # State transition methods
    def action_submit(self):
        """Submit boat for review (used by portal users)"""
        for boat in self:
            if not boat.owner_id:
                boat.owner_id = self.env.user.partner_id.id
            boat.write({'state': 'submitted'})
        return True

    def action_start_review(self):
        """Start reviewing the boat (used by admin)"""
        self.write({'state': 'under_review'})
        return True

    def action_approve(self):
        """Approve the boat (used by admin)"""
        self.write({
            'state': 'approved',
            'approved_by': self.env.user.id,
            'approved_date': fields.Datetime.now(),
        })
        # Notify owner
        self._send_approval_notification()
        return True

    def action_publish(self):
        """Publish boat to website (used by admin)"""
        self.write({
            'state': 'published',
            'website_published': True,
        })
        return True

    def action_unpublish(self):
        """Unpublish boat from website"""
        self.write({'website_published': False})
        return True

    def action_reject(self):
        """Reject the boat (used by admin)"""
        return {
            'name': _('Reject Boat'),
            'type': 'ir.actions.act_window',
            'res_model': 'boat.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_boat_id': self.id}
        }

    def action_set_draft(self):
        """Reset to draft"""
        self.write({'state': 'draft'})
        return True

    def _send_approval_notification(self):
        """Send email notification to owner when boat is approved"""
        for boat in self:
            if boat.owner_id and boat.owner_id.email:
                template = self.env.ref('boat_base.email_template_boat_approved', raise_if_not_found=False)
                if template:
                    template.send_mail(boat.id, force_send=True)

    def _compute_access_url(self):
        """Compute portal access URL"""
        super()._compute_access_url()
        for boat in self:
            boat.access_url = f'/my/boats/{boat.id}'

    # Constraints
    @api.constrains('guest_capacity', 'sleeping_capacity')
    def _check_capacities(self):
        """Ensure sleeping capacity doesn't exceed guest capacity"""
        for boat in self:
            if boat.sleeping_capacity and boat.guest_capacity:
                if boat.sleeping_capacity > boat.guest_capacity:
                    raise ValidationError(
                        _('Sleeping capacity cannot exceed guest capacity!')
                    )

    @api.constrains('year_built')
    def _check_year_built(self):
        """Validate year built"""
        import datetime
        current_year = datetime.datetime.now().year
        for boat in self:
            if boat.year_built and (boat.year_built < 1900 or boat.year_built > current_year + 1):
                raise ValidationError(
                    _('Year built must be between 1900 and %s') % (current_year + 1)
                )


class BoatTag(models.Model):
    """Website tags for boats"""
    _name = 'boat.tag'
    _description = 'Boat Tag'
    _order = 'name'

    name = fields.Char(string='Tag Name', required=True, translate=True)
    color = fields.Integer(string='Color Index')
    
    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Tag name must be unique!')
    ]