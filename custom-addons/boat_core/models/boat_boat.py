from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Boat(models.Model):
    _name = "boat.boat"
    _description = "Boat"
    _rec_name = "name"
    _order = "create_date desc"
    _inherit = ["image.mixin"]

    website_published = fields.Boolean(string='Published on Website')
    owner_partner_id = fields.Many2one('res.partner', required=True, index=True)
    moderation_state = fields.Selection([
        ('draft','Draft'),('submitted','Submitted'),
        ('approved','Approved'),('rejected','Rejected')
    ], default='draft', index=True)

    active = fields.Boolean(default=True)
    owner_id = fields.Many2one("res.users", required=True, index=True)
    name = fields.Char(required=True)
    brand_name = fields.Char()
    registration_no = fields.Char()
    category_id = fields.Many2one("boat.category", required=True, index=True)
    year_built = fields.Integer()
    year_renovated = fields.Integer()
    build_type_id = fields.Many2one(
        "boat.option", domain=[("master_type", "=", "build_type")]
    )
    deck_count = fields.Integer()
    guest_capacity = fields.Integer(required=True, default=2)
    bedroom_count = fields.Integer()
    bathroom_count = fields.Integer()
    sleeping_capacity = fields.Integer(string="Sleeping Capacity", default=0)
    staff_count = fields.Integer()
    description_html = fields.Html()
    image_ids = fields.Many2many("ir.attachment", string="Images")
    featured_image_id = fields.Many2one("ir.attachment")
    video_url = fields.Char()
    website_url = fields.Char()
    active_service = fields.Boolean(default=True)

    region_id = fields.Many2one("boat.region", required=True)
    boarding_jetty = fields.Char()
    service_area = fields.Char()

    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id.id
    )
    pricing_period = fields.Selection(
        [
            ("hour_pp", "Hourly per person"),
            ("day_pp", "Daily per person"),
            ("day_boat", "Daily per boat"),
        ],
        required=True,
        default="day_boat",
    )
    price_rent = fields.Monetary(default=0.0)
    price_advance_percent = fields.Float(default=20.0)
    price_extra_guest = fields.Monetary(default=0.0)
    min_duration_hours = fields.Integer(default=2)
    max_duration_hours = fields.Integer(default=240)
    advance_notice_hours = fields.Integer(default=12)

    amenity_ids = fields.Many2many(
        "boat.option",
        "boat_amenity_rel",
        "boat_id",
        "option_id",
        string="Amenities",
        domain=[("master_type", "=", "amenity")],
    )
    meal_type_ids = fields.Many2many(
        "boat.option",
        "boat_meal_type_rel",
        "boat_id",
        "option_id",
        domain=[("master_type", "=", "meal_type")],
    )
    cuisine_type_ids = fields.Many2many(
        "boat.option",
        "boat_cuisine_type_rel",
        "boat_id",
        "option_id",
        domain=[("master_type", "=", "cuisine_type")],
    )
    included_meal_ids = fields.Many2many(
        "boat.option",
        "boat_included_meal_rel",
        "boat_id",
        "option_id",
        domain=[("master_type", "=", "included_meal")],
    )
    safety_check_ids = fields.Many2many(
        "boat.option",
        "boat_safety_check_rel",
        "boat_id",
        "option_id",
        domain=[("master_type", "=", "safety_check")],
    )
    included_activity_ids = fields.Many2many(
        "boat.option",
        "boat_included_activity_rel",
        "boat_id",
        "option_id",
        domain=[("master_type", "=", "activity")],
    )
    paid_addon_ids = fields.Many2many(
        "boat.option",
        "boat_paid_addon_rel",
        "boat_id",
        "option_id",
        domain=[("master_type", "=", "paid_addon")],
    )

    safety_cert_text = fields.Text()
    emergency_phone = fields.Char()
    is_certified = fields.Boolean()

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("archived", "Archived"),
        ],
        default="draft",
        index=True,
    )

    seo_title = fields.Char()
    seo_description = fields.Char()
    seo_keywords = fields.Char()

    rating_avg = fields.Float(digits=(2, 1))
    rating_count = fields.Integer()

    @api.constrains("price_advance_percent")
    def _check_advance(self):
        for rec in self:
            if rec.price_advance_percent < 0 or rec.price_advance_percent > 100:
                raise ValidationError(_("Advance %% must be 0..100"))

    @api.constrains("featured_image_id", "image_ids")
    def _check_feature_in_images(self):
        for rec in self:
            if rec.featured_image_id and rec.featured_image_id not in rec.image_ids:
                raise ValidationError(_("Featured image must be one of Images."))

    def action_submit(self):
        self.write({"state": "submitted"})

    def action_approve(self):
        self.write({"state": "approved"})

    def action_reject(self):
        self.write({"state": "rejected"})
