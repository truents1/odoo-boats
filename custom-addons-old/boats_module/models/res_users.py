# -*- coding: utf-8 -*-
from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'
    
    boat_listing_ids = fields.One2many('boat.listing', 'owner_id', string='My Boats')
