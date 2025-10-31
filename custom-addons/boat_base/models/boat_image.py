from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class BoatImage(models.Model):
    _name = 'boat.image'
    _description = 'Boat Image'
    _order = 'sequence, id'

    name = fields.Char('Image Title', required=True)
    sequence = fields.Integer('Sequence', default=10)
    boat_id = fields.Many2one('boat.boat', 'Boat', required=True, ondelete='cascade')
    image_1920 = fields.Image('Image', required=True, max_width=1920, max_height=1920)
    image_512 = fields.Image('Image 512', related='image_1920', max_width=512, max_height=512, store=True)
    image_256 = fields.Image('Image 256', related='image_1920', max_width=256, max_height=256, store=True)
    image_128 = fields.Image('Image 128', related='image_1920', max_width=128, max_height=128, store=True)
    is_featured = fields.Boolean('Featured Image', default=False)
    
    @api.model_create_multi
    def create(self, vals_list):
        """Auto-set first image as featured if no featured image exists"""
        records = super().create(vals_list)
        for record in records:
            if record.boat_id and not record.boat_id.image_ids.filtered('is_featured'):
                record.is_featured = True
        return records
    
    def write(self, vals):
        """Ensure only one featured image per boat"""
        if vals.get('is_featured'):
            for record in self:
                # Unset other featured images for the same boat
                other_featured = record.boat_id.image_ids.filtered(
                    lambda img: img.is_featured and img.id != record.id
                )
                if other_featured:
                    other_featured.write({'is_featured': False})
        return super().write(vals)
    
    def action_set_featured(self):
        """Button action to set as featured image"""
        self.ensure_one()
        self.write({'is_featured': True})
        return True