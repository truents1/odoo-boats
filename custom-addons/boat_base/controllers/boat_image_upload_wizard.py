from odoo import models, fields, api, _


class BoatImageUploadWizard(models.TransientModel):
    _name = 'boat.image.upload.wizard'
    _description = 'Multi-Image Upload Wizard'

    boat_id = fields.Many2one('boat.boat', 'Boat', required=True, readonly=True)
    
    # Multiple image fields for quick upload
    image_1 = fields.Image('Image 1', max_width=1920, max_height=1920)
    image_2 = fields.Image('Image 2', max_width=1920, max_height=1920)
    image_3 = fields.Image('Image 3', max_width=1920, max_height=1920)
    image_4 = fields.Image('Image 4', max_width=1920, max_height=1920)
    image_5 = fields.Image('Image 5', max_width=1920, max_height=1920)
    image_6 = fields.Image('Image 6', max_width=1920, max_height=1920)
    
    def action_upload_images(self):
        """Create boat.image records for all uploaded images"""
        self.ensure_one()
        
        image_fields = ['image_1', 'image_2', 'image_3', 'image_4', 'image_5', 'image_6']
        images_created = 0
        
        for field_name in image_fields:
            image_data = self[field_name]
            if image_data:
                self.env['boat.image'].create({
                    'boat_id': self.boat_id.id,
                    'image_1920': image_data,
                })
                images_created += 1
        
        if images_created > 0:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success!'),
                    'message': _('%s image(s) uploaded successfully') % images_created,
                    'type': 'success',
                    'sticky': False,
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Images'),
                    'message': _('Please select at least one image to upload'),
                    'type': 'warning',
                    'sticky': False,
                }
            }