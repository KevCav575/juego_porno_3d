---
name: Clinical Assurance
colors:
  surface: '#faf8ff'
  surface-dim: '#d2d9f4'
  surface-bright: '#faf8ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f3ff'
  surface-container: '#eaedff'
  surface-container-high: '#e2e7ff'
  surface-container-highest: '#dae2fd'
  on-surface: '#131b2e'
  on-surface-variant: '#434655'
  inverse-surface: '#283044'
  inverse-on-surface: '#eef0ff'
  outline: '#737686'
  outline-variant: '#c3c6d7'
  surface-tint: '#0053db'
  primary: '#004ac6'
  on-primary: '#ffffff'
  primary-container: '#2563eb'
  on-primary-container: '#eeefff'
  inverse-primary: '#b4c5ff'
  secondary: '#006a61'
  on-secondary: '#ffffff'
  secondary-container: '#86f2e4'
  on-secondary-container: '#006f66'
  tertiary: '#784b00'
  on-tertiary: '#ffffff'
  tertiary-container: '#996100'
  on-tertiary-container: '#ffeedd'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dbe1ff'
  primary-fixed-dim: '#b4c5ff'
  on-primary-fixed: '#00174b'
  on-primary-fixed-variant: '#003ea8'
  secondary-fixed: '#89f5e7'
  secondary-fixed-dim: '#6bd8cb'
  on-secondary-fixed: '#00201d'
  on-secondary-fixed-variant: '#005049'
  tertiary-fixed: '#ffddb8'
  tertiary-fixed-dim: '#ffb95f'
  on-tertiary-fixed: '#2a1700'
  on-tertiary-fixed-variant: '#653e00'
  background: '#faf8ff'
  on-background: '#131b2e'
  surface-variant: '#dae2fd'
typography:
  display-hero:
    fontFamily: Manrope
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  display-hero-mobile:
    fontFamily: Manrope
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg:
    fontFamily: Manrope
    fontSize: 36px
    fontWeight: '600'
    lineHeight: 44px
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Manrope
    fontSize: 26px
    fontWeight: '600'
    lineHeight: 34px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Manrope
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Manrope
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  title-md:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 26px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.02em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1.5rem
  gutter-mobile: 1rem
  margin: 2rem
  margin-mobile: 1.25rem
  margin-desktop: 3rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2rem
  space-2xl: 3rem
  space-3xl: 4.5rem
---

## Brand & Style

This design system establishes an empathetic, clinically rigorous, and reassuring visual language for preventive medical assessment. It merges the structure of modern health software with the approachability needed to put patients at ease during potentially stressful evaluations. 

The aesthetic is anchored in Corporate / Modern clinical minimalism. Surfaces are kept clean and bright to communicate hygiene, diagnostic precision, and organizational trust. Information density is calibrated to prevent cognitive overload, emphasizing high legibility, generous breathing room, and clear progression states.

Emotional drivers:
- **Trust & Competence**: Crisp alignments, authoritative typography, and clinical-grade color harmony.
- **Empathy & Reassurance**: Approachable soft corners, low-stress color transitions, and humane copy presentation.
- **Accessibility & Agency**: Large touch targets, immediate visual validation, and plain-language metric visualization designed across multi-generational demographics.

## Colors

The palette balances authoritative medical blue with preventive mint/teal to reduce clinical anxiety while maintaining diagnostic credibility.

- **Primary (`#2563EB`)**: Anchor color for primary actions, current active stages, brand touchpoints, and trusted anchor elements.
- **Secondary (`#0D9488`)**: Mint/teal accent used to signal positive health indicators, completed steps, verified security badges, and low-risk diagnostic states.
- **Tertiary (`#F59E0B`)**: Subtle amber reserved specifically for moderate risk alerts, lifestyle recommendations, and attention-needed notifications.
- **Neutral (`#0F172A`)**: Deep slate neutral ensuring high-contrast text hierarchies against pristine light backdrops. Secondary text resolves to slate-600 (`#475569`) and subtle borders map to slate-200 (`#E2E8F0`).
- **Semantic Red (`#EF4444`)**: Critical/elevated risk markers, error boundaries, and high-priority medical warnings.
- **Background (`#F8FAFC`)**: Ultra-clean hospital-grade slate white providing soft contrast against pure white (`#FFFFFF`) card surfaces.

## Typography

The typographic hierarchy combines the warm, geometric legibility of **Manrope** for headers with the high-performance utilitarian neutrality of **Inter** for clinical data and body copy.

- **Manrope**: Chosen for headlines, titles, and score displays. Its open apertures and friendly curves make clinical metrics approachable without sacrificing institutional authority.
- **Inter**: Drives readability across assessments, patient disclaimers, input elements, and microcopy. Its x-height and robust structural contrast maintain high legibility across older demographics and varied screen calibrations.
- **Readability Rules**: All body text must maintain a minimum contrast ratio of 4.5:1 against surfaces. Critical risk metrics prioritize semi-bold to bold weights for instantaneous comprehension.

## Layout & Spacing

The layout is built upon an 8pt architectural rhythm, structuring content into a balanced, centered grid that reduces horizontal eye travel during assessments.

- **Grid Model**: 12-column grid on desktop (max width: 1200px) with 24px gutters; 8-column layout on tablet with 20px gutters; 4-column layout on mobile with 16px gutters.
- **Vertical Rhythm**: Section layouts rely on `space-2xl` to `space-3xl` gaps, preventing clinical clutter and delivering an uncluttered, reassuring landing environment.
- **Assessment Flow**: Medical questionnaires, risk sliders, and step flows are constrained to a focused single-column maximum width of 680px to center attention and simplify cognitive throughput.

## Elevation & Depth

Elevation conveys cleanliness, separation, and gentle interaction rather than physical weight. The strategy uses soft, cool-tinted ambient shadows layered on pure white cards over the `#F8FAFC` base surface.

- **Level 0 (Flat)**: Baseline canvas (`#F8FAFC`) and neutral container insets.
- **Level 1 (Card Default)**: `0 1px 3px 0 rgba(15, 23, 42, 0.05), 0 1px 2px -1px rgba(15, 23, 42, 0.03)` with a 1px solid border (`#E2E8F0`). Used for clinical assessment cards, trust signals, and informative content blocks.
- **Level 2 (Hover & Active States)**: `0 10px 15px -3px rgba(15, 23, 42, 0.06), 0 4px 6px -4px rgba(15, 23, 42, 0.03)`. Reserved for selected options, active input modules, and interactive preview steps.
- **Level 3 (Modals & Sticky Headers)**: `0 20px 25px -5px rgba(15, 23, 42, 0.08), 0 8px 10px -6px rgba(15, 23, 42, 0.03)`. Used for dynamic risk breakdowns, diagnostic tooltips, and floating completion triggers.

## Shapes

The roundedness level is strictly set to **2 (Rounded)**:
- Standard components (buttons, input fields, checkboxes): `0.5rem` (8px).
- Content containers, interactive selection panels, and cards: `rounded-lg` (`1rem` / 16px).
- Diagnostic dashboards, feature heroes, and modal dialogs: `rounded-xl` (`1.5rem` / 24px).
- Badges, status chips, and step indicators: Full pill radii (`9999px`) to create clear semantic differentiation from rectangular data cards.

This geometry maintains clinical precision while softening the experience to welcome and reassure the patient.

## Components

### Buttons
- **Primary CTA**: Background `#2563EB`, text `#FFFFFF`, rounded 8px (`roundedness: 2`), font weight 600. Includes subtle hover shift to `#1D4ED8` and clear 2px focus ring (`#93C5FD`). Padding: 12px 24px for desktop, minimum height 48px to satisfy touch standards.
- **Secondary / Ghost**: White background, 1px border (`#E2E8F0`), text `#0F172A`. Hover background `#F1F5F9`.

### Chips & Badges
- **Status / Risk Chips**: Pill-shaped (`9999px`), padding 4px 12px, font size 12px bold.
  - *Low Risk*: Mint background (`#CCFBF1`), text `#0F766E`.
  - *Moderate Risk*: Amber background (`#FEF3C7`), text `#B45309`.
  - *High Risk*: Soft red background (`#FEE2E2`), text `#B91C1C`.
- **Trust Badges**: White background, subtle border, containing clinical shield/lock icons paired with teal accents.

### Form Inputs & Checkboxes
- **Input Fields**: Crisp `#FFFFFF` background, 1px border `#CBD5E1`, rounded 8px. Height 48px with 16px horizontal padding. Active focus transitions border to `#2563EB` with a soft blue halo shadow.
- **Selection Cards (Radio/Check alternatives)**: Large touch cards (minimum 64px height) featuring integrated icon, title, and description. Unselected: 1px border `#E2E8F0`. Selected: 2px border `#2563EB` with a subtle `#EFF6FF` tint.

### Interactive Step Indicator
- Linear stepper situated at the top of the assessment. Completed steps feature `#0D9488` with checkmark icons; active step features `#2563EB` with bold numbering; upcoming steps display subtle `#94A3B8` outlines over light slate backgrounds. Connecting tracks animate progressively via teal fill.

### Cards & Medical Risk Visualizers
- **Cards**: Surface `#FFFFFF`, border `#E2E8F0`, rounded 16px (`rounded-lg`), Level 1 elevation.
- **Metric Meter**: Continuous horizontal gauge transitioning smoothly from teal (`#0D9488`) to amber (`#F59E0B`) to coral (`#EF4444`), overlaid with an ergonomic marker displaying the calibrated risk percentile.