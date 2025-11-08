from odoo import models, fields, api, exceptions
from datetime import datetime, timedelta

class BoatBooking(models.Model):
    """Booking records for boat rentals - MINIMAL VERSION"""
    _name = 'boat.booking'
    _description = 'Boat Booking'
    _order = 'create_date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    BOOKING_STATUS = [
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('paid', 'Paid'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('partial', 'Partially Paid'),
        ('paid', 'Fully Paid'),
        ('refunded', 'Refunded'),
    ]
    
    # Reference
    name = fields.Char(string='Booking Reference', required=True, copy=False,
                        default='New', readonly=True)
    
    # Relationships
    boat_id = fields.Many2one('boat.listing', string='Boat', required=True,
                               domain="[('moderation_status', '=', 'approved'), ('active', '=', True)]")
    guest_id = fields.Many2one('res.users', string='Guest', required=True,
                                default=lambda self: self.env.user,
                                domain="[('user_type', '=', 'guest')]")
    
    # Booking Details
    start_date = fields.Datetime(string='Start Date', required=True)
    end_date = fields.Datetime(string='End Date', required=True)
    num_guests = fields.Integer(string='Number of Guests', required=True, default=1)
    duration_hours = fields.Float(compute='_compute_duration', string='Duration (Hours)', store=True)
    
    # Pricing
    base_amount = fields.Float(string='Base Amount')
    total_amount = fields.Float(string='Total Amount')
    net_payable = fields.Float(string='Net Payable Now')
    
    # Payment
    payment_status = fields.Selection(PAYMENT_STATUS, string='Payment Status',
                                       default='pending', tracking=True)
    transaction_id = fields.Char(string='Transaction ID')
    payment_method = fields.Char(string='Payment Method')
    paid_amount = fields.Float(string='Paid Amount')
    
    # Status
    booking_status = fields.Selection(BOOKING_STATUS, string='Booking Status',
                                       default='draft', required=True, tracking=True)
    
    # Cancellation
    is_cancelled = fields.Boolean(string='Is Cancelled', default=False)
    cancellation_date = fields.Datetime(string='Cancellation Date')
    cancellation_reason = fields.Text(string='Cancellation Reason')
    refund_amount = fields.Float(string='Refund Amount')
    
    @api.model
    def create(self, vals):
        """Generate unique booking reference"""
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('boat.booking') or 'New'
        return super(BoatBooking, self).create(vals)
    
    @api.depends('start_date', 'end_date')
    def _compute_duration(self):
        for booking in self:
            if booking.start_date and booking.end_date:
                delta = booking.end_date - booking.start_date
                booking.duration_hours = delta.total_seconds() / 3600
            else:
                booking.duration_hours = 0.0
    
    def check_availability(self):
        """Check for conflicting bookings"""
        self.ensure_one()
        conflicting = self.search([
            ('boat_id', '=', self.boat_id.id),
            ('id', '!=', self.id),
            ('booking_status', 'not in', ['cancelled', 'draft']),
            '|',
            '&', ('start_date', '<=', self.start_date), ('end_date', '>', self.start_date),
            '&', ('start_date', '<', self.end_date), ('end_date', '>=', self.end_date),
        ])
        
        if conflicting:
            raise exceptions.ValidationError(
                'This boat is already booked for the selected dates.'
            )
