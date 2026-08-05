---
name: Inspector Safety Investigative System
color-schemes:
  dark:
    name: Dark Mode (v2 — Dart)
    colors:
      surface: '#121414'
      surface-dim: '#121414'
      surface-bright: '#38393a'
      surface-container-lowest: '#0c0f0f'
      surface-container-low: '#1a1c1c'
      surface-container: '#1e2020'
      surface-container-high: '#282a2b'
      surface-container-highest: '#333535'
      on-surface: '#e2e2e2'
      on-surface-variant: '#becab9'
      inverse-surface: '#e2e2e2'
      inverse-on-surface: '#2f3131'
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
      tertiary: '#8dd2d8'
      on-tertiary: '#00363a'
      tertiary-container: '#569ba1'
      on-tertiary-container: '#002f32'
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
      tertiary-fixed: '#a9eef4'
      tertiary-fixed-dim: '#8dd2d8'
      on-tertiary-fixed: '#002022'
      on-tertiary-fixed-variant: '#004f54'
      background: '#121414'
      on-background: '#e2e2e2'
      surface-variant: '#333535'
  light:
    name: Light Mode
    colors:
      surface: '#f9f9f9'
      surface-dim: '#dadada'
      surface-bright: '#f9f9f9'
      surface-container-lowest: '#ffffff'
      surface-container-low: '#f4f3f3'
      surface-container: '#eeeeee'
      surface-container-high: '#e8e8e8'
      surface-container-highest: '#e2e2e2'
      on-surface: '#1a1c1c'
      on-surface-variant: '#3f4a3d'
      inverse-surface: '#2f3131'
      inverse-on-surface: '#f1f1f1'
      outline: '#6f7a6b'
      outline-variant: '#becab9'
      surface-tint: '#006e22'
      primary: '#006b21'
      on-primary: '#ffffff'
      primary-container: '#09872d'
      on-primary-container: '#f7fff1'
      inverse-primary: '#71dd77'
      secondary: '#bb0213'
      on-secondary: '#ffffff'
      secondary-container: '#e02a29'
      on-secondary-container: '#fffbff'
      tertiary: '#17666b'
      on-tertiary: '#ffffff'
      tertiary-container: '#387f84'
      on-tertiary-container: '#f4feff'
      error: '#ba1a1a'
      on-error: '#ffffff'
      error-container: '#ffdad6'
      on-error-container: '#93000a'
      primary-fixed: '#8dfa91'
      primary-fixed-dim: '#71dd77'
      on-primary-fixed: '#002105'
      on-primary-fixed-variant: '#005317'
      secondary-fixed: '#ffdad6'
      secondary-fixed-dim: '#ffb4ab'
      on-secondary-fixed: '#410002'
      on-secondary-fixed-variant: '#93000c'
      tertiary-fixed: '#a9eef4'
      tertiary-fixed-dim: '#8dd2d8'
      on-tertiary-fixed: '#002022'
      on-tertiary-fixed-variant: '#004f54'
      background: '#f9f9f9'
      on-background: '#1a1c1c'
      surface-variant: '#e2e2e2'
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
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base-unit: 4px
  gutter: 16px
  margin-sm: 16px
  margin-lg: 24px
  deck-width: 60%
  clipboard-width: 40%
---

## Brand & Style

The design system is built for a technical investigation simulator, blending the rigid, institutional authority of IFFluminense with the tactile, bureaucratic tension of a field safety inspector. The aesthetic is a hybrid of **Brutalism** and **Tactile Design**, emphasizing raw functionality, high-contrast legibility, and physical metaphors like clipboards, rubber stamps, and industrial monitors.

The interface evokes the feeling of a "field workstation"—a place where technical data meets high-stakes decision-making. It prioritizes clarity over decoration, using solid shapes and a structured grid to simulate the methodical nature of work safety inspections. The emotional response is one of focus, responsibility, and the weight of official duty.

## Colors

The palette is strictly anchored by the **Institutional Green** and **Institutional Red**. These are not merely decorative; they serve as functional indicators of "Safe/Compliant" and "Danger/Violation."

The system defines two color schemes (see `color-schemes` in the frontmatter above):

### Dark Mode (Dart)
Dark variant with soft neutrals (`surface: #121414`) and warm on-surface text (`#e2e2e2`). Uses strict Material-like tokens without extra thematic colors. Primary green (`#71dd77`) and secondary red (`#ffb4ab`) are preserved for the dark palette. Tertiary is cyan (`#8dd2d8`). Uses moderate rounding (`DEFAULT 0.5rem`).

### Light Mode
Full-light variant with white/near-white surfaces (`surface: #f9f9f9`, `surface-container-lowest: #ffffff`). Primary green darkens for contrast (`#006b21`). Secondary red becomes `#bb0213` with white text. Tertiary shifts to deep teal (`#17666b`). Outlines are darker (`#6f7a6b`) for definition against light backgrounds. Uses the same moderate rounding and spacing as Dark Mode.

---

**Cross-mode constants:** In all schemes, the action-button greens and reds remain visually consistent:
- **Primary action:** Solid `#2F9E41` background
- **Danger action:** Solid `#CD191E` background
- **Stamp ADVERTIR:** Uses `#F3997B`
- **Stamp INTERDITAR:** Uses `#CD191E`

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
- **Rhythm:** A 4px base unit ensures mathematical precision. Margins use `margin-lg` (24px) within investigation documents to prevent visual clutter, while HUD elements are tightly packed to simulate industrial instrumentation.

## Elevation & Depth

Visual hierarchy is achieved through **Tonal Layers** and **Solid Shadows**, eschewing soft blurs for a more "printed" or "analog" look:

- **Surface Tiers:** The deepest tier is the background (`on-surface` on `surface`). Tactical panels (clipboards and cards) sit above the background with no blur, using a **2px offset solid shadow** in a darker tint of the surface color.
- **Document Pop-out:** Investigation documents use contrasting container colors (e.g., `surface-container-highest` in Dark Mode, or a distinct card surface in Light Mode) to naturally advance in the Z-axis.
- **Outlines:** Low-contrast outlines (1px solid) in `outline-variant` define the boundaries of paper documents and input fields, reinforcing the flat, structural style.

## Shapes

The shape language is **Moderate (0.5rem)** to balance industrial durability with modern visual ergonomics.

- **Hard Edges:** Most large containers (Relief/Clipboard) use `rounded-sm` (0.25rem) or `0px` (sharp) to maintain a bureaucratic, rigid feel.
- **Action Elements:** Buttons and interactive chips use `0.5rem` (DEFAULT) to make them identifiable as interactive objects.
- **Stamps:** Rectangular outlines for decision carimbos must remain perfectly sharp (0px) to mimic physical rubber stamps.

## Components

### Buttons
- **Primary Action:** Solid `#2F9E41` background, white (`#FFFFFF`) text. Rectangular with minimal rounding.
- **Danger Action:** Solid `#CD191E` background.
- **Tactile Toggle:** Checkboxes are large (24x24px) for desktop precision, using a heavy 2px border and a sharp "X" mark for selection.

### The "Inspector's Clipboard" (Cards)
Cards are the primary gameplay vehicle. They use a container surface (e.g., `surface-container` or `surface-container-highest`) with an `outline-variant` border. Headers should be a solid block of `primary-container` with `on-primary-container` text to separate metadata from the body.

### Stamps (Decision Elements)
A unique component to this system. Stamps are text-only with heavy borders, rotated between 3 to 5 degrees. 
- **ADVERTIR:** Uses `#F3997B`.
- **INTERDITAR:** Uses `#CD191E`.

### Media Viewport
A framed area for evidence. It uses a thick 4px border in `outline` and a background of `#000000` (Dark Mode) or a dark neutral (Light Mode) to make site photos or videos the focus.

### Institutional Footer
The brand logo must reside in the bottom-right of non-gameplay screens (Menu, Loading) with a clear safety zone equal to the size of the logo's red square.
