# Houseboat Aggregation Platform

## Installation Instructions

### Docker Installation

1. **Copy module to custom-addons**
   ```bash
   cp -r odoo_boats /path/to/your/project/custom-addons/
   ```

2. **Restart Odoo container**
   ```bash
   docker restart odoo-boats-app
   ```

3. **Update Apps List**
   - Login to Odoo: http://localhost:8069
   - Go to Apps menu
   - Click "Update Apps List"

4. **Install Module**
   - Search for "Houseboat" or "odoo_boats"
   - Click Install

### Configuration

1. **Master Data Setup**
   - Navigate to: Boats → Configuration → Master Data
   - Add Regions (e.g., Kerala, Goa)
   - Add Categories (Houseboat, Yacht, etc.)
   - Add Generic Masters (Amenities, Meal Types, etc.)

2. **Payment Gateway Setup**
   - Install payment module: `payment_razorpay` or `payment_stripe`
   - Configure in: Accounting → Configuration → Payment Providers
   - Enter API credentials
   - Enable for website checkout

3. **Create Users**
   - Boat Owner: User Type = "boat_owner"
   - Guest: User Type = "guest"
   - Admin: Assign to "Boat Administrator" group

## Module Structure

```
odoo_boats/
├── __init__.py
├── __manifest__.py
├── models/          # Data models
├── controllers/     # Web controllers
├── views/           # Backend views
├── templates/       # Website templates
├── security/        # Access rights
├── data/            # Default data
├── static/          # CSS, JS, images
└── wizard/          # Wizards
```

## Features

- ✅ Public boat search and filtering
- ✅ Boat owner portal (no backend access needed)
- ✅ Guest booking system
- ✅ Admin moderation workflow
- ✅ Review and rating system
- ✅ Email notifications
- ✅ Payment gateway integration
- ✅ Cancellation management
- ✅ SEO optimization

## Support

For issues and questions, please contact: support@yourcompany.com
