# AKC LLC Brand Guidelines

This document outlines the official brand guidelines for AKC LLC, including logo usage, color palette, typography, and UI elements. These guidelines ensure consistent branding across all interfaces of the AKC Construction CRM.

## Logo

![AKC LLC Logo](static/img/akc_logo.png)

### Logo Usage

- The AKC LLC logo should always be displayed in its primary color **#0485ea (Bright Blue)** on a white or light background
- Minimum display size: 40px height for digital applications
- Maintain proper spacing around the logo (at least half the height of the logo on all sides)
- Do not alter the proportions, colors, or any elements of the logo
- When used on dark or complex backgrounds, use the white/monochrome version of the logo

### Logo Placement

- The logo appears in the top left corner of the application navigation bar
- The logo is paired with "Construction CRM" subtitle text in Montserrat font

## Brand Colors

### Primary Color
- **Bright Blue (#0485ea)** – This is the dominant brand color used for primary buttons, links, and accents

### Secondary Colors
- **White (#ffffff)** – Primary background color
- **Dark Gray (#333333)** – Primary text color

### UI Color Variables
```css
--akc-primary: #0485ea;
--akc-primary-dark: #0370c9;
--akc-primary-light: #4fa6f0;
--akc-dark: #333333;
--akc-light-gray: #f5f5f5;
--akc-medium-gray: #e0e0e0;
--akc-white: #ffffff;
```

## Typography

### Primary Font
- **Montserrat**
  - Headings: Bold (700)
  - Navigation: Medium (500)
  - Buttons: Semi-Bold (600)

### Secondary Font
- **Open Sans**
  - Body text: Regular (400)
  - Small text: Light (300)
  - Emphasized text: Semi-Bold (600)

### Font Usage
- Headings (h1-h6): Montserrat Bold
- Body text: Open Sans Regular
- Buttons and calls-to-action: Montserrat Semi-Bold
- Navigation: Montserrat Medium
- Form labels: Open Sans Semi-Bold

## UI Elements

### Buttons
- Primary buttons: Bright Blue background (#0485ea) with white text
- Secondary buttons: Dark Gray background (#333333) with white text
- Outline buttons: Transparent with colored borders
- Button radius: 6px
- Button padding: 0.5rem 1.25rem (standard), 0.25rem 0.75rem (small), 0.75rem 1.5rem (large)

### Cards
- No borders
- 6px border radius
- Light shadow: 0 4px 6px rgba(0, 0, 0, 0.1)
- White background
- Subtle hover effect (elevation increase)

### Forms
- Input fields: 1px border, 6px border radius
- Focus state: Bright Blue border/outline
- Labels: Semi-bold, Dark Gray

### Shadows
- Light: 0 2px 4px rgba(0, 0, 0, 0.1)
- Medium: 0 4px 6px rgba(0, 0, 0, 0.1) 
- Heavy: 0 8px 16px rgba(0, 0, 0, 0.1)

## Animation & Interaction

- Subtle transitions: 0.2-0.3s ease for hover effects
- Fade-in animations for content loading
- Button ripple effect on click
- Card elevation change on hover
- Form field focus effects

## Prohibited Uses

- Do not alter the logo proportions or colors
- Do not use colors not specified in the brand palette for primary UI elements
- Do not use fonts other than Montserrat and Open Sans
- Do not remove the spacing around the logo
- Do not apply effects (shadows, gradients, etc.) to the logo

---

These brand guidelines are implemented in the AKC CRM application through the following files:
- `static/css/akc-brand.css` - Main brand styling
- `static/js/akc-ui.js` - Interaction and animation
- `templates/base.html` - Logo integration

For any questions regarding brand usage, please contact the development team. 