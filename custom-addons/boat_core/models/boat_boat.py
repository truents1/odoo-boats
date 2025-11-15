# boat_core/models/boat_boat.py
from odoo import api, fields, models

class BoatBoat(models.Model):
    _name = 'boat.boat'
    _description = 'Boat'

    name = fields.Char(required=True)  # Boat Name
    brand_name = fields.Char()  # Business/Brand Name
    registration_no = fields.Char()
    category_id = fields.Many2one('boat.category', string='Category', ondelete='restrict')
    year_built = fields.Integer()
    year_renovated = fields.Integer()
    build_type_id = fields.Many2one('boat.build.type', string='Boat Build Type', ondelete='restrict')
    decks = fields.Integer(string='Number of Decks')
    guest_capacity = fields.Integer()
    bedrooms = fields.Integer()
    bathrooms = fields.Integer()
    onboat_staff = fields.Integer()
    description_html = fields.Html(string='Description')
    video_url = fields.Char()
    website_url = fields.Char()
    active_service = fields.Boolean(string='Active in Service', default=True)

    image_ids = fields.One2many('boat.image', 'boat_id', string='Images')
    featured_image_id = fields.Many2one('boat.image', compute='_compute_featured', store=True)

    owner_partner_id = fields.Many2one('res.partner', string='Owner', index=True)
    state = fields.Selection([('draft','Draft'),('published','Published')], default='draft')

    @api.depends('image_ids.is_featured')
    def _compute_featured(self):
        for rec in self:
            rec.featured_image_id = next((img for img in rec.image_ids if img.is_featured), False)

class BoatImage(models.Model):
    _name = 'boat.image'
    _description = 'Boat Image'
    _order = 'sequence, id'

    boat_id = fields.Many2one('boat.boat', required=True, ondelete='cascade')
    name = fields.Char()
    image_1920 = fields.Image(max_width=1920, max_height=1920, verify_resolution=False)
    sequence = fields.Integer(default=10)
    is_featured = fields.Boolean(default=False)

class BoatCategory(models.Model):
    _name = 'boat.category'
    _description = 'Boat Category'
    name = fields.Char(required=True)

class BoatBuildType(models.Model):
    _name = 'boat.build.type'
    _description = 'Boat Build Type'
    name = fields.Char(required=True)
