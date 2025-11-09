from odoo import http
from odoo.http import request

class OwnerPortal(http.Controller):

    @http.route(['/owner/boats/new'], type='http', auth='user', website=True, csrf=True)
    def owner_boat_new_form(self, **kw):
        vals = {
            'categories': request.env['boat.category'].sudo().search([]),
            'regions': request.env['boat.region'].sudo().search([]),
        }
        return request.render('boat_guest_portal.owner_boat_form', vals)

    @http.route(['/owner/boats/create'], type='http', auth='user', methods=['POST'], website=True, csrf=True)
    def owner_boat_create(self, **post):
        # sanitize and map fields
        partner = request.env.user.partner_id
        env = request.env
        def _int(v): return int(v) if v and v.isdigit() else 0
        def _float(v):
            try: return float(v or 0)
            except: return 0.0

        create_vals = {
            'name': post.get('name'),
            'category_id': int(post.get('category_id') or 0) or False,
            'region_id': int(post.get('region_id') or 0) or False,
            'guest_capacity': _int(post.get('guest_capacity')),
            'rent_amount': _float(post.get('rent_amount')),
            'pricing_period': post.get('pricing_period') or 'flat_day',
            'description': post.get('description'),
            'owner_partner_id': partner.id,
            'moderation_state': 'submitted',
        }
        # create as sudo so portal can submit even if model perms are tight
        boat = env['boat.boat'].sudo().create(create_vals)

        # optional featured image via file input named 'image'
        upload = request.httprequest.files.get('image')
        if upload and upload.filename:
            attachment = request.env['ir.attachment'].sudo().create({
                'name': upload.filename,
                'datas': upload.read().encode('base64') if hasattr(bytes, 'encode') else upload.read(),
                'res_model': 'boat.boat',
                'res_id': boat.id,
                'mimetype': upload.mimetype,
            })
            # if you have boat.image model, link it here instead

        return request.redirect('/owner/boats/thanks')

    @http.route(['/owner/boats/thanks'], type='http', auth='user', website=True)
    def owner_boat_thanks(self, **kw):
        return request.render('boat_guest_portal.owner_boat_thanks', {})
