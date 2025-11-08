# -*- coding: utf-8 -*-
# Owner portal controller
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.exceptions import AccessError

class BoatOwnerPortal(CustomerPortal):
    
    @http.route(['/my/boats', '/my/boats/page/'], type='http', auth='user', website=True)
    def my_boats(self, page=1, sortby='date', filterby='all', **kwargs):
        """Boat owner dashboard - My Boats"""
        
        # Check if user is boat owner
        if request.env.user.user_type != 'boat_owner':
            return request.redirect('/my')
        
        # Build domain
        domain = [('owner_id', '=', request.env.user.id)]
        
        if filterby == 'pending':
            domain.append(('moderation_status', '=', 'pending'))
        elif filterby == 'approved':
            domain.append(('moderation_status', '=', 'approved'))
        elif filterby == 'rejected':
            domain.append(('moderation_status', '=', 'rejected'))
        
        # Sorting
        sort_mapping = {
            'date': 'create_date desc',
            'name': 'name',
            'status': 'moderation_status',
        }
        
        # Pagination
        boats_per_page = 10
        boat_count = request.env['boat.listing'].search_count(domain)
        pager = request.website.pager(
            url='/my/boats',
            total=boat_count,
            page=page,
            step=boats_per_page,
        )
        
        boats = request.env['boat.listing'].search(
            domain,
            limit=boats_per_page,
            offset=pager['offset'],
            order=sort_mapping.get(sortby, 'create_date desc')
        )
        
        values = {
            'boats': boats,
            'pager': pager,
            'sortby': sortby,
            'filterby': filterby,
            'page_name': 'my_boats',
        }
        
        return request.render('odoo_boats.owner_dashboard', values)
    
    @http.route(['/my/boat/new'], type='http', auth='user', website=True)
    def boat_create_form(self, **kwargs):
        """Create new boat listing form"""
        
        if request.env.user.user_type != 'boat_owner':
            return request.redirect('/my')
        
        # Get master data for dropdowns
        regions = request.env['boat.region'].sudo().search([('active', '=', True)])
        categories = request.env['boat.category'].sudo().search([('active', '=', True)])
        build_types = request.env['boat.generic.master'].sudo().search([
            ('master_type', '=', 'build_type'),
            ('active', '=', True)
        ])
        amenities = request.env['boat.generic.master'].sudo().search([
            ('master_type', '=', 'amenity'),
            ('active', '=', True)
        ])
        currencies = request.env['boat.generic.master'].sudo().search([
            ('master_type', '=', 'currency'),
            ('active', '=', True)
        ])
        
        values = {
            'regions': regions,
            'categories': categories,
            'build_types': build_types,
            'amenities': amenities,
            'currencies': currencies,
            'boat': None,  # New boat
        }
        
        return request.render('odoo_boats.boat_submission_form', values)
    
    @http.route(['/my/boat//edit'], type='http', auth='user', website=True)
    def boat_edit_form(self, boat_id, **kwargs):
        """Edit existing boat listing"""
        
        boat = request.env['boat.listing'].browse(boat_id)
        
        # Security check
        if boat.owner_id.id != request.env.user.id:
            raise AccessError("You don't have permission to edit this boat.")
        
        # Get master data (same as create)
        regions = request.env['boat.region'].sudo().search([('active', '=', True)])
        categories = request.env['boat.category'].sudo().search([('active', '=', True)])
        # ... (similar to create_form)
        
        values = {
            'boat': boat,
            'regions': regions,
            'categories': categories,
            # ... other master data
        }
        
        return request.render('odoo_boats.boat_submission_form', values)
    
    @http.route(['/my/boat/submit'], type='http', auth='user', methods=['POST'], website=True, csrf=True)
    def boat_submit(self, **post):
        """Handle boat submission (create/update)"""
        
        if request.env.user.user_type != 'boat_owner':
            return request.redirect('/my')
        
        try:
            boat_id = post.get('boat_id')
            
            # Prepare values
            vals = {
                'name': post.get('name'),
                'business_name': post.get('business_name'),
                'category_id': int(post.get('category_id')),
                'region_id': int(post.get('region_id')),
                'guest_capacity': int(post.get('guest_capacity')),
                'rent_amount': float(post.get('rent_amount')),
                'pricing_period': post.get('pricing_period'),
                'description': post.get('description'),
                # ... other fields
            }
            
            if boat_id:
                # Update existing
                boat = request.env['boat.listing'].browse(int(boat_id))
                if boat.owner_id.id != request.env.user.id:
                    raise AccessError("Access denied")
                boat.write(vals)
            else:
                # Create new
                vals['owner_id'] = request.env.user.id
                boat = request.env['boat.listing'].create(vals)
            
            return request.redirect(f'/my/boat/{boat.id}?message=saved')
        
        except Exception as e:
            return request.redirect(f'/my/boat/new?error={str(e)}')