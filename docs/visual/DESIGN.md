---
name: Inspector Safety Investigative System
colors:
  surface: '#08151a'
  surface-dim: '#08151a'
  surface-bright: '#2e3b41'
  surface-container-lowest: '#041015'
  surface-container-low: '#111d22'
  surface-container: '#152127'
  surface-container-high: '#1f2c31'
  surface-container-highest: '#2a373c'
  on-surface: '#d7e5ec'
  on-surface-variant: '#becab9'
  inverse-surface: '#d7e5ec'
  inverse-on-surface: '#263238'
  outline: '#889484'
  outline-variant: '#3f4a3d'
  surface-tint: '#71dd77'
  primary: '#71dd77'
  on-primary: '#00390d'
  primary-container: '#37a547'
  on-primary-container: '#00320a'
  inverse-primary: '#006e22'
  secondary: '#ffb4ab'
  on-secondary: '#690006'
  secondary-container: '#bb0213'
  on-secondary-container: '#ffc8c1'
  tertiary: '#8ed4c7'
  on-tertiary: '#003731'
  tertiary-container: '#589d91'
  on-tertiary-container: '#00302a'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#8dfa91'
  primary-fixed-dim: '#71dd77'
  on-primary-fixed: '#002105'
  on-primary-fixed-variant: '#005317'
  secondary-fixed: '#ffdad6'
  secondary-fixed-dim: '#ffb4ab'
  on-secondary-fixed: '#410002'
  on-secondary-fixed-variant: '#93000c'
  tertiary-fixed: '#a9f0e3'
  tertiary-fixed-dim: '#8ed4c7'
  on-tertiary-fixed: '#00201c'
  on-tertiary-fixed-variant: '#005047'
  background: '#08151a'
  on-background: '#d7e5ec'
  surface-variant: '#2a373c'
  paper-warm: '#FDE2CF'
  terracotta-accent: '#F3997B'
  deep-industrial: '#14312B'
  safety-blue: '#5BABB3'
  text-on-light: '#000000'
typography:
  display-lg:
    fontFamily: Open Sans
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Open Sans
    fontSize: 20px
    fontWeight: '700'
    lineHeight: 28px
    letterSpacing: '0'
  body-base:
    fontFamily: Open Sans
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 22px
    letterSpacing: '0'
  body-bold:
    fontFamily: Open Sans
    fontSize: 14px
    fontWeight: '700'
    lineHeight: 22px
    letterSpacing: '0'
  label-caps:
    fontFamily: Open Sans
    fontSize: 12px
    fontWeight: '700'
    lineHeight: 16px
    letterSpacing: 0.05em
  stamp-lg:
    fontFamily: Open Sans
    fontSize: 24px
    fontWeight: '800'
    lineHeight: 24px
    letterSpacing: 0.1em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  base-unit: 4px
  gutter: 16px
  margin-desktop: 48px
  panel-padding: 24px
---

## Brand & Style

The design system is built for a technical investigation simulator, blending the rigid, institutional authority of IFFluminense with the tactile, bureaucratic tension of a field safety inspector. The aesthetic is a hybrid of **Brutalism** and **Tactile Design**, emphasizing raw functionality, high-contrast legibility, and physical metaphors like clipboards, rubber stamps, and industrial monitors.

The interface evokes the feeling of a "field workstation"—a place where technical data meets high-stakes decision-making. It prioritizes clarity over decoration, using solid shapes and a structured grid to simulate the methodical nature of work safety inspections. The emotional response is one of focus, responsibility, and the weight of official duty.

## Colors

The palette is strictly anchored by the **Institutional Green** and **Institutional Red**. These are not merely decorative; they serve as functional indicators of "Safe/Compliant" and "Danger/Violation."

- **Default Mode:** Dark. The core environment (backgrounds and HUD) uses `neutral` (#0A171C) and `deep-industrial` (#14312B) to simulate a low-light control room environment.
- **Primary (Green):** Reserved for the IFF brand and "Approve/Safe" actions.
- **Secondary (Red):** Reserved for "Interdict/Danger" actions and critical errors.
- **Tertiary (Petroleum):** Used for header backgrounds and structural UI elements.
- **Paper Warm:** A tactile neutral used exclusively for active investigation documents (forms, clipboards, reports) to provide high contrast against the dark background and a "physical" feel.

## Typography

This design system exclusively utilizes **Open Sans** to maintain institutional compliance. The hierarchy is designed for speed and clarity under the pressure of timed gameplay.

- **Scale:** Larger sizes are used for system-level navigation and the "Official Stamp" aesthetics.
- **Stamps:** The `stamp-lg` role is used for decision-making outcomes (e.g., "INTERDITADO"), mimicking the heavy weight of a physical ink stamp.
- **Readability:** Body text uses a generous line-height (22px) to ensure technical safety descriptions remain legible during intense investigation phases.
- **Labels:** Uppercase labels with increased letter spacing are used for checkboxes and metadata to create a "technical log" appearance.

## Layout & Spacing

The layout follows a **Fixed Grid** model optimized for 16:9 desktop displays (1920x1080). It uses a "split-desk" approach:

- **Left Panel (60%):** The "Observation Deck." Contains the visual evidence viewport and technical site reports.
- **Right Panel (40%):** The "Inspector's Clipboard." A tactile document area for checklist interaction and final decision stamps.
- **Rhythm:** A 4px base unit ensures mathematical precision. Margin and padding are generous within investigation documents (`panel-padding`) to prevent visual clutter, while HUD elements are tightly packed to simulate industrial instrumentation.

## Elevation & Depth

Visual hierarchy is achieved through **Tonal Layers** and **Solid Shadows**, eschewing soft blurs for a more "printed" or "analog" look:

- **Surface Tiers:** Backgrounds are the deepest tier (`#0A171C`). Tactical panels (clipboards) sit above the background with no blur, but with a **2px offset solid shadow** in a darker tint of the background color.
- **Investigation Docs:** These use the `paper-warm` color to naturally "pop" forward in the Z-axis against the dark background.
- **Outlines:** Low-contrast outlines (1px solid) in `#1D4940` are used to define the boundaries of paper documents and input fields, reinforcing the flat, structural style.

## Shapes

The shape language is **Soft (0.25rem)** to suggest industrial durability without being overly aggressive. 

- **Hard Edges:** Most large containers (Relief/Clipboard) use the base `rounded-sm` (2px) or `0px` (sharp) to maintain a bureaucratic, rigid feel.
- **Action Elements:** Buttons and interactive chips use `0.25rem` (Soft) to make them identifiable as interactive objects.
- **Stamps:** Rectangular outlines for decision carimbos must remain perfectly sharp (0px) to mimic physical rubber stamps.

## Components

### Buttons
- **Primary Action:** Solid `#2F9E41` background, `#FDE2CF` text. Rectangular with minimal rounding.
- **Danger Action:** Solid `#CD191E` background.
- **Tactile Toggle:** Checkboxes are large (24x24px) for desktop precision, using a heavy 2px border and a sharp "X" mark for selection.

### The "Inspector's Clipboard" (Cards)
Cards are the primary gameplay vehicle. They use the `paper-warm` background with a `#1D4940` border. Headers should be a solid block of `#19655B` with white text to separate metadata from the body.

### Stamps (Decision Elements)
A unique component to this system. Stamps are text-only with heavy borders, rotated between 3 to 5 degrees. 
- **ADVERTIR:** Uses `#F3997B`.
- **INTERDITAR:** Uses `#CD191E`.

### Media Viewport
A framed area for evidence. It uses a thick 4px border in `#19655B` and a background of `#000000` to make site photos or videos the focus.

### Institutional Footer
The brand logo must reside in the bottom-right of non-gameplay screens (Menu, Loading) with a clear safety zone equal to the size of the logo's red square.
