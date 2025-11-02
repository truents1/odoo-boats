from odoo import models, fields

class BoatImageUploadWizard(models.TransientModel):
    _name = "boat.image.upload.wizard"
    _description = "Boat Image Upload Wizard"

    image = fields.Binary(required=True)
    boat_id = fields.Many2one('boat.boat', required=True)

    def action_upload(self):
        self.ensure_one()
        self.env['boat.image'].create({'boat_id': self.boat_id.id, 'image': self.image})
        return {'type': 'ir.actions.act_window_close'}