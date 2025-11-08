from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'
    
    USER_TYPES = [
        ('guest', 'Guest/Traveler'),
        ('boat_owner', 'Boat Owner'),
    ]
    
    user_type = fields.Selection(USER_TYPES, string='User Type', default='guest')
    business_name = fields.Char(string='Business/Company Name')
    website_url = fields.Char(string='Website')
    about = fields.Text(string='About Me/Business')
    phone_verified = fields.Boolean(string='Phone Verified', default=False)
    email_verified = fields.Boolean(string='Email Verified', default=False)
    
    # Related records
    boat_listing_ids = fields.One2many('boat.listing', 'owner_id', string='My Boats')
    booking_ids = fields.One2many('boat.booking', 'guest_id', string='My Bookings')

