from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class BoatBooking(models.Model):
    _name = "boat.booking"
    _description = "Boat Booking"
    _order = "create_date desc"

    boat_id = fields.Many2one('boat.boat', required=True, index=True)
    owner_id = fields.Many2one(related='boat_id.owner_id', store=True)
    guest_id = fields.Many2one('res.users', required=True, index=True)
    region_id = fields.Many2one(related='boat_id.region_id', store=True)

    date_from = fields.Datetime(required=True)
    date_to   = fields.Datetime(required=True)
    duration_hours = fields.Float(compute='_compute_duration', store=True)
    guest_count = fields.Integer(required=True, default=2)

    pricing_period = fields.Selection(related='boat_id.pricing_period', store=True)
    currency_id = fields.Many2one(related='boat_id.currency_id', store=True)

    price_base = fields.Monetary()
    price_extra_guest = fields.Monetary()
    tax_amount = fields.Monetary()
    price_total = fields.Monetary()

    advance_percent = fields.Float()
    advance_amount = fields.Monetary()
    balance_amount = fields.Monetary()

    payment_tx_id = fields.Many2one('payment.transaction')
    payment_status = fields.Selection([
        ('pending','Pending'), ('authorized','Authorized'),
        ('paid','Paid'), ('failed','Failed'), ('refunded','Refunded')
    ], default='pending')

    state = fields.Selection([
        ('draft','Draft'), ('pending_payment','Pending Payment'),
        ('confirmed','Confirmed'), ('cancel_requested','Cancel Requested'),
        ('cancelled','Cancelled'), ('refunded','Refunded')
    ], default='draft', index=True)

    policy_cutoff_days = fields.Integer(default=2)
    policy_fee_percent = fields.Float(default=10.0)

    @api.depends('date_from','date_to')
    def _compute_duration(self):
        for r in self:
            if r.date_from and r.date_to:
                delta = fields.Datetime.to_datetime(r.date_to) - fields.Datetime.to_datetime(r.date_from)
                r.duration_hours = delta.total_seconds() / 3600.0
            else:
                r.duration_hours = 0.0

    @api.constrains('date_from','date_to')
    def _check_dates(self):
        for r in self:
            if r.date_to and r.date_from and r.date_to <= r.date_from:
                raise ValidationError(_("End must be after start."))

    @api.constrains('boat_id','date_from','date_to','state')
    def _check_overlap(self):
        for r in self:
            if not r.boat_id or not r.date_from or not r.date_to:
                continue
            domain = [
                ('id','!=', r.id),
                ('boat_id','=', r.boat_id.id),
                ('state','in', ['pending_payment','confirmed']),
                ('date_from','<', r.date_to),
                ('date_to','>', r.date_from),
            ]
            if self.search_count(domain):
                raise ValidationError(_("Boat is already booked for the selected time range."))

    def compute_pricing(self):
        self.ensure_one()
        boat = self.boat_id
        hrs = self.duration_hours
        guests = self.guest_count
        base = 0
        if boat.pricing_period == 'hour_pp':
            base = boat.price_rent * hrs * guests
        elif boat.pricing_period == 'day_pp':
            days = max(1, int((hrs + 23)//24))
            base = boat.price_rent * days * guests
        else:  # day_boat
            days = max(1, int((hrs + 23)//24))
            base = boat.price_rent * days
        extra = 0
        if guests > boat.guest_capacity and boat.price_extra_guest:
            extra = (guests - boat.guest_capacity) * boat.price_extra_guest
        tax_percent = float(self.env['ir.config_parameter'].sudo().get_param('boat.tax_percent', '0'))
        tax = (base + extra) * tax_percent / 100.0
        total = base + extra + tax
        adv_pct = boat.price_advance_percent
        adv_amt = total * adv_pct / 100.0
        self.update({
            'price_base': base,
            'price_extra_guest': extra,
            'tax_amount': tax,
            'price_total': total,
            'advance_percent': adv_pct,
            'advance_amount': adv_amt,
            'balance_amount': total - adv_amt,
        })
