from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    is_boat_owner = fields.Boolean('Is Boat Owner', default=False)
    is_boat_guest = fields.Boolean('Is Boat Guest', default=False)
    
    # Boat Owner fields
    boat_ids = fields.One2many('boat.boat', 'owner_id', 'Owned Boats')
    boat_count = fields.Integer('Number of Boats', compute='_compute_boat_count')
    owner_commission_rate = fields.Float('Commission Rate (%)', default=0.0)
    
    @api.depends('boat_ids')
    def _compute_boat_count(self):
        for partner in self:
            partner.boat_count = len(partner.boat_ids)