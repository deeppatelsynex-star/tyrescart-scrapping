# TyresVision — Colors & Typography

A focused reference for the two most-reused pieces of the design system: the color palette and the type scale. Both are extracted directly from the live `:root` tokens and CSS rules in [index.php](index.php) (`<style>` block, lines 139–170). For layout, spacing, components, and everything else, see the full [DESIGN-SYSTEM.md](DESIGN-SYSTEM.md).

---

## Colors

### Palette

| Swatch | Token | Hex | Role |
|---|---|---|---|
| 🟢 | `--green` | `#58B31B` | Primary brand color — sampled from the logo. CTAs (WhatsApp button), dots, small accents. |
| 🟢 | `--green-bright` | `#68C927` | Hover state for anything using `--green`. |
| 🟢 | `--green-deep` | `#35760F` | Accessible green for **text** on white — icons, eyebrow labels, links, FAQ chevrons. |
| 🟩 | `--green-tint` | `#EFF9E6` | Pale green fill for icon wells, avatar circles, focus-ring glow. |
| ⚫ | `--ink` | `#0E1108` | Primary text color / near-black — sampled from the logo. Also the "Call" button and footer background. |
| ⚫ | `--ink-2` | `#191F12` | Secondary dark shade — hero gradient end stop, brand-pill text. |
| ⬛ | `--slate` | `#4C5548` | Secondary/muted text — leads, card body copy, form labels. |
| ⬜ | `--line` | `#E3E7DE` | Borders, dividers, card outlines. |
| ⬜ | `--bg` | `#FFFFFF` | Page background. |
| ⬜ | `--bg-soft` | `#F6F8F3` | Alternating section background (stats, services, FAQ). |

### Colors used inline (not tokenized)

| Hex / value | Where | Why it exists |
|---|---|---|
| `#0B1505` | Text on `.btn-wa`, `.brand.more` | Near-black label on green background — passes ~8:1 contrast; white on green would not. |
| `#96E05C` | `.hero .eyebrow` | Lighter green tuned for legibility on the dark hero background. |
| `#23300F`, `#2F5A12` | `.final` gradient stops | Mid-tones between `--ink` and green for the final-CTA section's diagonal gradient. |
| `rgba(255,255,255, .5 – .94)` | Various text on dark surfaces (footer, hero, final CTA) | White at varying opacity instead of a flat gray, to keep it feeling like "white on black" rather than a separate gray token. |
| `#0E1108` | `<meta name="theme-color">` | Matches `--ink` so the mobile browser chrome blends with the header/footer. |
| `#CBD6C0` | `.card:hover` / `.step:hover` border | A darkened `--line` for the hover state, not worth its own token. |
| `#C0392B` | Form validation (JS) | One-off error-red for the empty-tyre-size field outline — the only non-brand color in the whole page. |

### How the palette is actually used

- **Green is an accent, never a fill.** No large surface is solid green — it appears in CTAs, dots, thin rules, icon wells, and borders. Big surfaces are always white, `--bg-soft`, or `--ink`.
- **Two greens for two jobs**: `--green` is for *backgrounds* (buttons, dots); `--green-deep` is for *text on white* (better contrast ratio at small sizes — eyebrows, links, icons on light cards).
- **Contrast rule, no exceptions**: text sitting on `--green` is always `#0B1505` (near-black), never white. Green and white together don't clear contrast requirements.
- **Dark sections aren't flat black.** Hero, final CTA, and footer all use a gradient rooted in `--ink` (`--ink` → `--ink-2`, or `--ink` → mid-tones → green for the final CTA) rather than a single flat fill — it's what gives those bands depth against the mostly-white page.
- **Neutrals lean warm-green, not true gray.** `--slate` (`#4C5548`) and `--line` (`#E3E7DE`) both carry a slight green cast rather than being neutral grays — this ties body text and borders back to the brand color even where green itself doesn't appear.

---

## Typography

### Font stack
```css
--font: "Inter","Segoe UI",system-ui,-apple-system,"Helvetica Neue",Arial,sans-serif;
```
**Note:** Inter is requested but not actually loaded (no `@font-face` or Google Fonts `<link>` anywhere in the page) — every visitor without Inter installed locally sees their OS default (Segoe UI on Windows, San Francisco on Mac, Roboto on Android, etc.) instead. If pixel-consistent branding across devices matters, add:
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap" rel="stylesheet">
```

### Base
| Property | Value |
|---|---|
| Base size | `17px` |
| Line height | `1.6` |
| Smoothing | `-webkit-font-smoothing: antialiased` |
| Text sizing | `-webkit-text-size-adjust: 100%` (prevents mobile Safari auto-zoom reflow) |

### Full type scale

| Element / class | Size | Weight | Line-height / Letter-spacing | Color |
|---|---|---|---|---|
| `h1` | `clamp(2.1rem, 5.2vw, 3.5rem)` | 800 | `1.15` / `-.02em` | `--ink` (white on hero) |
| `h2` | `clamp(1.6rem, 3.4vw, 2.35rem)` | 800 | `1.15` / `-.02em` | `--ink` (white on final CTA) |
| `h3` | `1.1rem` | 700 | `1.15` / `-.01em` | `--ink` |
| Body `p` | `1rem` (17px) | 400 | `1.6` | `--ink` |
| `.lead` | `clamp(1.02rem, 1.5vw, 1.18rem)` | 400 | `1.6` (inherited) | `--slate` |
| `.eyebrow` | `.75rem` | 700 | uppercase, `.12em` tracking | `--green-deep` |
| Logo wordmark `.word` | `1.24rem` (`.lg` variant: `1.8rem`) | 900, italic | `-.02em` tracking | mixed (see below) |
| `.btn` | `1rem` | 700 | — | variant-dependent |
| `.btn-sm` | `.92rem` | 700 | — | variant-dependent |
| Stat number `.stat b` | `clamp(1.7rem, 3.6vw, 2.3rem)` | 800 | `-.03em` tracking | `--ink` |
| Stat label `.stat span` | `.85rem` | 600 | — | `--slate` |
| Nav link | `.94rem` | 600 | — | `--slate` (→ `--green-deep` on hover) |
| Field label | `.79rem` | 700 | uppercase, `.07em` tracking | `--slate` |
| Card body `.card p` | `.96rem` | 400 | — | `--slate` |
| Quote-card subtitle `.sub` | `.9rem` | 400 | — | `--slate` |
| Form note | `.78rem` | 400 | — | `--slate` |
| Tagline | `.78rem` | 700, italic | `.01em` tracking | inherit |
| Pill text `.pill` | `.83rem` | 600 | — | `rgba(255,255,255,.93)` (on dark) |
| Brand tag `.brand` | `.9rem` | 700 | `-.01em` tracking | `--ink-2` |
| FAQ question `summary` | `1rem` | 700 | — | `--ink` |
| FAQ answer `.body` | `.96rem` | 400 | — | `--slate` |
| Footer heading `footer h4` | `.8rem` | 700 (default `<h4>` weight, uppercase applied) | uppercase, `.1em` tracking | `#fff` |
| Footer fine print `.f-notice` | `.79rem` | 400 | `1.6` | `rgba(255,255,255,.5)` |
| Modal title `.notice-modal h2` | `1.08rem` | 800 | `1.3` / `-.01em` | `--ink` |
| Modal timestamp `.stamp` | `.72rem` | 700 | uppercase, `.1em` tracking | `--slate` |

### Type principles

1. **Headings are heavy and tight.** Every heading (`h1`–`h3`, stat numbers) uses weight 700–800 with negative letter-spacing — the type reads as confident and dense rather than airy.
2. **Fluid scaling everywhere it matters.** `h1`, `h2`, `.lead`, and stat numbers all use `clamp()` so they scale continuously between a mobile floor and a desktop ceiling — no fixed breakpoint jump, no separate "mobile h1" override anywhere in the stylesheet.
3. **The eyebrow is a structural device, not decoration.** Every content section opens with the same `.eyebrow` pattern (tiny, bold, uppercase, letter-spaced, `--green-deep`) directly above its `h2` — it's the page's consistent "kicker" rhythm, and any new section should keep it.
4. **Line-length discipline.** Long-form text is always capped with a character-based `max-width` (`.lead` at `62ch`, the footer legal notice at `78ch`) rather than a pixel width, so it stays readable regardless of font-size changes.
5. **Two weights of "quiet" text.** `--slate` body copy sits at `.85rem`–`.96rem` depending on context (stat labels smaller, card copy larger) — there's no single "small text" size, it's tuned per component.
6. **The logo breaks the font system on purpose.** `.logo .t1` ("TYRES") renders in `Georgia, "Times New Roman", serif` — the only serif anywhere on the page — set against `.logo .t2` ("VISION") in the brand sans stack, colored `--green`. This mixed-typeface, mixed-color wordmark is a deliberate one-off; it should not be treated as a pattern to extend elsewhere.

---

## Copy-paste tokens

```css
:root{
  /* Color */
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

  /* Type */
  --font:"Inter","Segoe UI",system-ui,-apple-system,"Helvetica Neue",Arial,sans-serif;
}

body{
  font-family:var(--font);
  font-size:17px;
  line-height:1.6;
  color:var(--ink);
  -webkit-font-smoothing:antialiased;
}
h1,h2,h3{ line-height:1.15; letter-spacing:-.02em; margin:0 0 .5em; }
h1{ font-size:clamp(2.1rem,5.2vw,3.5rem); font-weight:800; }
h2{ font-size:clamp(1.6rem,3.4vw,2.35rem); font-weight:800; }
h3{ font-size:1.1rem; font-weight:700; letter-spacing:-.01em; }
.eyebrow{
  display:inline-block; font-size:.75rem; font-weight:700;
  letter-spacing:.12em; text-transform:uppercase; color:var(--green-deep);
  margin-bottom:14px;
}
.lead{ font-size:clamp(1.02rem,1.5vw,1.18rem); color:var(--slate); max-width:62ch; }
```
