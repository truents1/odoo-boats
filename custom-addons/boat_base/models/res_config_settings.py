from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    # Commission Settings
    default_commission_rate = fields.Float(
        'Default Commission Rate (%)',
        related='company_id.default_commission_rate',
        readonly=False
    )
    default_booking_advance = fields.Float(
        'Default Booking Advance (%)',
        related='company_id.default_booking_advance',
        readonly=False
    )
    
    # Booking Rules
    cancellation_days = fields.Integer(
        'Cancellation Days Before Travel',
        related='company_id.cancellation_days',
        readonly=False
    )
    min_advance_booking_hours = fields.Integer(
        'Minimum Advance Booking (Hours)',
        related='company_id.min_advance_booking_hours',
        readonly=False
    )