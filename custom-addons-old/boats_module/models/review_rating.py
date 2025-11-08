from odoo import models, fields, api, exceptions

class BoatReview(models.Model):
    """Guest reviews for boats - MINIMAL VERSION"""
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