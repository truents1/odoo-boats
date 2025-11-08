from odoo import http
from odoo.http import request

class BoatWebsite(http.Controller):

    @http.route(['/boats'], type='http', auth='public', website=True)
    def boats(self, **kw):
        domain = [('state','=','approved')]
        if kw.get('region_id'):
            domain.append(('region_id','=', int(kw['region_id'])))
        if kw.get('category_id'):
            domain.append(('category_id','=', int(kw['category_id'])))
        boats = request.env['boat.boat'].sudo().search(domain, limit=24)
        return request.render('boat_guest_portal.boat_list', {'boats': boats, 'kw': kw})

    @http.route(['/boats/<model("boat.boat"):boat>'], type='http', auth='public', website=True)
    def boat_detail(self, boat, **kw):
        return request.render('boat_guest_portal.boat_detail', {'boat': boat})
