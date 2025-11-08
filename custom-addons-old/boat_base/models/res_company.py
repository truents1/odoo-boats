from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'
    
    # Boat Management Settings
    default_commission_rate = fields.Float('Default Commission Rate (%)', default=15.0)
    default_booking_advance = fields.Float('Default Booking Advance (%)', default=30.0)
    cancellation_days = fields.Integer('Cancellation Days Before Travel', default=7)
    min_advance_booking_hours = fields.Integer('Minimum Advance Booking (Hours)', default=48)
