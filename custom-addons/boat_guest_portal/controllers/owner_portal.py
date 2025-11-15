# boat_guest_portal/controllers/boats.py
from odoo import http
from odoo.http import request

class BoatWebsite(http.Controller):

    @http.route('/boats/new', type='http', auth='user', website=True, csrf=True)
    def boats_new(self, **kw):
        # master data for dropdowns
        categories = request.env['boat.category'].sudo().search([])
        build_types = request.env['boat.build.type'].sudo().search([])
        return request.render('boat_guest_portal.boat_form', {
            'categories': categories,
            'build_types': build_types,
            'page_title': 'Add a Boat',
        })

    @http.route('/boats/submit', type='http', auth='user', methods=['POST'], website=True, csrf=True)
    def boats_submit(self, **post):
        vals = {
            'name': post.get('name'),
            'brand_name': post.get('brand_name') or False,
            'registration_no': post.get('registration_no') or False,
            'category_id': int(post['category_id']) if post.get('category_id') else False,
            'year_built': int(post['year_built']) if post.get('year_built') else False,
            'year_renovated': int(post['year_renovated']) if post.get('year_renovated') else False,
            'build_type_id': int(post['build_type_id']) if post.get('build_type_id') else False,
            'decks': int(post['decks']) if post.get('decks') else 0,
            'guest_capacity': int(post['guest_capacity']) if post.get('guest_capacity') else 0,
            'bedrooms': int(post['bedrooms']) if post.get('bedrooms') else 0,
            'bathrooms': int(post['bathrooms']) if post.get('bathrooms') else 0,
            'onboat_staff': int(post['onboat_staff']) if post.get('onboat_staff') else 0,
            'description_html': post.get('description_html') or False,
            'video_url': post.get('video_url') or False,
            'website_url': post.get('website_url') or False,
            'active_service': True if post.get('active_service') == 'on' else False,
            'owner_partner_id': request.env.user.partner_id.id,
            'state': 'draft',
        }
        boat = request.env['boat.boat'].sudo().create(vals)

        # handle uploaded images
        # expected inputs: images[] (multiple), featured_image_index (0-based)
        files = request.httprequest.files.getlist('images')
        featured_idx = int(post.get('featured_image_index')) if post.get('featured_image_index') else -1
        for idx, fs in enumerate(files):
            content = fs.read()
            request.env['boat.image'].sudo().create({
                'boat_id': boat.id,
                'name': fs.filename or 'image',
                'image_1920': content.encode('base64') if hasattr(content, 'encode') else content,
                'sequence': idx,
                'is_featured': (idx == featured_idx),
            })

        return request.redirect(f'/boats/{boat.id}')
