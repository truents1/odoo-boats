# custom/boat_core/models/boat_image.py
from odoo import models, fields

class BoatImage(models.Model):
    _name = 'boat.image'
    _description = 'Boat Image'
    _order = 'sequence,id'

    boat_id = fields.Many2one('boat.boat', required=True, ondelete='cascade', index=True)
    image = fields.Binary(attachment=True, required=True)
    name = fields.Char()
    sequence = fields.Integer(default=10)
