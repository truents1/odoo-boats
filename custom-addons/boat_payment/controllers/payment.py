from odoo import http
from odoo.http import request

class BoatPayment(http.Controller):

    @http.route('/payment/boat/<int:booking_id>', type='http', auth='user', website=True)
    def payment_page(self, booking_id, **kw):
        booking = request.env['boat.booking'].sudo().browse(booking_id)
        if not booking.exists():
            return request.not_found()
        return request.render('boat_payment.payment_placeholder', {'booking': booking})


