# Quantum Clarity Design System

## Overview
The Quantum Clarity theme is designed for the RAMA (Research Automation Using MCP Server & Agentic AI) project. It emphasizes intelligence, clarity, and trust with a dark mode-first approach optimized for long research sessions.

---

## Color Palette

### Primary Accent (Electric Violet)
- **Hex**: `#6B48FF`
- **Usage**: Primary buttons, active states, key icons, progress indicators
- **Associated Feeling**: Innovation, intelligence, cutting-edge technology

### Secondary Accent (Teal Glow)
- **Hex**: `#00C9A7`
- **Usage**: Success messages, "idea generated" indicators, minor CTAs
- **Associated Feeling**: Success, growth, positive feedback

---

## Neutral Backgrounds

### Midnight Ink (Main Background)
- **Hex**: `#1A1A2E`
- **Usage**: Main app background, sidebars

### Shadowed Nebula (Secondary Background)
- **Hex**: `#2C2C4A`
- **Usage**: Card backgrounds, secondary panels, hover states

### Cosmic Gray (Tertiary Background)
- **Hex**: `#3D3D5E`
- **Usage**: Input fields, tertiary backgrounds

---

## Text Colors

### Stellar White (Primary Text)
- **Hex**: `#E0E0E0`
- **Usage**: Main headings, body text

### Nebula Gray (Secondary Text)
- **Hex**: `#A0A0B0`
- **Usage**: Descriptions, labels, less important information

### Pure White (CTA Text)
- **Hex**: `#FFFFFF`
- **Usage**: Text on primary accent buttons

---

## Semantic Colors

### Success
- **Hex**: `#00C9A7` (Teal Glow)
- **Usage**: Success messages, completed tasks

### Warning
- **Hex**: `#FFC107` (Amber)
- **Usage**: Warning alerts, cautionary messages

### Error
- **Hex**: `#DC3545` (Crimson Red)
- **Usage**: Error messages, validation failures

---

## Typography

### Font Family
- **Primary**: `'Inter', sans-serif`
- **Source**: [Google Fonts](https://fonts.google.com/specimen/Inter)

### Font Weights & Sizes

#### Headings
- **Weight**: 700 (Bold)
- **Sizes**: 
  - H1: 36px
  - H2: 24px
  - H3: 18px

#### Body Text
- **Weight**: 400 (Regular)
- **Size**: 14-16px

#### Labels / Small Text
- **Weight**: 500 (Medium)
- **Size**: 12-13px
- **Color**: Often uses secondary text color

---

## Component Styles

### Buttons

#### Primary Button
```css
background-color: #6B48FF;
color: #FFFFFF;
padding: 15px;
border-radius: 5px;
font-weight: 700;
transition: background-color 0.3s ease;
```

**Hover State**: `background-color: #5a38e0;`

#### Secondary Button (Outlined)
```css
background-color: transparent;
border: 2px solid #6B48FF;
color: #6B48FF;
padding: 10px 20px;
border-radius: 5px;
font-weight: 600;
```

**Hover State**: 
```css
background-color: #6B48FF;
color: #FFFFFF;
```

### Input Fields
```css
background-color: #3D3D5E;
color: #E0E0E0;
border: 1px solid #3D3D5E;
padding: 12px;
border-radius: 5px;
```

**Focus State**: `border-color: #6B48FF;`

### Cards
```css
background-color: #2C2C4A;
padding: 30px;
border-radius: 10px;
border: 2px solid #6B48FF;
box-shadow: 0 4px 15px rgba(107, 72, 255, 0.2);
```

**Hover State**: 
```css
transform: translateY(-5px);
box-shadow: 0 8px 25px rgba(107, 72, 255, 0.3);
```

---

## Iconography

### Recommended Icon Sets
1. **Feather Icons**: Clean, minimalist line icons
2. **Phosphor Icons**: Modern, versatile icon family

### Icon Usage Guidelines
- Use monochromatic icons
- Match primary text color (`#E0E0E0`) or accent colors
- Consistent stroke width (2px recommended)
- Size: 20-24px for navigation, 16-18px for inline

---

## Spacing & Layout

### Spacing Scale
- **XS**: 4px
- **SM**: 8px
- **MD**: 16px
- **LG**: 24px
- **XL**: 32px
- **XXL**: 48px

### Container Max-Widths
- **Small**: 600px
- **Medium**: 900px
- **Large**: 1200px
- **Full**: 100%

---

## Animation & Transitions

### Standard Transition
```css
transition: all 0.3s ease;
```

### Hover Elevations
```css
transform: translateY(-5px);
transition: transform 0.3s ease;
```

---

## Accessibility

### Contrast Ratios
- Primary text on dark background: **WCAG AA compliant**
- Secondary text on dark background: **WCAG AA compliant**
- Accent colors provide sufficient contrast for interactive elements

### Focus States
Always provide visible focus indicators:
```css
outline: 2px solid #6B48FF;
outline-offset: 2px;
```

---

## CSS Variables Reference

```css
:root {
  --primary-accent: #6B48FF;
  --secondary-accent: #00C9A7;
  --neutral-background-dark: #1A1A2E;
  --neutral-background-light: #2C2C4A;
  --neutral-background-subtle: #3D3D5E;
  --text-primary: #E0E0E0;
  --text-secondary: #A0A0B0;
  --text-cta: #FFFFFF;
  --success: #00C9A7;
  --warning: #FFC107;
  --error: #DC3545;
}
```

---

## Implementation Notes

1. **Dark Mode First**: All components are designed for dark mode by default
2. **Consistent Spacing**: Use the spacing scale for margins and padding
3. **Elevation**: Use box-shadows to create depth hierarchy
4. **Interactive Feedback**: All interactive elements should have hover and focus states
5. **Loading States**: Disabled buttons should have reduced opacity (0.6) and "not-allowed" cursor

---

## Future Considerations

- Light mode variant (optional)
- Color blindness accessibility testing
- High contrast mode support
- Custom focus indicators for keyboard navigation
- Animation preferences (respect `prefers-reduced-motion`)
