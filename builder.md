# VisionAdmin Composable Section Builder — Architectural Solution & Implementation Plan

> **Document Status**: Architectural Solution & Technical Blueprint  
> **Target Files**: `builder.md`, `bilder.md`  
> **Objective**: Eliminate code modification when creating, extending, or mixing section layouts across TyresVision.

---

## 1. Executive Summary & Problem Analysis

### 1.1 The Core Bottlenecks
Currently, adding or extending page sections on TyresVision requires manual code changes across 4–5 different files:
1. **Hardcoded Frontend Dispatcher**: `templates/Client/Home.html` uses rigid Jinja blocks (`{% elif sec.section_type == 'advice' %}`). If a new section type is introduced, it will not display on the storefront until a developer writes new HTML and Jinja logic.
2. **Rigid Layout Silos**: Each section type is locked into a fixed schema:
   - `features` and `advice` only allow 3-column cards (`icon`, `title`, `description`).
   - `shop_by` only allows grouped chips (`heading`, `type`, `chips`).
   - `coverage` only allows 2 fixed service cards + area chips.
   - You cannot mix and match items (e.g., adding vehicle chips inside an advice section, or adding a secondary button, or adding a comparison box) without modifying JavaScript, HTML, and Python code.
3. **Missing Fields Limitation**: If an admin needs an extra field (e.g., a secondary CTA button, a promo badge, a callout banner, or custom highlight colors), there is no way to add it in the Section Builder without altering the database handling and JS packing scripts.

### 1.2 The Goal: Zero-Code Dynamic Composable Builder
Enable any administrator to:
- Create **unlimited new sections** from the admin dashboard with **zero code changes**.
- **Mix and match any components** (e.g., Cards + Chips + Comparison Cards + FAQs + Multiple Buttons) inside any single section.
- Freely add **custom attributes/fields** (secondary buttons, tags, highlight text, colors).
- Preview and publish instantly without deploying or editing code.

---

## 2. The Architectural Solution: Composable Block Engine

Instead of treating a Section as a **rigid, single-purpose type**, the system transitions to a **Container + Modular Block Stack** model (used by modern headless CMS engines like Strapi Dynamic Zones, Webflow, and Shopify Sections).

```
┌────────────────────────────────────────────────────────────────────────┐
│                        PAGE SECTION CONTAINER                          │
│  • Title (EN/AR)    • Subtitle/Eyebrow (EN/AR)   • Container Width     │
│  • Background Theme • Top/Bottom Padding         • Primary / Sec CTA   │
├────────────────────────────────────────────────────────────────────────┤
│  STACK OF MODULAR BLOCKS (Admin can add, remove, and reorder any):     │
│                                                                        │
│   [ BLOCK 1: Cards Grid ] ────────── 3 cols (Icons, Titles, Descs)    │
│                                                                        │
│   [ BLOCK 2: Chips Cloud ] ───────── Vehicle / Tyre Size Chips        │
│                                                                        │
│   [ BLOCK 3: Comparison Split ] ──── Centre Fitting vs Mobile Van      │
│                                                                        │
│   [ BLOCK 4: Accordion FAQ ] ─────── Collapsible Questions & Answers  │
│                                                                        │
│   [ BLOCK 5: Action Button Row ] ─── WhatsApp + Direct Phone Call      │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. The 10 Universal Atomic Building Blocks

By breaking all website sections into 10 reusable atomic blocks, any current or future section can be constructed without touching template code:

| Block Identifier | Block Name | Configurable Parameters | Use Cases |
|---|---|---|---|
| `cards_grid` | **Card Grid** | Columns (1, 2, 3, 4), Style (standard, bordered, glass, hover-glow), Items: `icon`, `tag`, `title`, `desc`, `link` | Why Us, Tyre Advice, Guarantee Cards, Value Props |
| `chips_cloud` | **Interactive Chips** | Layout (inline, wrap, grouped), Action (`whatsapp`, `filter`, `link`), Items: `label`, `value`, `icon` | Tyre Sizes, Vehicles, Brands, Area Coverage |
| `comparison_split` | **Service Comparison** | Cards count (2 or 3), Featured badge, Items: `badge`, `heading`, `desc`, `price_tag`, `button_text`, `button_url` | Centre vs Mobile Van, Plan Comparisons |
| `metrics_strip` | **Statistics Counter** | Columns (2, 3, 4), Items: `number`, `label`, `icon` | Stats bar, Trust counters, Milestone badges |
| `process_steps` | **Step Timeline** | Layout (horizontal, vertical), Items: `step_number`, `icon`, `title`, `desc`, `badge` | How It Works, Order Process, 4-Step Guide |
| `accordion_faq` | **Collapsible Accordion** | Open first by default (yes/no), Items: `question`, `answer` (Rich HTML) | FAQs, Technical Specs, Policies |
| `reviews_slider` | **Customer Reviews** | Layout (grid, slider), Items: `rating` (1-5), `quote`, `author`, `location`, `avatar` | Customer Testimonials, Reviews |
| `media_story` | **Media + Prose Split** | Alignment (`image_left`, `image_right`, `full_bleed`), `image_url`, `content` (Rich HTML), `bullet_points` | About Story, Warehouse Media, 2-Column Narratives |
| `pricing_matrix` | **Tabular Pricing** | Columns definitions, Rows: `size`, `vehicle`, `budget_price`, `mid_price`, `prem_price` | Tyre Size Price Matrix, Service Price Lists |
| `cta_actions` | **Action Button Group** | Alignment (center, left, right), Buttons list: `text`, `url`, `variant` (whatsapp, phone, white, dark, outline) | CTA Banners, Contact Buttons, Conversion Strips |

---

## 4. Universal Data Structure (`section_data`)

To maintain 100% backward compatibility with existing hardcoded sections while enabling unlimited dynamic sections, `section_data` supports the composable `blocks` array:

```json
{
  "theme": {
    "bg_style": "default", 
    "padding_y": "compact",
    "container_max_w": "1280px"
  },
  "blocks": [
    {
      "type": "cards_grid",
      "columns": 3,
      "items": [
        {
          "icon": "clock",
          "tag": { "en": "SAFETY", "ar": "أمان" },
          "title": { "en": "Check Manufacturing Date", "ar": "تحقق من تاريخ الصنع" },
          "description": { "en": "UAE heat ages rubber faster than tread...", "ar": "حرارة الإمارات تؤثر على المطاط..." }
        }
      ]
    },
    {
      "type": "chips_cloud",
      "group_title": { "en": "Popular Sizes", "ar": "مقاسات شائعة" },
      "action_type": "whatsapp",
      "chips": ["195/65 R15", "205/55 R16", "265/65 R17"]
    },
    {
      "type": "cta_actions",
      "buttons": [
        {
          "text": { "en": "WhatsApp Expert", "ar": "تواصل عبر واتساب" },
          "url": "https://wa.me/971505069575",
          "variant": "whatsapp"
        },
        {
          "text": { "en": "Call Support", "ar": "اتصال هاتف" },
          "url": "tel:+971505069575",
          "variant": "phone"
        }
      ]
    }
  ]
}
```

---

## 5. Storefront Universal Block Dispatcher

In `templates/Client/Home.html` (and any custom page like `About.html`), the renderer checks if the section has dynamic `blocks`. If so, it dispatches each block through a universal Jinja macro:

```jinja2
<!-- Check if section uses the Composable Block Engine -->
{% if sec.section_data and sec.section_data.blocks %}
  <section class="dynamic-section" id="section-{{ sec.id }}">
    <div class="wrap">
      <!-- Section Header -->
      {% if sec.section_title %}
        <div class="center mb-8">
          {% if sec.section_subtitle %}<span class="eyebrow">{{ sec.section_subtitle }}</span>{% endif %}
          <h2>{{ sec.section_title }}</h2>
          {% if sec.content %}<div class="lead">{{ sec.content | safe }}</div>{% endif %}
        </div>
      {% endif %}

      <!-- Dynamic Blocks Stack -->
      {% for block in sec.section_data.blocks %}
        {% include 'Client/components/blocks/' ~ block.type ~ '.html' ignore missing %}
      {% endfor %}
    </div>
  </section>

<!-- Backward Compatibility: Fallback to existing legacy hardcoded types -->
{% elif sec.section_type == 'hero' %}
  ...
{% elif sec.section_type == 'advice' %}
  ...
{% endif %}
```

### Why this solves the issue permanently:
- When an admin adds a new section in VisionAdmin and adds any combination of blocks, the template **automatically loops through the blocks and renders them**.
- **No Python code, no Jinja template edits, and no deployment are required.**

---

## 6. Admin Interface Design (VisionAdmin UI)

### 6.1 The Composable Block Modal
In `/visionadmin/sections`:
1. **Section General Settings** (Top):
   - Page Slug, Section Title (EN/AR), Subtitle (EN/AR), Description (CKEditor), Visibility, Sort Order.
2. **Composable Blocks Canvas** (Middle):
   - A visual stack showing the blocks currently inside the section.
   - Drag-and-drop handles to reorder blocks vertically.
   - **"+ Add Block" Dropdown Menu**:
     - 🃏 Add Cards Grid (Advice, Features, Guarantees)
     - 🏷️ Add Chips Cloud (Sizes, Vehicles, Brands, Areas)
     - ⚖️ Add Comparison Service Split (Fitting Centre vs Mobile Van)
     - 📊 Add Metric Counters (Stats, Numbers)
     - 🔢 Add Step Timeline (How It Works)
     - ❓ Add FAQ Accordion
     - ⭐ Add Reviews
     - 🖼️ Add Media / Story Split
     - 💰 Add Price Matrix
     - 🔘 Add Action Buttons Row
3. **Custom Fields & Attributes Drawer** (Bottom):
   - Allows adding optional key-value pairs (e.g. `callout_badge: "Limited Offer"`, `accent_color: "#58B31B"`, `secondary_url: "..."`) without altering database tables.

---

## 7. Phased Implementation Plan

```
┌────────────────────────────────────────────────────────────────────────┐
│                        IMPLEMENTATION PHASES                           │
│                                                                        │
│  PHASE 1 ── Core Universal Block Macros (Frontend)                     │
│  PHASE 2 ── Composable Block Controller & UI (VisionAdmin)             │
│  PHASE 3 ── Dynamic Custom Fields & Attributes Drawer                  │
│  PHASE 4 ── Presets & Auto-Migration for Existing Sections             │
│  PHASE 5 ── Verification & Stress Testing                              │
└────────────────────────────────────────────────────────────────────────┘
```

### Phase 1: Core Universal Block Macros (Frontend)
- Create modular Jinja partials under `templates/Client/components/blocks/`:
  - `cards_grid.html`
  - `chips_cloud.html`
  - `comparison_split.html`
  - `metrics_strip.html`
  - `process_steps.html`
  - `accordion_faq.html`
  - `reviews_slider.html`
  - `media_story.html`
  - `pricing_matrix.html`
  - `cta_actions.html`
- Update `templates/Client/Home.html` and `About.html` to check for `sec.section_data.blocks` first before checking legacy types.

### Phase 2: Composable Block Controller & UI (VisionAdmin)
- In `templates/visionadmin/sections.html`:
  - Add a **"Custom Composable Layout"** option in the Predefined Section Layout selector.
  - Create the **Block Palette & Canvas**: buttons to append any atomic block to the active section.
- In `static/visionadmin/sections.js`:
  - Implement block add/remove/reorder event handlers.
  - Build universal serializing logic: collects all configured blocks into `section_data.blocks`.

### Phase 3: Dynamic Custom Fields & Attributes
- Add a key-value attribute manager inside the modal.
- Any custom attribute (e.g., `promo_pill`, `custom_badge`, `wa_custom_message`) is serialized into `section_data.custom_fields` and exposed in Jinja.

### Phase 4: Presets & Auto-Migration
- Pre-configure 1-click presets in the admin (e.g., *"Buying Advice + Vehicle Chips"*, *"Service Options + Area Coverage"*, *"Hero + Stat Strip"*).
- Admins can click any preset as a starting template, then freely modify blocks.

### Phase 5: Verification & Quality Assurance
- Test creating 3 completely new, composite sections with mixed blocks (e.g. Cards + Chips + FAQ + CTA) strictly from the browser.
- Verify instant storefront rendering in both English and Arabic.
- Ensure 100% backward compatibility for existing sections (`hero`, `features`, `coverage`, `advice`, etc.).

---

## 8. Summary of Benefits

1. **Zero Code Touched**: New sections with any combination of content are created directly from the browser.
2. **Infinite Flexibility**: No longer restricted to rigid "cards-only" or "chips-only" layouts — components can be stacked freely.
3. **Multilingual by Default**: Every block element inherently supports English and Arabic.
4. **Instant Turnaround**: Marketing or content updates take seconds instead of requiring developer deployments.
