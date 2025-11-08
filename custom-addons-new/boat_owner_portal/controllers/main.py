from odoo import http
from odoo.http import request

class BoatOwnerPortal(http.Controller):

    @http.route(['/owner/boats'], type='http', auth='user', website=True)
    def owner_boats(self, **kw):
        boats = request.env['boat.boat'].sudo().search([('owner_id','=', request.env.user.id)])
        return request.render('boat_owner_portal.owner_boats', {'boats': boats})

    @http.route(['/owner/boats/new'], type='http', auth='user', website=True)
    def owner_boats_new(self, **kw):
        return request.render('boat_owner_portal.owner_boat_form', {})

    @http.route(['/owner/boats/create'], type='json', auth='user')
    def owner_boats_create(self, **post):
        vals = {
            'owner_id': request.env.user.id,
            'name': post.get('name'),
            'category_id': int(post.get('category_id')) if post.get('category_id') else False,
            'region_id': int(post.get('region_id')) if post.get('region_id') else False,
            'guest_capacity': int(post.get('guest_capacity') or 2),
            'pricing_period': post.get('pricing_period') or 'day_boat',
            'price_rent': float(post.get('price_rent') or 0),
            'state': 'submitted',
        }
        boat = request.env['boat.boat'].sudo().create(vals)
        return {'ok': True, 'id': boat.id}
