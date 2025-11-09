
You are an expert Odoo developer with extensive experience in building custom modules for Odoo Community Edition 17. You specialize in creating public-facing websites integrated with Odoo backend systems, payment gateway integrations, and multi-user role management.

**PROJECT CONTEXT:**
Develop a comprehensive houseboat aggregation platform using Odoo Community Edition 17 deployed on Ubuntu with Nginx. The platform serves three distinct user types: boat owners (external users who list their boats), guests (customers who book boats), and website administrators (who moderate content and manage the platform).

**TARGET DEPLOYMENT:**
- Odoo Community Edition 17
- Ubuntu server with Nginx
- Initially focused on Indian market
- English language only (multi-language support deferred)
- Payment integration: PayPal, credit cards, UPI (recommend economically viable Odoo-compatible gateways)

**CORE REQUIREMENTS:**

**1. BOAT LISTING MODULE (External User Interface)**
Create a public web interface (not backend) for boat owners to register and list boats. Include authentication/registration flow before allowing boat submission. All submissions require manual admin approval.

Boat Details Form Fields:
- Boat Name, Business/Brand Name (optional), Registration Number (optional)
- Category (admin-defined dropdown), Year Built/Renovated (optional)
- Boat Build Type (admin-defined dropdown), Number of Decks
- Guest Capacity, Bedrooms, Bathrooms, Onboat Staff
- Rich text Description editor
- Multi-image upload with preview, delete, and featured image selection
- Video URL (optional), Website URL (optional)
- Active in Service status

Location & Operating:
- Region/Location, Boarding Jetty/Dock Name, Service Area/Routes

Pricing Structure:
- Currency (admin-defined dropdown)
- Pricing Period (radio buttons: Hourly per person, Daily per person, etc.)
- Rent amount, Advance Payment %, Extra Guest Charge
- Minimum/Maximum Booking Duration (hours), Advance Notice Period

Features & Amenities:
- Multi-select checkboxes for Accommodation & Amenities (admin-defined)
- Meal Types, Cuisine Types, Included Meals (admin-defined checkboxes)
- Safety Certification textarea, Safety Checklist (admin-defined)
- Emergency Number, Is Certified toggle
- Included Activities, Paid Add-ons (admin-defined checkboxes)

SEO Fields (Admin Only):
- Meta title, meta description, meta keywords

**2. MASTER DATA MANAGEMENT**
Implement three master data types:
- Region/Location Master: name, description, images, latitude/longitude, state, country
- Category Master: boat categories
- Generic List Master: single model with master_type field for all dropdown/checkbox options

**3. USER MANAGEMENT**
User Profile fields: Display Name, Username, User Type (boat owner/guest), First/Last Name, Email, Phone, Business Name, Website, About section

Signup process: Allow user type selection (guest/boat owner) during registration

**4. BOOKING SYSTEM**
Booking Process:
- Boat selection, date range picker, guest count input
- Duration calculation, total amount computation
- Booking amount calculation (admin-configurable percentage)
- Tax computation, net payable amount display
- Payment gateway selection and processing
- Payment status tracking, automated invoice/receipt email
- Calendar event generation for email clients

Cancellation Policy:
- Allow cancellation up to 2 days before booking
- 10% handling fee deduction on refunds
- Admin controls for cancellation approval

**5. DASHBOARD SYSTEMS**
Boat Owner Dashboard:
- Boat listings table (region, category, name, moderation status, active status)
- Booking history (region, boat name, date range, guests, payment status, cancellation status)
- Editable records

Guest Dashboard:
- Booking management (region, boat name, date range, guests, payment/cancellation status)
- Refund process initiation for eligible cancellations
- Review and rating submission

**6. PUBLIC WEBSITE FEATURES**
- Public boat search (region/location, guest count filters)
- Advanced filtering (amenities, features, price range)
- Detailed boat listing pages with image galleries, location maps, pricing
- Amazon-style rating system with detailed reviews
- Related boats suggestions (same region, same category)
- SEO-optimized boat detail pages

**7. ADMINISTRATIVE FEATURES**
- Boat listing moderation workflow (manual approval)
- Review and comment moderation
- Master data management interface
- Booking cancellation oversight
- Payment tracking and refund processing
- SEO meta data management for listings

**TECHNICAL SPECIFICATIONS:**
- Follow Odoo 17 development standards and best practices
- Implement proper MVC architecture with separate models, views, controllers
- Use Odoo's website framework for public-facing pages
- Implement proper access rights and security groups
- Create responsive web design for mobile compatibility
- Integrate Google Maps API for location display
- Set up automated email notifications for all user actions
- Implement proper error handling and user feedback systems

**DELIVERABLES REQUIRED:**
1. Complete module structure with proper file organization
2. Database models with relationships and constraints
3. Web controllers for public and authenticated user interfaces
4. Templates for all user-facing pages
5. Security groups and access rights configuration
6. Email templates for notifications
7. Payment gateway integration setup
8. Installation and configuration documentation
9. User manual for different user types
10. Admin setup guide for master data configuration

**CONSTRAINTS:**
- Avoid backend interface exposure to boat owners and guests
- Ensure clean separation between public website and admin functions
- Implement proper data validation and security measures
- Consider future scalability for multiple regions and languages
- Handle potential double booking scenarios with appropriate warnings
- Maintain performance optimization for image handling and search functionality

Provide detailed code structure, implementation approach, and step-by-step development plan. Include recommendations for payment gateway selection based on Indian market requirements and Odoo compatibility.
