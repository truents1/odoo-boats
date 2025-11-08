from odoo import models, fields, api


class ResPartner(models.Model):
    """Extend res.partner to add boat owner and guest functionality"""
    _inherit = 'res.partner'
    
    # Boat-related fields
    is_boat_owner = fields.Boolean('Is Boat Owner', default=False, help="Check if this partner owns boats")
    is_boat_guest = fields.Boolean('Is Boat Guest', default=False, help="Check if this partner can book boats")
    
    # Boat Owner fields
    boat_ids = fields.One2many('boat.boat', 'owner_id', 'Owned Boats')
    boat_count = fields.Integer('Number of Boats', compute='_compute_boat_count', store=True)
    owner_commission_rate = fields.Float('Commission Rate (%)', default=15.0, help="Commission percentage for this owner")
    
    # Statistics
    total_bookings = fields.Integer('Total Bookings', compute='_compute_booking_stats', store=True)
    total_revenue = fields.Float('Total Revenue', compute='_compute_booking_stats', store=True)

    @api.depends('boat_ids')
    def _compute_boat_count(self):
        """Count boats owned by this partner"""
        for partner in self:
            partner.boat_count = len(partner.boat_ids)

    def _compute_booking_stats(self):
        """Compute booking statistics - placeholder for future booking module"""
        for partner in self:
            # These will be computed from bookings once booking module is added
            partner.total_bookings = 0
            partner.total_revenue = 0.0

    def action_view_boats(self):
        """View boats owned by this partner"""
        self.ensure_one()
        return {
            'name': f'{self.name} - Boats',
            'type': 'ir.actions.act_window',
            'res_model': 'boat.boat',
            'view_mode': 'kanban,tree,form',
            'domain': [('owner_id', '=', self.id)],
            'context': {
                'default_owner_id': self.id,
            },
        }