from odoo import api, fields, models, _

class Boat(models.Model):
    _inherit = "boat.boat"
    _description = "Boat moderation extension"

    # extend the existing selection; include ondelete as required by Odoo 17
    state = fields.Selection(
        selection_add=[
            ("under_review", "Under Review"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        ondelete={
            "under_review": "set default",
            "approved": "set default",
            "rejected": "set default",
        },
    )

    def action_submit_for_review(self):
        self.write({"state": "under_review"})
        return True

    def action_approve(self):
        self.write({"state": "approved", "is_published": True})
        return True

    def action_reject(self):
        self.write({"state": "rejected", "is_published": False})
        return True
