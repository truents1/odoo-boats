# -*- coding: utf-8 -*-
# Master data models will go here
from odoo import models, fields, api

class BoatRegion(models.Model):
    """Geographic locations where boats operate"""
    _name = 'boat.region'
    _description = 'Boat Operating Regions'
    _order = 'name'
    
    name = fields.Char(string='Region Name', required=True)
    description = fields.Text(string='Region Description')
    image_ids = fields.Many2many('ir.attachment', string='Region Images')
    latitude = fields.Float(string='Latitude', digits=(10, 7))
    longitude = fields.Float(string='Longitude', digits=(10, 7))
    state = fields.Char(string='State/Province')
    country_id = fields.Many2one('res.country', string='Country', required=True)
    active = fields.Boolean(default=True)
    boat_count = fields.Integer(compute='_compute_boat_count', string='Number of Boats')
    
    @api.depends('boat_listing_ids')
    def _compute_boat_count(self):
        for region in self:
            region.boat_count = len(region.boat_listing_ids)
    
    boat_listing_ids = fields.One2many('boat.listing', 'region_id', string='Boats')

class BoatCategory(models.Model):
    """Types of boats (Houseboat, Yacht, Cruise, etc.)"""
    _name = 'boat.category'
    _description = 'Boat Categories'
    _order = 'sequence, name'
    
    name = fields.Char(string='Category Name', required=True)
    description = fields.Text(string='Category Description')
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    image = fields.Image(string='Category Icon')

class GenericMaster(models.Model):
    """Flexible master data for all dropdowns and checkboxes"""
    _name = 'boat.generic.master'
    _description = 'Generic Master Data'
    _order = 'master_type, sequence, name'
    
    MASTER_TYPES = [
        ('build_type', 'Boat Build Type'),
        ('amenity', 'Amenity'),
        ('meal_type', 'Meal Type'),
        ('cuisine', 'Cuisine Type'),
        ('safety_item', 'Safety Checklist Item'),
        ('activity', 'Activity'),
        ('addon', 'Paid Add-on'),
        ('currency', 'Currency'),
    ]
    
    name = fields.Char(string='Name', required=True)
    master_type = fields.Selection(MASTER_TYPES, string='Master Type', required=True, index=True)
    description = fields.Text(string='Description')
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    icon = fields.Char(string='Icon Class') 
    