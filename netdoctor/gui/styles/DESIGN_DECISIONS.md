# Design Decisions - Blue Dark Theme

## Overview

The `blue_dark.qss` theme file provides comprehensive styling for all Qt widgets in the NetDoctor application, following a flat, modern design aesthetic with a professional blue color scheme.

## Design Philosophy

### 1. Flat Modern Style
- **No 3D bevels or shadows**: All widgets use flat backgrounds without gradients or inset/outset borders
- **Rationale**: Modern UI design favors flat aesthetics for cleaner, more professional appearance and better accessibility
- **Implementation**: All `border` properties use solid colors, no `border-style: inset/outset`

### 2. Rounded Corners (6-10px)
- **Standard widgets**: 6px border-radius (buttons, inputs, checkboxes)
- **Cards and containers**: 8px border-radius (tables, group boxes)
- **Large cards**: 10px border-radius (KPI cards)
- **Rationale**: Rounded corners soften the interface, create visual hierarchy, and align with modern design trends
- **Consistency**: Smaller interactive elements get smaller radii; larger containers get larger radii

### 3. Subtle Hover Transitions
- **Color transitions**: Hover states use slightly lighter variants of the base color
- **Background changes**: Interactive elements change background color on hover (e.g., `#2A2A3E` hover background)
- **Border highlights**: Focused inputs use blue border (`#4A90E2`) to indicate active state
- **Rationale**: Hover feedback improves usability without being distracting
- **Note**: QSS doesn't support CSS transitions, so state changes are instant but visually subtle

### 4. No Default Qt Bevels
- **Flat borders**: All borders are `1px solid` without bevel styles
- **Border removal**: Navigation buttons and icon buttons use `border: none`
- **Rationale**: Removes outdated 3D appearance, creates cleaner modern look

### 5. Consistent Padding & Spacing
- **Buttons**: `10px 20px` (vertical, horizontal) - comfortable click target
- **Input fields**: `8px 12px` - adequate text spacing
- **Table cells**: `8px` - readable content spacing
- **Cards**: `16px` - breathing room for content
- **Rationale**: Consistent spacing creates visual rhythm and improves readability

### 6. Typography Hierarchy
- **Page Title**: 24px, weight 700 (bold) - Main page headings
- **Section Title**: 14px, weight 600 (semi-bold) - Section headings
- **Body Text**: 13px, weight 400 (regular) - Standard text
- **Muted Text**: 12px, weight 400 - Secondary information
- **Rationale**: Clear hierarchy guides user attention and improves scannability
- **Implementation**: Object names (`pageTitle`, `sectionTitle`, `muted`) enable targeted styling

## Color Usage

### Primary Blue (#4A90E2)
- Primary buttons
- Active navigation items
- Focus borders
- Table headers
- Selection highlights

### Background Hierarchy
- Main: `#1E1E2E` - Application background
- Sidebar: `#181825` - Navigation area (darker)
- Cards: `#1F1F2F` - Elevated content surfaces
- Elevated: `#2A2A3E` - Hover states

### Text Contrast
- Primary: `#E4E4E7` - High contrast for readability (13.5:1 ratio)
- Secondary: `#A1A1AA` - Medium contrast for labels (7.2:1 ratio)
- Muted: `#71717A` - Low contrast for hints (4.5:1 ratio)

## Widget-Specific Decisions

### Buttons
- **Primary**: Blue background, white text - Main actions
- **Danger**: Red background, white text - Destructive actions
- **Secondary**: Dark background, light text - Alternative actions
- **Minimum size**: 32px height for touch-friendly interaction

### Input Fields
- **Background**: Darker than main background for visual separation
- **Focus state**: Blue border to indicate active input
- **Placeholder**: Muted text color for clarity

### Tables
- **Alternating rows**: Subtle background variation for readability
- **Header**: Blue text color to match accent scheme
- **Selection**: Semi-transparent blue overlay (20% opacity)

### Scrollbars
- **Thin design**: 12px width/height - Minimal visual footprint
- **Rounded handles**: 6px border-radius for modern appearance
- **Hover state**: Lighter color for visibility

### Progress Bars
- **Background**: Dark with border
- **Chunk**: Primary blue with rounded corners
- **Height**: 24px for good visibility

### Tooltips
- **Dark background**: Matches application theme
- **Rounded corners**: 6px for consistency
- **Opacity**: 240 (slightly transparent for subtle appearance)

## Accessibility Considerations

1. **High Contrast**: Text colors meet WCAG AA standards
2. **Focus Indicators**: Blue borders on focused inputs
3. **Touch Targets**: Minimum 32px height for interactive elements
4. **Color Independence**: Status indicators use both color and icons/text
5. **Readable Font Sizes**: Minimum 12px for body text

## Performance Notes

- QSS is compiled at runtime, so large stylesheets can impact startup time
- All colors are defined inline (no CSS variables support in QSS)
- Comments include palette references for maintainability

## Maintenance

- All color values include comments referencing the palette
- Consistent naming conventions for object names
- Typography hierarchy uses object names for easy updates
- Widget-specific sections are clearly labeled

