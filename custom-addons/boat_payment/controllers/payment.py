from odoo import http
from odoo.http import request

class BoatPayment(http.Controller):

    @http.route(['/payment/boat/<int:booking_id>'], type='http', auth='user', website=True)
    def payment_page(self, booking_id, **kw):
        booking = request.env['boat.booking'].browse(booking_id).sudo()
        if not booking:
            return request.not_found()
        # Placeholder: redirect to generic payment checkout when tx is created.
        # In a real provider, create payment.transaction then redirect.
        return request.render('boat_payment.payment_placeholder', {'booking': booking})
