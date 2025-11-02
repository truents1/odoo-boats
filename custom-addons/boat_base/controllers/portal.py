from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError
from odoo.tools import groupby as groupbyelem
from operator import itemgetter


class BoatPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        """Add boat count to portal home"""
        values = super()._prepare_home_portal_values(counters)
        if 'boat_count' in counters:
            boat_count = request.env['boat.boat'].search_count([
                ('owner_id', '=', request.env.user.partner_id.id)
            ])
            values['boat_count'] = boat_count
        return values

    @http.route(['/my/boats', '/my/boats/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_boats(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        """List user's boats in portal"""
        values = self._prepare_portal_layout_values()
        BoatBoat = request.env['boat.boat']
        
        domain = [('owner_id', '=', request.env.user.partner_id.id)]

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
            'state': {'label': _('Status'), 'order': 'state'},
        }
        
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'draft': {'label': _('Draft'), 'domain': [('state', '=', 'draft')]},
            'submitted': {'label': _('Submitted'), 'domain': [('state', '=', 'submitted')]},
            'approved': {'label': _('Approved'), 'domain': [('state', 'in', ['approved', 'published'])]},
        }

        # Default sort by date
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # Default filter by all
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        # Count for pager
        boat_count = BoatBoat.search_count(domain)
        
        # Pager
        pager = portal_pager(
            url="/my/boats",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby},
            total=boat_count,
            page=page,
            step=self._items_per_page
        )

        # Content according to pager and archive selected
        boats = BoatBoat.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        
        values.update({
            'boats': boats,
            'page_name': 'boat',
            'default_url': '/my/boats',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': searchbar_filters,
            'filterby': filterby,
        })
        
        return request.render("boat_base.portal_my_boats", values)

    @http.route(['/my/boats/<int:boat_id>'], type='http', auth="user", website=True)
    def portal_my_boat(self, boat_id=None, access_token=None, **kw):
        """Display a specific boat"""
        try:
            boat_sudo = self._document_check_access('boat.boat', boat_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = {
            'boat': boat_sudo,
            'page_name': 'boat',
        }
        return request.render("boat_base.portal_my_boat", values)

    @http.route(['/my/boats/new'], type='http', auth="user", website=True)
    def portal_boat_new(self, **kw):
        """Create new boat form"""
        values = self._prepare_boat_form_values()
        return request.render("boat_base.portal_boat_form", values)

    @http.route(['/my/boats/<int:boat_id>/edit'], type='http', auth="user", website=True)
    def portal_boat_edit(self, boat_id=None, **kw):
        """Edit existing boat form"""
        try:
            boat_sudo = self._document_check_access('boat.boat', boat_id)
        except (AccessError, MissingError):
            return request.redirect('/my/boats')

        # Only allow editing if boat is in draft or rejected state
        if boat_sudo.state not in ['draft', 'rejected']:
            return request.redirect(f'/my/boats/{boat_id}')

        values = self._prepare_boat_form_values(boat=boat_sudo)
        return request.render("boat_base.portal_boat_form", values)

    @http.route(['/my/boats/save'], type='http', auth="user", website=True, methods=['POST'], csrf=True)
    def portal_boat_save(self, **post):
        """Save boat data from portal form"""
        BoatBoat = request.env['boat.boat']
        
        # Prepare values
        values = {
            'name': post.get('name'),
            'category_id': int(post.get('category_id')) if post.get('category_id') else False,
            'location_id': int(post.get('location_id')) if post.get('location_id') else False,
            'guest_capacity': int(post.get('guest_capacity', 1)),
            'sleeping_capacity': int(post.get('sleeping_capacity', 1)),
            'num_bedrooms': int(post.get('num_bedrooms', 0)),
            'num_bathrooms': int(post.get('num_bathrooms', 0)),
            'length': float(post.get('length', 0)) if post.get('length') else False,
            'year_built': int(post.get('year_built')) if post.get('year_built') else False,
            'engine_type': post.get('engine_type'),
            'fuel_capacity': float(post.get('fuel_capacity', 0)) if post.get('fuel_capacity') else False,
            'max_speed': float(post.get('max_speed', 0)) if post.get('max_speed') else False,
            'base_price_per_day': float(post.get('base_price_per_day', 0)),
            'description': post.get('description'),
            'owner_id': request.env.user.partner_id.id,
        }

        # Handle amenities (many2many)
        if post.get('feature_ids'):
            feature_ids = [int(fid) for fid in post.getlist('feature_ids')]
            values['feature_ids'] = [(6, 0, feature_ids)]

        boat_id = post.get('boat_id')
        if boat_id:
            # Update existing boat
            boat = BoatBoat.browse(int(boat_id))
            if boat.owner_id.id == request.env.user.partner_id.id:
                boat.write(values)
        else:
            # Create new boat
            boat = BoatBoat.create(values)
            boat_id = boat.id

        # Handle image upload
if post.get('image_1920'):
    try:
        boat.image_1920 = post.get('image_1920')
    except Exception as e:
        _logger.error(f"Image upload failed: {str(e)}")

    return request.redirect(f'/my/boats/{boat_id}')

    @http.route(['/my/boats/<int:boat_id>/submit'], type='http', auth="user", website=True, methods=['POST'])
    def portal_boat_submit(self, boat_id=None, **kw):
        """Submit boat for review"""
        try:
            boat_sudo = self._document_check_access('boat.boat', boat_id)
        except (AccessError, MissingError):
            return request.redirect('/my/boats')

        if boat_sudo.owner_id.id == request.env.user.partner_id.id:
            boat_sudo.action_submit()

        return request.redirect(f'/my/boats/{boat_id}')

    def _prepare_boat_form_values(self, boat=None):
        """Prepare values for boat form"""
        categories = request.env['boat.category'].sudo().search([])
        locations = request.env['boat.location'].sudo().search([('active', '=', True)])
        amenities = request.env['boat.amenity'].sudo().search([])

        values = {
            'boat': boat,
            'categories': categories,
            'locations': locations,
            'amenities': amenities,
            'page_name': 'boat_form',
        }
        return values


class BoatWebsite(http.Controller):
    """Public website controller for boat listings"""

    @http.route(['/boats', '/boats/page/<int:page>'], type='http', auth="public", website=True)
    def boats_list(self, page=1, category=None, location=None, search=None, **kwargs):
        """Public boat listing page"""
        BoatBoat = request.env['boat.boat']
        
        domain = [
            ('website_published', '=', True),
            ('state', '=', 'published')
        ]

        if category:
            domain.append(('category_id', '=', int(category)))
        
        if location:
            domain.append(('location_id', '=', int(location)))

        if search:
            domain.append(('name', 'ilike', search))

        # Count for pager
        boat_count = BoatBoat.sudo().search_count(domain)

        # Pager
        pager = portal_pager(
            url="/boats",
            total=boat_count,
            page=page,
            step=12,
            url_args={'category': category, 'location': location, 'search': search}
        )

        # Get boats
        boats = BoatBoat.sudo().search(
            domain,
            limit=12,
            offset=pager['offset'],
            order='create_date desc'
        )

        # Get filter options
        categories = request.env['boat.category'].sudo().search([])
        locations = request.env['boat.location'].sudo().search([('active', '=', True)])

        values = {
            'boats': boats,
            'pager': pager,
            'categories': categories,
            'locations': locations,
            'selected_category': int(category) if category else None,
            'selected_location': int(location) if location else None,
            'search': search or '',
        }

        return request.render("boat_base.boats_list", values)

    @http.route(['/boats/<int:boat_id>'], type='http', auth="public", website=True)
    def boat_detail(self, boat_id=None, **kwargs):
        """Public boat detail page"""
        boat = request.env['boat.boat'].sudo().browse(boat_id)

        if not boat.exists() or not boat.website_published:
            return request.redirect('/boats')

        values = {
            'boat': boat,
        }

        return request.render("boat_base.boat_detail", values)