# -*- coding: utf-8 -*-
# Main website controller
from odoo import http
from odoo.http import request
import json

class BoatWebsiteController(http.Controller):
    
    @http.route(['/boats', '/boats/page/'], type='http', auth='public', website=True)
    def boat_search(self, page=1, **kwargs):
        """Public boat search and listing page"""
        
        # Build domain from filters
        domain = [('moderation_status', '=', 'approved'), ('active', '=', True')]
        
        # Region filter
        if kwargs.get('region_id'):
            domain.append(('region_id', '=', int(kwargs.get('region_id'))))
        
        # Guest capacity filter
        if kwargs.get('guests'):
            domain.append(('guest_capacity', '>=', int(kwargs.get('guests'))))
        
        # Price range filter
        if kwargs.get('price_min'):
            domain.append(('rent_amount', '>=', float(kwargs.get('price_min'))))
        if kwargs.get('price_max'):
            domain.append(('rent_amount', '<=', float(kwargs.get('price_max'))))
        
        # Amenity filters
        if kwargs.get('amenities'):
            amenity_ids = [int(a) for a in kwargs.get('amenities').split(',')]
            domain.append(('amenity_ids', 'in', amenity_ids))
        
        # Pagination
        boats_per_page = 12
        boat_count = request.env['boat.listing'].sudo().search_count(domain)
        pager = request.website.pager(
            url='/boats',
            total=boat_count,
            page=page,
            step=boats_per_page,
            url_args=kwargs
        )
        
        boats = request.env['boat.listing'].sudo().search(
            domain,
            limit=boats_per_page,
            offset=pager['offset'],
            order='average_rating desc, create_date desc'
        )
        
        # Get filter options
        regions = request.env['boat.region'].sudo().search([('active', '=', True)])
        amenities = request.env['boat.generic.master'].sudo().search([
            ('master_type', '=', 'amenity'),
            ('active', '=', True)
        ])
        
        values = {
            'boats': boats,
            'regions': regions,
            'amenities': amenities,
            'pager': pager,
            'search_params': kwargs,
        }
        
        return request.render('odoo_boats.boat_search_page', values)
    
    @http.route(['/boat/'], type='http', auth='public', website=True)
    def boat_detail(self, boat, **kwargs):
        """Boat detail page with all information"""
        
        if boat.moderation_status != 'approved' or not boat.active:
            return request.render('website.404')
        
        # Related boats (same region or category)
        related_boats = request.env['boat.listing'].sudo().search([
            ('id', '!=', boat.id),
            ('moderation_status', '=', 'approved'),
            ('active', '=', True),
            '|',
            ('region_id', '=', boat.region_id.id),
            ('category_id', '=', boat.category_id.id),
        ], limit=4, order='average_rating desc')
        
        # Reviews (published only)
        reviews = request.env['boat.review'].sudo().search([
            ('boat_id', '=', boat.id),
            ('is_published', '=', True)
        ], order='create_date desc', limit=10)
        
        values = {
            'boat': boat,
            'related_boats': related_boats,
            'reviews': reviews,
            'main_object': boat,
        }
        
        return request.render('odoo_boats.boat_detail_page', values)
    
    @http.route(['/boat//book'], type='http', auth='user', website=True)
    def boat_booking_form(self, boat, **kwargs):
        """Booking checkout page"""
        
        if boat.moderation_status != 'approved' or not boat.active:
            return request.render('website.404')
        
        # Check if user is a guest
        if request.env.user.user_type != 'guest':
            return request.redirect('/web/login?error=guest_only')
        
        values = {
            'boat': boat,
            'booking_data': kwargs,
        }
        
        return request.render('odoo_boats.booking_checkout_page', values)
    
    @http.route(['/boat/booking/create'], type='json', auth='user', website=True)
    def create_booking(self, **kwargs):
        """Create booking record (AJAX)"""
        
        try:
            booking = request.env['boat.booking'].sudo().create({
                'boat_id': int(kwargs.get('boat_id')),
                'guest_id': request.env.user.id,
                'start_date': kwargs.get('start_date'),
                'end_date': kwargs.get('end_date'),
                'num_guests': int(kwargs.get('num_guests')),
            })
            
            # Check availability
            booking.check_availability()
            
            return {
                'success': True,
                'booking_id': booking.id,
                'booking_ref': booking.name,
                'net_payable': booking.net_payable,
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @http.route(['/boat/booking//payment'], type='http', auth='user', website=True)
    def booking_payment(self, booking_id, **kwargs):
        """Payment gateway integration page"""
        
        booking = request.env['boat.booking'].sudo().browse(booking_id)
        
        if not booking or booking.guest_id.id != request.env.user.id:
            return request.render('website.404')
        
        # Get available payment providers
        payment_providers = request.env['payment.provider'].sudo().search([
            ('state', '=', 'enabled'),
        ])
        
        values = {
            'booking': booking,
            'payment_providers': payment_providers,
        }
        
        return request.render('odoo_boats.payment_page', values)