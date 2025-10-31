# Adding Boats Menu to Website

## Issue Fixed
Removed the automatic menu injection that was causing XPath errors. In Odoo 17, it's better to add menu items via the website builder UI.

## File Updated
✅ `views/website_templates.xml` - Removed the menu inheritance template

## How to Add "Boats" Menu to Website

After the module is installed, add the menu manually through the website builder:

### Method 1: Using Website Builder (Recommended)

1. **Go to your website** (click "Website" in the main menu or visit the website URL)

2. **Enable Edit Mode**:
   - Click "Edit" button in top right
   - Or press `Ctrl + K` then type "edit"

3. **Add Menu Item**:
   - Click on the menu bar at the top
   - Click "+ New Menu" or "Edit Menu"
   - Add a new menu item:
     - **Name**: Boats
     - **URL**: /boats
     - **Position**: Where you want it in the menu
   - Save

4. **Exit Edit Mode**: Click "Save" in top right

### Method 2: Via Backend Settings

1. **Go to**: Website → Configuration → Menus

2. **Create New Menu**:
   - Name: Boats
   - URL: /boats
   - Parent Menu: Main Menu (or wherever you want)
   - Sequence: 40 (adjust as needed)

3. **Save**

### Method 3: Add it Back via XML (Optional)

If you really want it automated, you can try this alternative template in `website_templates.xml`:

```xml
<!-- Add this before the closing </odoo> tag -->
<record id="website_menu_boats" model="website.menu">
    <field name="name">Boats</field>
    <field name="url">/boats</field>
    <field name="parent_id" ref="website.main_menu"/>
    <field name="sequence">40</field>
</record>
```

## Now Try Installing Again

1. **Update** `views/website_templates.xml` in your repository

2. **Restart Odoo**:
   ```bash
   docker-compose restart web
   ```

3. **Upgrade the module**:
   - Go to Apps
   - Find "Boat Management Base"
   - Click "Upgrade"
   - Should succeed now! ✅

## What's Working

After successful installation:

✅ Backend boat management with full workflow
✅ Portal access at `/my/boats` for boat owners
✅ Public boat listing at `/boats` (accessible directly via URL)
✅ Public boat details at `/boats/<id>`
✅ All filters and search functionality

## Testing URLs

After installation, test these URLs:

- **Backend**: http://localhost:8069/web (login as admin)
  - Go to Boat Management → All Boats
  - Go to Boat Management → Pending Review

- **Portal**: http://localhost:8069/my/boats (login as portal user)
  - Create new boat
  - Submit for review

- **Public Website**: http://localhost:8069/boats (no login needed)
  - Browse published boats
  - View boat details

## Quick Test Plan

1. **As Admin**:
   - Create categories, locations, amenities
   - Create a test boat
   - Change state to "Published"
   - Set "Visible on Website" = True

2. **Visit** http://localhost:8069/boats
   - Should see the published boat

3. **Create Portal User**:
   - Settings → Users → Create
   - Set Portal access
   - Login as that user

4. **As Portal User**:
   - Visit /my/boats
   - Create a boat
   - Submit for review

5. **As Admin**:
   - Review the submitted boat
   - Approve and publish it

6. **Check Website**:
   - Visit /boats
   - Should see both boats

## Troubleshooting

### Can't access /boats
- Make sure module is installed
- Check controllers/portal.py exists
- Restart Odoo

### Boats not showing on /boats
- Check boat state = 'published'
- Check website_published = True
- Try as admin first (to rule out permission issues)

### Menu not showing
- That's expected - add it manually via website builder
- Or use Method 3 above to add via XML