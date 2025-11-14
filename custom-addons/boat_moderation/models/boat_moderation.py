# custom/boat_moderation/models/boat_moderation.py
from odoo import models, fields

class BoatModeration(models.Model):
    _name = 'boat.moderation'
    _description = 'Boat Moderation'

    name = fields.Char(required=True, default="Moderation")
    state = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], default='pending')
