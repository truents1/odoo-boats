from odoo import models, fields, api
from odoo.exceptions import ValidationError


class BoatImage(models.Model):
    """Model to handle multiple images for boats with featured image support"""
    _name = 'boat.image'
    _description = 'Boat Images'
    _order = 'sequence, id'

    name = fields.Char('Image Name', compute='_compute_name', store=True)
    sequence = fields.Integer('Sequence', default=10, help="Display order of images")
    boat_id = fields.Many2one('boat.boat', 'Boat', required=True, ondelete='cascade')
    image_1920 = fields.Image('Image', required=True, max_width=1920, max_height=1920)
    image_512 = fields.Image('Medium Image', related='image_1920', max_width=512, max_height=512, store=True)
    image_256 = fields.Image('Small Image', related='image_1920', max_width=256, max_height=256, store=True)
    image_128 = fields.Image('Thumbnail', related='image_1920', max_width=128, max_height=128, store=True)
    is_featured = fields.Boolean('Featured Image', default=False, help="Set as the main image for this boat")

    @api.depends('boat_id.name')
    def _compute_name(self):
        """Generate a descriptive name for the image"""
        for image in self:
            if image.boat_id:
                image.name = f"{image.boat_id.name} - Image {image.sequence}"
            else:
                image.name = f"Image {image.sequence}"

    @api.constrains('is_featured', 'boat_id')
    def _check_featured_image(self):
        """Ensure only one featured image per boat"""
        for image in self:
            if image.is_featured:
                other_featured = self.search([
                    ('boat_id', '=', image.boat_id.id),
                    ('is_featured', '=', True),
                    ('id', '!=', image.id)
                ])
                if other_featured:
                    # Automatically unset other featured images
                    other_featured.write({'is_featured': False})

    def action_set_featured(self):
        """Set this image as the featured image and update boat's main image"""
        self.ensure_one()
        # Unset all other featured images for this boat
        self.search([
            ('boat_id', '=', self.boat_id.id),
            ('id', '!=', self.id)
        ]).write({'is_featured': False})
        
        # Set this as featured
        self.write({'is_featured': True})
        
        # Update the boat's main image
        self.boat_id.write({
            'image_1920': self.image_1920,
        })
        
        return True

    def action_remove_featured(self):
        """Remove featured status from this image"""
        self.ensure_one()
        self.write({'is_featured': False})
        return True

    @api.model_create_multi
    def create(self, vals_list):
        """When creating images, auto-set first one as featured if none exists"""
        records = super().create(vals_list)
        for record in records:
            if record.boat_id:
                # Check if boat has any featured image
                has_featured = self.search_count([
                    ('boat_id', '=', record.boat_id.id),
                    ('is_featured', '=', True)
                ])
                # If no featured image exists, make this one featured
                if not has_featured:
                    record.action_set_featured()
        return records