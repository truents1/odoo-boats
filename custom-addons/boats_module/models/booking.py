# -*- coding: utf-8 -*-
# Booking model will go here
from odoo import models, fields, api, exceptions
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class BoatBooking(models.Model):
    """Booking records for boat rentals"""
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
    base_amount = fields.Float(string='Base Amount', compute='_compute_amounts', store=True)
    extra_guest_amount = fields.Float(string='Extra Guest Charge', compute='_compute_amounts', store=True)
    subtotal = fields.Float(string='Subtotal', compute='_compute_amounts', store=True)
    booking_amount = fields.Float(string='Booking Amount (Advance)', compute='_compute_amounts', store=True)
    tax_amount = fields.Float(string='Tax Amount', compute='_compute_amounts', store=True)
    total_amount = fields.Float(string='Total Amount', compute='_compute_amounts', store=True)
    net_payable = fields.Float(string='Net Payable Now', compute='_compute_amounts', store=True)
    
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
    refund_processed = fields.Boolean(string='Refund Processed', default=False)
    
    # Computed
    can_cancel = fields.Boolean(compute='_compute_can_cancel', string='Can Cancel')
    
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
    
    @api.depends('boat_id', 'duration_hours', 'num_guests')
    def _compute_amounts(self):
        for booking in self:
            if not booking.boat_id:
                booking.base_amount = 0.0
                booking.extra_guest_amount = 0.0
                booking.subtotal = 0.0
                booking.booking_amount = 0.0
                booking.tax_amount = 0.0
                booking.total_amount = 0.0
                booking.net_payable = 0.0
                continue
            
            boat = booking.boat_id
            
            # Calculate base amount
            if boat.pricing_period in ['hourly_person', 'daily_person']:
                units = booking.duration_hours if 'hourly' in boat.pricing_period else booking.duration_hours / 24
                booking.base_amount = units * boat.rent_amount * booking.num_guests
            else:
                units = booking.duration_hours if 'hourly' in boat.pricing_period else booking.duration_hours / 24
                booking.base_amount = units * boat.rent_amount
            
            # Extra guest charges
            if booking.num_guests > boat.guest_capacity:
                extra_guests = booking.num_guests - boat.guest_capacity
                booking.extra_guest_amount = extra_guests * boat.extra_guest_charge
            else:
                booking.extra_guest_amount = 0.0
            
            booking.subtotal = booking.base_amount + booking.extra_guest_amount
            
            # Advance payment (configurable %)
            booking.booking_amount = booking.subtotal * (boat.advance_payment_percent / 100)
            
            # Tax (example: 18% GST for India)
            tax_rate = 0.18  # This should be configurable
            booking.tax_amount = booking.booking_amount * tax_rate
            
            booking.total_amount = booking.booking_amount + booking.tax_amount
            booking.net_payable = booking.total_amount
    
    @api.depends('start_date', 'booking_status')
    def _compute_can_cancel(self):
        """Allow cancellation up to 2 days before booking"""
        for booking in self:
            if booking.booking_status in ['cancelled', 'completed']:
                booking.can_cancel = False
            elif booking.start_date:
                two_days_before = booking.start_date - timedelta(days=2)
                booking.can_cancel = datetime.now() <= two_days_before
            else:
                booking.can_cancel = False
    
    @api.constrains('start_date', 'end_date', 'num_guests')
    def _check_booking_validity(self):
        """Validate booking constraints"""
        for booking in self:
            if booking.start_date >= booking.end_date:
                raise exceptions.ValidationError('End date must be after start date.')
            
            if booking.boat_id:
                if booking.duration_hours < booking.boat_id.min_booking_hours:
                    raise exceptions.ValidationError(
                        f'Minimum booking duration is {booking.boat_id.min_booking_hours} hours.'
                    )
                
                if booking.duration_hours > booking.boat_id.max_booking_hours:
                    raise exceptions.ValidationError(
                        f'Maximum booking duration is {booking.boat_id.max_booking_hours} hours.'
                    )
                
                # Check advance notice
                notice_required = booking.boat_id.advance_notice_hours
                hours_until_booking = (booking.start_date - datetime.now()).total_seconds() / 3600
                if hours_until_booking < notice_required:
                    raise exceptions.ValidationError(
                        f'Bookings require at least {notice_required} hours advance notice.'
                    )
    
    def check_availability(self):
        """Check for conflicting bookings"""
        self.ensure_one()
        conflicting = self.search([
            ('boat_id', '=', self.boat_id.id),
            ('id', '!=', self.id),
            ('booking_status', 'not in', ['cancelled', 'draft']),
            '|',
            '&', ('start_date', '<=', self.start_date), ('end_date', '>', self.start_date),
            '&', ('start_date', '=', self.end_date),
        ])
        
        if conflicting:
            raise exceptions.ValidationError(
                'This boat is already booked for the selected dates. Please choose different dates.'
            )
    
    def action_confirm_booking(self):
        """Confirm booking after payment"""
        self.ensure_one()
        self.check_availability()
        self.booking_status = 'confirmed'
        self.payment_status = 'paid'
        self._send_confirmation_email()
    
    def action_cancel_booking(self):
        """Initiate cancellation with refund calculation"""
        self.ensure_one()
        if not self.can_cancel:
            raise exceptions.UserError('This booking cannot be cancelled.')
        
        # Calculate refund (90% refund, 10% handling fee)
        self.refund_amount = self.paid_amount * 0.9
        self.is_cancelled = True
        self.cancellation_date = datetime.now()
        self.booking_status = 'cancelled'
        
        # Notify admin for refund processing
        self._notify_cancellation()
    
    def _send_confirmation_email(self):
        template = self.env.ref('odoo_boats.email_template_booking_confirmation')
        template.send_mail(self.id)
    
    def _notify_cancellation(self):
        template = self.env.ref('odoo_boats.email_template_booking_cancelled')
        template.send_mail(self.id)

class BoatReview(models.Model):
    """Guest reviews for boats"""
    _name = 'boat.review'
    _description = 'Boat Review'
    _order = 'create_date desc'
    
    boat_id = fields.Many2one('boat.listing', string='Boat', required=True, ondelete='cascade')
    booking_id = fields.Many2one('boat.booking', string='Booking', required=True)
    guest_id = fields.Many2one('res.users', string='Guest', required=True)
    
    rating = fields.Integer(string='Rating', required=True)
    title = fields.Char(string='Review Title')
    review_text = fields.Text(string='Review')
    
    is_moderated = fields.Boolean(string='Moderated', default=False)
    is_published = fields.Boolean(string='Published', default=False)
    
    @api.constrains('rating')
    def _check_rating(self):
        for review in self:
            if not (1 <= review.rating <= 5):
                raise exceptions.ValidationError('Rating must be between 1 and 5 stars.')
