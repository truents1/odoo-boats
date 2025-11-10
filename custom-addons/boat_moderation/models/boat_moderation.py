from odoo import models, fields

class BoatModeration(models.Model):
    _name = 'boat.moderation'
    _description = 'Boat Moderation'

    # Define your fields here
    name = fields.Char(string='Name')
    # Add other fields as necessary