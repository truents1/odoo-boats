# -*- coding: utf-8 -*-
from odoo import models, fields

class BoatRegion(models.Model):
    _name = 'boat.region'
    _description = 'Boat Region'
    
    name = fields.Char(string='Region Name', required=True)
    country_id = fields.Many2one('res.country', string='Country')
    active = fields.Boolean(default=True)

class BoatCategory(models.Model):
    _name = 'boat.category'
    _description = 'Boat Category'
    
    name = fields.Char(string='Category Name', required=True)
    active = fields.Boolean(default=True)
