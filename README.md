# 0) High-level architecture

Split into small, cohesive addons. Keep public UI in website modules. Keep business logic in core/booking. Admin stays in backend. External users never touch backend menus.

```
addons/
  boat_masterdata/        # Regions, categories, generic options, amenity taxonomies
  boat_core/              # Boat model, media, pricing, SEO, moderation state
  boat_booking/           # Availability, bookings, pricing engine, cancellation/refund rules
  boat_reviews/           # Ratings, reviews, aggregates
  boat_owner_portal/      # Website: owner auth, submission, dashboard, edit flows
  boat_guest_portal/      # Website: guest auth, search, filters, detail page, booking, dashboard
  boat_payment/           # Payment providers glue and callbacks, receipt/ICS emails
  boat_moderation/        # Admin queues for boats, reviews, bookings, refunds
  boat_seo/               # Meta fields exposure, sitemap, OpenGraph, schema.org
```

Dependencies:

* All website modules depend on `website`, `auth_signup`.
* `boat_payment` depends on `payment` and the chosen provider module(s) if available.
* No frontend exposure to backend menus for owners/guests.

# 1) Data models (key fields and constraints)

## 1.1 boat_masterdata

`boat.region`

* name (required), description (html), image_ids (ir.attachment m2m), latitude, longitude, state, country
* active (bool)

`boat.category`

* name (required), parent_id (for hierarchy), active

`boat.option`  (Generic List Master)

* name (required)
* master_type (selection): `build_type`, `amenity`, `meal_type`, `cuisine_type`, `included_meal`, `safety_check`, `activity`, `paid_addon`, `pricing_period`, `currency`
* value_code (optional), active, sequence

Access: admin only.

## 1.2 boat_core

`boat.boat`

* owner_id (res.users, required, portal)
* name (required)
* brand_name, registration_no
* category_id (boat.category, required)
* year_built, year_renovated
* build_type_id (boat.option where master_type=build_type)
* deck_count, guest_capacity, bedroom_count, bathroom_count, staff_count
* description_html (html)
* image_ids (ir.attachment m2m, website publishable), featured_image_id
* video_url, website_url
* active_service (bool)
* region_id (boat.region, required)
* boarding_jetty, service_area
* currency_id (res.currency, limit choices by admin if needed)
* pricing_period (selection)  # normalized from boat.option with stable keys; or FK to option
* price_rent (monetary)
* price_advance_percent (float 0..100)
* price_extra_guest (monetary)
* min_duration_hours, max_duration_hours, advance_notice_hours
* amenity_ids (m2m boat.option where master_type=amenity)
* meal_type_ids (m2m), cuisine_type_ids (m2m), included_meal_ids (m2m)
* safety_cert_text (text)
* safety_check_ids (m2m boat.option where master_type=safety_check)
* emergency_phone, is_certified (bool)
* included_activity_ids (m2m), paid_addon_ids (m2m)
* state (selection): `draft`, `submitted`, `approved`, `rejected`, `archived`
* seo_title, seo_description, seo_keywords (admin only, access rule)
* rating_avg, rating_count (stored compute from reviews)

Constraints:

* SQL check `price_advance_percent BETWEEN 0 AND 100`.
* Featured image must be in image_ids (python constraint).
* Owner can only edit own boats unless admin.

## 1.3 boat_booking

`boat.availability.slot` (optional if you later add advanced calendars)

* boat_id, date_from, date_to, kind (`blocked`, `available`), note

`boat.booking`

* sequence, name (booking code)
* boat_id (required), owner_id (related from boat), guest_id (res.users portal), region_id (related)
* date_from (datetime), date_to (datetime), duration_hours (compute)
* guest_count (int >0)
* pricing_period, price_base, price_extra_guest, price_subtotal, tax_amount, price_total
* advance_percent, advance_amount, balance_amount
* currency_id
* payment_tx_id (payment.transaction), payment_status (selection: `pending`, `authorized`, `paid`, `refunded`, `failed`)
* state (selection): `draft`, `pending_payment`, `confirmed`, `cancel_requested`, `cancelled`, `refunded`
* cancel_requested_on, cancel_reason, cancel_fee_amount, refund_amount
* policy_cutoff_days=2 (default), policy_fee_percent=10 (default)
* notes, internal_note
* ics_attachment_id (ir.attachment)
* website_channel (`web`, `mobile_api`) for analytics

Constraints:

* No double booking: python constraint checks any overlapping confirmed/pending_payment bookings for same boat.
  Logic: overlap if `(new.start < existing.end) AND (existing.start < new.end)` for states in `pending_payment, confirmed`.
* `date_to > date_from`, `guest_count <= boat.guest_capacity + allowed_extra` (if using paid extra).

## 1.4 boat_reviews

`boat.review`

* boat_id, booking_id (optional if only after booking), user_id
* rating_overall (1..5) + optional subratings
* title, body (text)
* state: `pending`, `published`, `rejected`
* helpful_votes, report_count

Aggregate triggers:

* Recompute `boat.boat.rating_avg` and `rating_count` on publish.

# 2) Access control

Groups:

* `group_boat_owner_portal` (portal derived)
* `group_guest_portal` (portal derived)
* `group_boat_admin` (internal user)
* `group_moderator` (internal user limited)

ACLs (`ir.model.access.csv`):

* Owners: read/write own `boat.boat` in states `draft` or `rejected`, submit action; no unlink after approved if linked bookings exist. Record rules filter by `owner_id = user.id`.
* Owners: read bookings of own boats; read/write booking notes? write limited.
* Guests: read/write own `boat.booking` records; record rule `guest_id = user.id`.
* Public: read published boats and reviews through website controllers, not via RPC.
* Admin/Moderator: full.

# 3) Website flows and controllers

## 3.1 Public pages (guest)

Routes (controller `boat_guest_portal.controllers`):

* `/boats` search + filters (GET)
* `/boats/<slug(boat.boat)>` detail page (GET)
* `/boats/<slug>/availability` API for date widgets (GET JSON)
* `/book/<slug>` booking wizard (GET/POST)
* `/payment/boat/<booking>` kickoff (GET)
* `/payment/boat/<booking>/return` provider return (GET)
* `/payment/boat/<booking>/webhook` provider webhook (POST)
* `/my/bookings` dashboard list (GET)
* `/my/bookings/<id>` detail, cancel request (POST)
* Reviews: `/my/review/new`, `/boats/<slug>/reviews`

Search filters:

* region_id, guest_count, category_id
* amenities (ids), price_min/max, certified flag
* sort: relevance, price, rating

Templates: QWeb with Bootstrap 5 (Odoo website) and lazy-loaded images. Use Owl components for gallery if needed.

## 3.2 Owner portal

Routes (controller `boat_owner_portal.controllers`):

* `/owner/signup` user type flag
* `/owner/boats` list
* `/owner/boats/new` multi-step form
* `/owner/boats/<id>/edit`
* `/owner/bookings` list with statuses and payouts view (informational)
* Image upload endpoints using `ir.attachment` with `public=False`, then mark publish on approval. Feature image toggle.

Moderation:

* Submission sets state=`submitted`; admin reviews in backend, sets `approved` to expose on site.

## 3.3 Admin moderation backend

Menus only for internal users:

* Boats: Submitted queue, Approved, Rejected
* Reviews: Pending
* Bookings: Cancel requests, Refund queue
* Masterdata: Regions, Categories, Options

# 4) Pricing and booking engine

Computation service class in `boat_booking/models/pricing.py`:

* Input: boat, date_from/to, guest_count
* Map `pricing_period`:

  * `hour_pp` = hourly per person
  * `day_pp`  = daily per person
  * `day_boat` = daily per boat
  * others as needed
* Steps:

  1. Validate advance_notice_hours.
  2. Compute duration in hours and days. Enforce min/max.
  3. Base = rate × multiplier × guests depending on period.
  4. Extra guest charges if guest_count > boat.guest_capacity.
  5. Taxes: simple tax percent configurable in `ir.config_parameter` or region.
  6. Advance amount = ceil(advance_percent × total).
  7. Balance amount = total − advance.

Persist all numbers on `boat.booking` at creation to avoid drift.

# 5) Cancellation and refunds

Policy:

* Allow cancellation if now <= date_from − 2 days.
* Fee = max(10% of paid amount, configurable).
* Refund amount = paid − fee.
* State transitions:

  * guest action → `cancel_requested`
  * admin approves → compute refund, trigger provider refund API if supported → `refunded` else `cancelled` with manual note.

# 6) Emails and ICS

Emails (QWeb + mail templates):

* Owner: new submission received
* Owner: boat approved/rejected
* Guest: booking pending payment
* Guest: booking confirmed (attach .ics)
* Guest: cancellation approved and refund info
* Admin: cancel request alert

ICS generation in `boat_payment` after confirmation:

* Build `text/calendar` with VEVENT summary “Houseboat Booking: <Boat>”, start/end, location (region + jetty), organizer, UID, URL. Attach to mail.

# 7) Payment integration

Use Odoo’s `payment` framework:

Recommended for India:

* Razorpay: low fees, UPI + cards + net-banking. Odoo CE provider addon may not be official. Two paths:

  1. If a maintained Odoo 17 CE Razorpay provider addon is available, depend on it.
  2. Else implement a lightweight provider:

     * Model: inherit `payment.provider` with code `razorpay`.
     * Create order via REST, render checkout on `/payment/transaction/<tx>` with their JS.
     * Verify signature on return/webhook, set `payment.transaction` → `done` or `error`.
* PayPal: global fallback. Use official `payment_paypal` if present.
* Cashfree or PayU: similar pattern if you need UPI and cards with one contract.

Economic recommendation:

* Primary: Razorpay (UPI support, domestic rates).
* Secondary: PayPal for international guests.
* Keep provider selection at booking checkout. Default by region=India → Razorpay.

Security:

* Webhook endpoints CSRF-exempt with HMAC signature verification.
* Recompute amounts server-side before capturing.
* Store provider references only, no card data.

# 8) Public website UX details

* Search page: left filter panel, right results with photo, rating, price “from”.
* Boat detail: gallery, key specs, amenities, region map (Google Maps JS), pricing card with date range, guest picker, instant quote.
* Reviews: Amazon-style breakdown (5..1 stars bars), verified badge if linked to completed booking.
* Related boats: same region, same category limit 6.

Maps:

* Load Google Maps JS with API key from `ir.config_parameter`.
* Show marker at (lat, lon) from region, optional boat location override.

Images:

* Store originals in attachments. Generate website thumbnails via `website_image` helpers.
* Limit per-image size and total count. Client-side preview then upload.

# 9) SEO

* Per boat: meta title/description/keywords (admin only).
* Auto OpenGraph/Twitter tags using featured image.
* JSON-LD `Product` or `LocalBusiness` with `aggregateRating`.
* Sitemap entries for approved boats.
* Canonical URLs via slug.

# 10) Module skeletons (key files)

## boat_masterdata/**manifest**.py

```python
{
  "name": "Boat Masterdata",
  "version": "17.0.1.0",
  "depends": ["base"],
  "data": [
    "security/ir.model.access.csv",
    "views/boat_region_views.xml",
    "views/boat_category_views.xml",
    "views/boat_option_views.xml",
  ],
  "application": False,
}
```

### models/boat_region.py

```python
from odoo import api, fields, models

class BoatRegion(models.Model):
    _name = "boat.region"
    _description = "Region/Location"

    name = fields.Char(required=True)
    description = fields.Html()
    image_ids = fields.Many2many('ir.attachment', string="Images")
    latitude = fields.Float()
    longitude = fields.Float()
    state = fields.Char()
    country = fields.Char()
    active = fields.Boolean(default=True)
```

### models/boat_option.py

```python
class BoatOption(models.Model):
    _name = "boat.option"
    _description = "Generic Option"

    name = fields.Char(required=True)
    master_type = fields.Selection([
        ("build_type","Build Type"), ("amenity","Amenity"),
        ("meal_type","Meal Type"), ("cuisine_type","Cuisine Type"),
        ("included_meal","Included Meal"), ("safety_check","Safety Check"),
        ("activity","Included Activity"), ("paid_addon","Paid Add-on"),
        ("pricing_period","Pricing Period"), ("currency","Currency"),
    ], required=True, index=True)
    value_code = fields.Char()
    sequence = fields.Integer()
    active = fields.Boolean(default=True)
    _sql_constraints = [
        ('uniq_name_type', 'unique(name, master_type)',
         'Duplicate name for the same master type.')
    ]
```

## boat_core/models/boat_boat.py

```python
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class Boat(models.Model):
    _name = "boat.boat"
    _description = "Boat"
    _rec_name = "name"
    _order = "create_date desc"

    owner_id = fields.Many2one('res.users', required=True, index=True)
    name = fields.Char(required=True)
    brand_name = fields.Char()
    registration_no = fields.Char()
    category_id = fields.Many2one('boat.category', required=True, index=True)
    year_built = fields.Integer()
    year_renovated = fields.Integer()
    build_type_id = fields.Many2one('boat.option', domain=[('master_type','=','build_type')])
    deck_count = fields.Integer()
    guest_capacity = fields.Integer(required=True)
    bedroom_count = fields.Integer()
    bathroom_count = fields.Integer()
    staff_count = fields.Integer()
    description_html = fields.Html()
    image_ids = fields.Many2many('ir.attachment', string="Images")
    featured_image_id = fields.Many2one('ir.attachment')
    video_url = fields.Char()
    website_url = fields.Char()
    active_service = fields.Boolean(default=True)

    region_id = fields.Many2one('boat.region', required=True)
    boarding_jetty = fields.Char()
    service_area = fields.Char()

    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id.id)
    pricing_period = fields.Selection([
        ('hour_pp','Hourly per person'),
        ('day_pp','Daily per person'),
        ('day_boat','Daily per boat'),
    ], required=True, default='day_boat')
    price_rent = fields.Monetary(default=0.0)
    price_advance_percent = fields.Float(default=20.0)
    price_extra_guest = fields.Monetary(default=0.0)
    min_duration_hours = fields.Integer(default=2)
    max_duration_hours = fields.Integer(default=240)
    advance_notice_hours = fields.Integer(default=12)

    amenity_ids = fields.Many2many('boat.option', string="Amenities",
                                   domain=[('master_type','=','amenity')])
    meal_type_ids = fields.Many2many('boat.option', domain=[('master_type','=','meal_type')])
    cuisine_type_ids = fields.Many2many('boat.option', domain=[('master_type','=','cuisine_type')])
    included_meal_ids = fields.Many2many('boat.option', domain=[('master_type','=','included_meal')])
    safety_cert_text = fields.Text()
    safety_check_ids = fields.Many2many('boat.option', domain=[('master_type','=','safety_check')])
    emergency_phone = fields.Char()
    is_certified = fields.Boolean()

    included_activity_ids = fields.Many2many('boat.option', domain=[('master_type','=','activity')])
    paid_addon_ids = fields.Many2many('boat.option', domain=[('master_type','=','paid_addon')])

    state = fields.Selection([
        ('draft','Draft'), ('submitted','Submitted'),
        ('approved','Approved'), ('rejected','Rejected'), ('archived','Archived')
    ], default='draft', index=True)

    seo_title = fields.Char(groups="boat_seo.group_seo_admin")
    seo_description = fields.Char(groups="boat_seo.group_seo_admin")
    seo_keywords = fields.Char(groups="boat_seo.group_seo_admin")

    rating_avg = fields.Float(digits=(2,1))
    rating_count = fields.Integer()

    @api.constrains('price_advance_percent')
    def _check_advance(self):
        for rec in self:
            if rec.price_advance_percent < 0 or rec.price_advance_percent > 100:
                raise ValidationError(_("Advance % must be 0..100"))

    @api.constrains('featured_image_id','image_ids')
    def _check_feature_in_images(self):
        for rec in self:
            if rec.featured_image_id and rec.featured_image_id not in rec.image_ids:
                raise ValidationError(_("Featured image must be one of Images."))

    def action_submit(self):
        self.write({'state':'submitted'})

    def action_approve(self):
        self.write({'state':'approved'})

    def action_reject(self):
        self.write({'state':'rejected'})
```

## boat_booking/models/boat_booking.py

```python
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class BoatBooking(models.Model):
    _name = "boat.booking"
    _description = "Boat Booking"
    _order = "create_date desc"

    boat_id = fields.Many2one('boat.boat', required=True, index=True)
    owner_id = fields.Many2one(related='boat_id.owner_id', store=True)
    guest_id = fields.Many2one('res.users', required=True, index=True)
    region_id = fields.Many2one(related='boat_id.region_id', store=True)

    date_from = fields.Datetime(required=True)
    date_to   = fields.Datetime(required=True)
    duration_hours = fields.Float(compute='_compute_duration', store=True)
    guest_count = fields.Integer(required=True, default=2)

    pricing_period = fields.Selection(related='boat_id.pricing_period', store=True)
    currency_id = fields.Many2one(related='boat_id.currency_id', store=True)

    price_base = fields.Monetary()
    price_extra_guest = fields.Monetary()
    tax_amount = fields.Monetary()
    price_total = fields.Monetary()

    advance_percent = fields.Float()
    advance_amount = fields.Monetary()
    balance_amount = fields.Monetary()

    payment_tx_id = fields.Many2one('payment.transaction')
    payment_status = fields.Selection([
        ('pending','Pending'), ('authorized','Authorized'),
        ('paid','Paid'), ('failed','Failed'), ('refunded','Refunded')
    ], default='pending')

    state = fields.Selection([
        ('draft','Draft'), ('pending_payment','Pending Payment'),
        ('confirmed','Confirmed'), ('cancel_requested','Cancel Requested'),
        ('cancelled','Cancelled'), ('refunded','Refunded')
    ], default='draft', index=True)

    policy_cutoff_days = fields.Integer(default=2)
    policy_fee_percent = fields.Float(default=10.0)

    @api.depends('date_from','date_to')
    def _compute_duration(self):
        for r in self:
            if r.date_from and r.date_to:
                delta = fields.Datetime.to_datetime(r.date_to) - fields.Datetime.to_datetime(r.date_from)
                r.duration_hours = delta.total_seconds() / 3600.0
            else:
                r.duration_hours = 0.0

    @api.constrains('date_from','date_to')
    def _check_dates(self):
        for r in self:
            if r.date_to and r.date_from and r.date_to <= r.date_from:
                raise ValidationError(_("End must be after start."))

    @api.constrains('boat_id','date_from','date_to','state')
    def _check_overlap(self):
        for r in self:
            if not r.boat_id or not r.date_from or not r.date_to:
                continue
            domain = [
                ('id','!=', r.id),
                ('boat_id','=', r.boat_id.id),
                ('state','in', ['pending_payment','confirmed']),
                ('date_from','<', r.date_to),
                ('date_to','>', r.date_from),
            ]
            if self.search_count(domain):
                raise ValidationError(_("Boat is already booked for the selected time range."))
```

Pricing compute entrypoint:

```python
    def compute_pricing(self):
        self.ensure_one()
        boat = self.boat_id
        hrs = self.duration_hours
        guests = self.guest_count
        base = 0
        if boat.pricing_period == 'hour_pp':
            base = boat.price_rent * hrs * guests
        elif boat.pricing_period == 'day_pp':
            days = max(1, int((hrs + 23)//24))
            base = boat.price_rent * days * guests
        else:  # day_boat
            days = max(1, int((hrs + 23)//24))
            base = boat.price_rent * days
        extra = 0
        if guests > boat.guest_capacity and boat.price_extra_guest:
            extra = (guests - boat.guest_capacity) * boat.price_extra_guest
        tax_percent = float(self.env['ir.config_parameter'].sudo().get_param('boat.tax_percent', '0'))
        tax = (base + extra) * tax_percent / 100.0
        total = base + extra + tax
        adv_pct = boat.price_advance_percent
        adv_amt = total * adv_pct / 100.0
        self.update({
            'price_base': base,
            'price_extra_guest': extra,
            'tax_amount': tax,
            'price_total': total,
            'advance_percent': adv_pct,
            'advance_amount': adv_amt,
            'balance_amount': total - adv_amt,
        })
```

## Controllers (snippets)

### Public search

```python
# boat_guest_portal/controllers/main.py
from odoo import http
from odoo.http import request

class BoatWebsite(http.Controller):

    @http.route(['/boats'], type='http', auth='public', website=True)
    def boats(self, **kw):
        domain = [('state','=','approved')]
        if kw.get('region_id'):
            domain += [('region_id','=', int(kw['region_id']))]
        if kw.get('category_id'):
            domain += [('category_id','=', int(kw['category_id']))]
        # amenity filters...
        boats = request.env['boat.boat'].sudo().search(domain, limit=24)
        return request.render('boat_guest_portal.boat_list', {'boats': boats, 'kw': kw})
```

### Booking create

```python
    @http.route(['/book/<model("boat.boat"):boat>'], type='http', auth='user', website=True)
    def book(self, boat, **kw):
        user = request.env.user
        # user must be guest type; enforce via group
        values = {...}
        return request.render('boat_guest_portal.booking_form', values)

    @http.route(['/book/submit'], type='json', auth='user')
    def book_submit(self, **post):
        env = request.env
        boat = env['boat.boat'].browse(int(post['boat_id']))
        booking = env['boat.booking'].create({
            'boat_id': boat.id,
            'guest_id': env.user.id,
            'date_from': post['date_from'],
            'date_to': post['date_to'],
            'guest_count': int(post['guest_count']),
            'state': 'pending_payment',
        })
        booking.compute_pricing()
        return {'booking_id': booking.id, 'redirect': f"/payment/boat/{booking.id}"}
```

### Payment kickoff and callbacks

```python
# boat_payment/controllers/payment.py
class BoatPayment(http.Controller):

    @http.route(['/payment/boat/<int:booking_id>'], type='http', auth='user', website=True)
    def payment_page(self, booking_id, **kw):
        booking = request.env['boat.booking'].browse(booking_id).sudo()
        tx = request.env['payment.transaction'].sudo()._create(
            {
                'amount': booking.advance_amount,
                'currency_id': booking.currency_id.id,
                'partner_id': request.env.user.partner_id.id,
                'reference': f"BOAT-{booking.id}",
                'provider_id': self._select_provider_id(kw),
            }
        )
        booking.payment_tx_id = tx.id
        return request.redirect(f"/payment/checkout?reference={tx.reference}")
```

Webhook verifies signature, then:

```python
        if verified and status == 'paid':
            booking.sudo().write({'payment_status':'paid','state':'confirmed'})
            self._send_confirmation_email(booking)
```

# 11) Security and website-only exposure

* No backend menus for owners/guests.
* Portal groups see website pages only.
* Controllers use `sudo()` for read-only approved content. Writes always scoped to `request.env.user`.
* File uploads: store private first. On approval, copy or toggle permission.
* CSRF on website forms; webhooks CSRF-exempt with signature checks.

# 12) Dashboards

## Owner dashboard

* `/owner/boats`: table columns region, category, name, moderation state, active flag, edit/view.
* `/owner/bookings`: booking history with date range, guests, payment status, cancel status.
* Inline edit for text and numeric fields via JSON endpoints. Respect state.

## Guest dashboard

* `/my/bookings`: manage bookings, request cancellation button (disabled inside cutoff).
* Start refund flow. Show payment reference.
* Create review button after trip end.

# 13) Admin views

* Kanban for boats by state with quick approve/reject buttons.
* Tree views for reviews pending.
* Booking cancel queue with auto fee calculation.
* Payment tracking list with provider reference and reconciliation note.

# 14) Templates (key)

* `boat_guest_portal/`

  * `templates/boat_list.xml`: filters form + grid
  * `templates/boat_detail.xml`: gallery, map, price card, reviews
  * `templates/booking_form.xml`: date range widget, guest picker, live price
  * `templates/guest_dashboard.xml`
* `boat_owner_portal/`

  * `templates/owner_wizard.xml`, `templates/owner_dashboard.xml`
* `boat_payment/`

  * `templates/payment_redirect.xml`
* `boat_reviews/`

  * `templates/reviews_block.xml`, `templates/review_form.xml`

Use `t-call="website.layout"`, `t-esc`, `t-foreach`, and `owl` for interactive widgets.

# 15) Email templates

`data/mail_templates.xml`:

* `<record id="mail_tmpl_booking_confirmed" model="mail.template">` with ICS attachment from binary field.
* Other templates as listed in section 6.

# 16) Config parameters

* `boat.tax_percent` default 0
* `boat.payment.default_provider`
* `boat.maps.api_key`
* `boat.seo.enable_opengraph`
* `boat.policy.cutoff_days`, `boat.policy.fee_percent`

# 17) Deployment (Ubuntu + Nginx)

* Odoo 17 CE with workers > 2 for website.
* `proxy_mode = True`.
* Nginx:

```
server {
  listen 80;
  server_name yayboat.com;
  client_max_body_size 64m;
  location / {
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_pass http://127.0.0.1:8069;
  }
  location /longpolling {
    proxy_pass http://127.0.0.1:8072;
  }
  location ~* /web/static/ {
    proxy_cache_valid 200 60m;
    proxy_buffering on;
    expires 1h;
    proxy_pass http://127.0.0.1:8069;
  }
}
```

* Enable HTTPS with Certbot.
* Configure workers, db_maxconn, and `limit_request_field_size` for uploads.
* Use filestore on SSD. Enable image lazy loading.

# 18) Step-by-step build plan

1. Create `boat_masterdata`: models, menus, ACLs. Load seed data for pricing_period options.
2. Create `boat_core`: boat model, constraints, admin views only.
3. Create `boat_owner_portal`: owner signup flag, submission wizard, image upload, submit→moderation.
4. Create `boat_moderation`: backend queues and actions approve/reject. On approve, publish website.
5. Create `boat_guest_portal`: search, detail, related boats, map, booking wizard with price compute.
6. Create `boat_booking`: booking model, overlap constraint, pricing engine.
7. Create `boat_payment`: integrate Razorpay first. Payment kickoff, return, webhook. Update states, send emails with ICS.
8. Create `boat_reviews`: review write and moderation, aggregates on publish.
9. Create `boat_seo`: meta fields exposure, sitemap, OpenGraph, schema.org.
10. Add tests:

* model constraints (advance %, overlap)
* booking price scenarios
* policy cutoff and refund math
* controller auth and record rules

11. Documentation: installation, env vars, provider keys, maps API key, mail catchall.
12. Admin setup guide: create regions/categories/options, set tax %, policy %, default provider, email templates.
13. Load demo data for quick QA.
14. Performance pass: SQL indexes on (`boat_id`, `date_from`), (`region_id`, `category_id`), full-text on name/description if needed. Image thumbnailing.
15. Security audit: routes, sudo usage, webhook signatures, attachment access.

# 19) Payment provider blueprint (Razorpay quick sketch)

Model inherit:

```python
class PaymentProviderRazorpay(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(selection_add=[('razorpay', 'Razorpay')])
    razorpay_key_id = fields.Char(groups='base.group_system')
    razorpay_key_secret = fields.Char(groups='base.group_system')
```

Transaction methods:

* `_razorpay_form_generate_values(self, values)` create order and return keys for JS.
* `_razorpay_get_tx_from_data(self, data)` verify signature.
* `_razorpay_process_notification(self, data)` set `transaction.state` and link to booking.

# 20) User management

Extend signup to capture user_type:

* Add hidden field `user_type = owner|guest`.
* On signup, add to group `group_boat_owner_portal` or `group_guest_portal`.
* Profile fields on `res.users` via inheritance: display_name override, username, phone, business_name, website, about.

# 21) Validation and UX guards

* Enforce advance_notice_hours at booking submit.
* Show warning banners for potential overlaps when the user selects dates.
* Block delete of region/category if boats exist (ondelete='restrict') to avoid FK errors.
* Graceful 4xx messages on permission denials.
* Rate limiting on review posts.

# 22) Documentation deliverables

* Install guide: dependencies, addons path, config params, Nginx, HTTPS, mail.
* Admin manual: master data creation, moderation workflows, refunds.
* Owner manual: how to list a boat and update details.
* Guest manual: search, booking, payment, cancellation, reviews.

