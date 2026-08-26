# TyresVision — Design System

Extracted from the live styles in [index.php](index.php) (`<style>` block, lines 133–488). This is the single source of truth for colors, type, spacing, and components — change a token in `:root` and the whole page follows.

---

## 1. Brand Colors

All tokens are defined once in `:root` (index.php:139-154).

| Token | Hex / Value | Usage |
|---|---|---|
| `--green` | `#58B31B` | Logo green — primary brand color, WhatsApp CTA background, dots, accents |
| `--green-bright` | `#68C927` | Hover state for green buttons/highlights |
| `--green-deep` | `#35760F` | Accessible green for text on white (icons, eyebrow labels, links, FAQ chevrons) |
| `--green-tint` | `#EFF9E6` | Icon well backgrounds, avatar backgrounds, focus-ring glow |
| `--ink` | `#0E1108` | Logo black — primary text color, "Call" button background, footer background |
| `--ink-2` | `#191F12` | Secondary dark shade (hero gradient end, brand pill text) |
| `--slate` | `#4C5548` | Secondary/muted text (leads, card copy, labels) |
| `--line` | `#E3E7DE` | Borders, dividers, card outlines |
| `--bg` | `#FFFFFF` | Page background |
| `--bg-soft` | `#F6F8F3` | Section background (alternating sections: stats, services, FAQ) |

**Derived / inline colors used elsewhere:**
- `#0B1505` — near-black text on green buttons (WhatsApp CTA, "more brands" pill) for AAA contrast
- `#96E05C` — hero eyebrow text (lighter green for dark backgrounds)
- `#23300F`, `#2F5A12` — final-CTA section gradient stops
- `rgba(255,255,255,.66/.5/.72/.82/.85/.9/.93/.94)` — white text at varying opacity on dark surfaces
- Theme color (browser chrome): `#0E1108`

### Color Usage Rules
- **Green is an accent, not a fill.** It marks CTAs (WhatsApp), active/positive states (checkmarks, dots), and small brand touches (icon wells, borders). Large surfaces stay white/`--bg-soft`/`--ink`.
- **Text on green must be near-black** (`#0B1505`), never white — green doesn't pass contrast with white text.
- **`--green-deep`**, not `--green`, is used for green *text* on white backgrounds (better contrast ratio).
- Dark sections (hero, final CTA, footer) use `--ink` → `--ink-2` gradients, not flat black.

---

## 2. Typography

```css
--font: "Inter","Segoe UI",system-ui,-apple-system,"Helvetica Neue",Arial,sans-serif;
```
Inter is requested but **not loaded via `@font-face`/Google Fonts link** — it silently falls back to the OS system font stack unless Inter happens to be installed locally. *(Consider adding a Google Fonts `<link>` for Inter if true brand consistency across all OSes matters.)*

Body defaults: `font-size: 17px`, `line-height: 1.6`, antialiased.

### Type Scale

| Element | Size | Weight | Notes |
|---|---|---|---|
| `h1` | `clamp(2.1rem, 5.2vw, 3.5rem)` | 800 | `line-height:1.15`, `letter-spacing:-.02em`, fluid/responsive |
| `h2` | `clamp(1.6rem, 3.4vw, 2.35rem)` | 800 | same line-height/tracking as h1 |
| `h3` | `1.1rem` | 700 | `letter-spacing:-.01em` |
| Body / `p` | `17px` (1rem) | 400 | `line-height:1.6` |
| `.lead` | `clamp(1.02rem, 1.5vw, 1.18rem)` | 400 | color `--slate`, `max-width:62ch` |
| `.eyebrow` | `.75rem` | 700 | uppercase, `letter-spacing:.12em`, color `--green-deep` |
| Logo wordmark | `1.24rem` (`.lg`: `1.8rem`) | 900 italic | `letter-spacing:-.02em` |
| Buttons | `1rem` (`.btn-sm`: `.92rem`) | 700 | |
| Stat numbers | `clamp(1.7rem, 3.6vw, 2.3rem)` | 800 | `letter-spacing:-.03em` |
| Stat labels | `.85rem` | 600 | color `--slate` |
| Nav links | `.94rem` | 600 | |
| Field labels | `.79rem` | 700 | uppercase, `letter-spacing:.07em` |
| Card body copy | `.96rem` | 400 | color `--slate` |
| Small print (form note, tagline) | `.78rem`–`.79rem` | 700 | |

### Typographic Principles
- **Headings are tight and bold** (weight 800, negative letter-spacing) — confident, not delicate.
- **Fluid sizing via `clamp()`** on every heading and the lead paragraph — no fixed breakpoint jumps, scales smoothly from mobile to desktop.
- **Eyebrows** (uppercase, letter-spaced, small, green) precede every section heading as a consistent "kicker" pattern.
- Long-form text is capped with `max-width: Nch` (leads at `62ch`, footer notice at `78ch`) to keep line length readable.
- The logo uses a **mixed-typeface trick**: "TYRES" in Georgia serif (`--ink`), "VISION" in the sans brand font (`--green`), with a circular "O" (`.oring`) styled to echo a tyre.

---

## 3. Layout & Spacing

| Token | Value |
|---|---|
| `--maxw` | `1280px` — global content max-width (`.wrap`) |
| `--radius` | `14px` — default corner radius (cards, steps) |
| Page gutter | `20px` (`.wrap` padding) |
| Section padding | `clamp(52px, 7vw, 88px)` vertical |
| Grid gaps | `12–18px` (responsive: smaller on mobile, larger ≥560px) |

### Border Radius Scale
- `10px` — form inputs
- `11–12px` — icon wells, service pills, FAQ items
- `14px` (`--radius`) — cards, steps, stats block
- `16px` — modal sheet
- `20px` — quote card (hero)
- `100px` (pill) — buttons, badges, brand tags

### Shadow
```css
--shadow: 0 1px 2px rgba(14,17,8,.06), 0 8px 24px rgba(14,17,8,.09);
```
A soft two-layer shadow (tight + diffuse) used on hover states for cards/steps. Larger custom shadows are used for elevated surfaces: quote card (`0 24px 60px rgba(0,0,0,.34)`), modal sheet (`0 30px 80px rgba(0,0,0,.42)`), mobile sticky CTA bar (`0 -6px 24px rgba(14,17,8,.11)`), floating WhatsApp button (`0 10px 30px rgba(88,179,27,.5)`).

---

## 4. Components

### Buttons (`.btn`)
Pill-shaped (`border-radius:100px`), bold, `padding:15px 26px`, subtle lift on hover (`translateY(-2px)`).

| Variant | Background | Text | Use |
|---|---|---|---|
| `.btn-wa` | `--green` → `--green-bright` on hover | `#0B1505` | Primary CTA (WhatsApp) |
| `.btn-call` | `--ink` → `#000` on hover | `#fff` | Secondary CTA (phone) |
| `.btn-ghost` | transparent, `--line` border → `--ink` border on hover | `--ink` | Tertiary, on light backgrounds |
| `.btn-ghost-light` | transparent, translucent white border | `#fff` | Tertiary, on dark backgrounds (hero) |
| `.btn-white` | `#fff` → `#F1F4EC` on hover | `--ink` | On dark backgrounds needing a solid button |
| `.btn-sm` | — | — | Compact modifier (`11px 18px`, `.92rem`) |

Focus state: `outline:3px solid var(--ink); outline-offset:3px` (accessibility).

### Cards (`.card`)
White surface, `1px solid --line` border, `--radius` corners, `26px 24px` padding. On hover: `--shadow`, border darkens to `#CBD6C0`, lifts `-2px`. Icon well (`.icon`) is a `44×44px` rounded square in `--green-tint` with `--green-deep` icon color.

### Pills / Badges
- `.pill` — translucent white on dark hero background, used for trust badges ("Lowest price guaranteed" etc.)
- `.brand` — white pill with border for brand-name tags; `.brand.more` inverts to solid green
- `.eyebrow` — text-only label, not boxed

### Form Fields (`.field`)
`13px 14px` padding, `1.5px solid --line`, `10px` radius. Focus state: green border + `0 0 0 3px var(--green-tint)` glow ring — this glow-ring pattern is the standard focus treatment across the design.

### Stats Bar
4-column grid (2-col on mobile) with `1px` hairline gaps that form a grid via background color trick (`background:--line` behind white cells).

### Steps / Numbered Cards
Like `.card` but with a circular numbered badge (`.step-num`) pinned top-right, `--green-tint` background + `--green-deep` text.

### FAQ (`<details>`/`<summary>`)
Custom chevron built from two rotated borders in `--green-deep`, rotates 180° on `[open]`.

### Modal (`.notice-modal`)
White sheet, `16px` radius, `5px` solid green top accent bar, dark blurred backdrop (`rgba(8,12,5,.62)`, `blur(3px)`).

### Dark Sections (Hero / Final CTA / Footer)
Diagonal gradients between `--ink`, `--ink-2`, and green tones, topped with a repeating diagonal-stripe accent bar (`repeating-linear-gradient(90deg, var(--green) 0 26px, #fff 26px 52px)`) evoking a tyre tread pattern.

### Mobile-Only Elements
- `.mobile-cta` — fixed two-button bar pinned to viewport bottom, hidden ≥820px
- `.float-wa` — floating circular WhatsApp button, bottom-right, shown only ≥820px (desktop)

---

## 5. Motion

- Buttons/cards: `transform .12s–.18s ease` lift on hover, plus color/border/shadow transitions (`.15s–.18s ease`)
- Smooth anchor scrolling (`html{scroll-behavior:smooth}`)
- `@media (prefers-reduced-motion: reduce)` — all animation/transition/smooth-scroll disabled for users who request it

---

## 6. Responsive Breakpoints

| Breakpoint | Purpose |
|---|---|
| `max-width:460px` | Small-phone safety net — tighter nav/button padding, single-column form rows |
| `max-width:559px` | Compact card/quote padding |
| `min-width:560px` | Grid gap increases to 18px |
| `min-width:700px` | Services grid → 3 columns |
| `min-width:760px` | Footer grid → 3 columns, steps → 4 columns |
| `min-width:820px` | Sticky mobile CTA hides, floating WhatsApp button shows, header WhatsApp button shows |
| `min-width:900px` | Hero becomes 2-column (1.12fr / .88fr) |
| `min-width:980px` | Nav links visible, 3-column "why us" grid |
| `min-width:1000px` | Services grid → 4 columns |

Mobile-first: base styles target the smallest screens, with `body{padding-bottom:76px}` reserved for the sticky mobile CTA bar (removed ≥820px).

---

## 7. Iconography

Inline SVGs, `stroke`/`fill:currentColor` so they inherit context color. Consistent sizing: `14–22px` depending on context (pill icon = 14px, card icon = 22px, nav button icon = 16–17px). No icon font or external icon library — all hand-drawn inline paths (WhatsApp glyph, phone glyph, checkmarks, category icons).

---

## 8. Accessibility Notes Baked Into the CSS

- Skip-to-content link (`.skip`), visually hidden until focused
- All interactive elements have visible `:focus-visible` outlines (`--ink` or `--green-deep`, `3px`, offset)
- Text-on-green always uses near-black (`#0B1505`) for contrast, never white
- `--green-deep` (not `--green`) used for text to meet contrast on white
- `prefers-reduced-motion` respected globally

---

## 9. Quick Reference — Copy-Paste Tokens

```css
:root{
  --green:#58B31B;
  --green-bright:#68C927;
  --green-deep:#35760F;
  --green-tint:#EFF9E6;
  --ink:#0E1108;
  --ink-2:#191F12;
  --slate:#4C5548;
  --line:#E3E7DE;
  --bg:#FFFFFF;
  --bg-soft:#F6F8F3;
  --radius:14px;
  --shadow:0 1px 2px rgba(14,17,8,.06), 0 8px 24px rgba(14,17,8,.09);
  --maxw:1280px;
  --font:"Inter","Segoe UI",system-ui,-apple-system,"Helvetica Neue",Arial,sans-serif;
}
```
