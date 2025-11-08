# -*- coding: utf-8 -*-
from odoo import models, fields

class BoatListing(models.Model):
    _name = 'boat.listing'
    _description = 'Boat Listing'
    
    name = fields.Char(string='Boat Name', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)
