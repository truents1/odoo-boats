from odoo import api, fields, models

class BoatReview(models.Model):
    _name = "boat.review"
    _description = "Boat Review"
    _order = "create_date desc"

    boat_id = fields.Many2one('boat.boat', required=True, index=True)
    booking_id = fields.Many2one('boat.booking', index=True)
    user_id = fields.Many2one('res.users', required=True, index=True)
    rating_overall = fields.Integer(required=True, default=5)
    title = fields.Char()
    body = fields.Text()
    state = fields.Selection([('pending','Pending'),('published','Published'),('rejected','Rejected')], default='pending')
    helpful_votes = fields.Integer(default=0)
    report_count = fields.Integer(default=0)
