"""
scripts/seed_ckeditor_sections.py
Seeds the 12 CMS pages (Pages 2 through 13) in the MySQL `pages` table
with complete, modular, super-designed HTML sections inside CKEditor (page.content).
When viewed on the storefront or edited in VisionAdmin Page Builder, each page contains:
1. Hero Dark Banner (Breadcrumbs, Eyebrow, H1, Lead, Badges, WhatsApp/Call CTAs, Quote Card)
2. Value Proposition / Feature Cards Grid (Icon wells, titles, descriptions)
3. Pricing & Fitment Table (Guarantees strip + responsive table with per-row WhatsApp quote links)
4. Technical Advice / Local Coverage Section (Chips or Guidance cards)
5. Interactive FAQ Accordion (Questions, answers, animated chevrons)
6. High-Converting Emerald Gradient CTA Banner
"""

import os
import sys
import json
import urllib.parse

# Setup paths
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import get_connection
from build_4x4_page_clean import build_page_off_road_4x4


def build_hero_html(title, subtitle, lead, wa_text, wa_msg, breadcrumb_label="Page"):
    wa_encoded = urllib.parse.quote(wa_msg)
    return f"""
<section class="tv-page-hero">
  <div class="wrap hero-grid">
    <div class="tv-hero-left">
      <nav class="about-breadcrumb" aria-label="Breadcrumb" style="margin-bottom: 20px;">
        <a href="/">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>
          <span>Home</span>
        </a>
        <span class="sep" aria-hidden="true">/</span>
        <span class="current">{breadcrumb_label}</span>
      </nav>
      <span class="eyebrow">&mdash; {subtitle}</span>
      <h1>{title}</h1>
      <p class="lead">{lead}</p>
      <div class="cta-row">
        <a class="btn btn-wa" href="https://wa.me/971505069575?text={wa_encoded}" target="_blank" rel="noopener">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.46 1.32 4.96L2 22l5.25-1.38a9.9 9.9 0 004.79 1.22h.01c5.46 0 9.91-4.45 9.91-9.91C21.96 6.45 17.5 2 12.04 2zm5.8 14.06c-.24.68-1.42 1.31-1.96 1.36-.54.05-1.04.24-3.52-.73-2.99-1.18-4.86-4.29-5.01-4.49-.15-.2-1.2-1.6-1.2-3.05 0-1.45.76-2.16 1.03-2.46.27-.29.59-.37.78-.37s.39 0 .56.01c.18.01.42-.07.66.5.24.59.83 2.03.9 2.18.07.15.12.32.02.51-.1.2-.15.32-.29.5s-.3.4-.43.53c-.15.15-.3.31-.13.6.17.29.76 1.25 1.62 2.02 1.11.99 2.05 1.3 2.34 1.45.29.15.46.12.63-.07.17-.2.73-.85.92-1.14.2-.29.39-.24.66-.15.27.1 1.71.81 2 .96.29.15.49.22.56.34.07.13.07.75-.17 1.43z"/></svg>
          <span>{wa_text}</span>
        </a>
        <a class="btn btn-ghost-light" href="tel:+971505069575">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M6.62 10.79a15.05 15.05 0 006.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1C10.4 21 3 13.6 3 4.5 3 3.95 3.45 3.5 4 3.5h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/></svg>
          <span>+971 50 506 9575</span>
        </a>
      </div>
      <div class="hero-badges">
        <span class="pill"><svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M9 16.2L4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4z"/></svg> 100% Genuine Tyres</span>
        <span class="pill"><svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M9 16.2L4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4z"/></svg> Free Fitting &amp; Balancing</span>
        <span class="pill"><svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M9 16.2L4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4z"/></svg> Doorstep Mobile Van</span>
        <span class="pill"><svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M9 16.2L4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4z"/></svg> Official GCC Spec</span>
      </div>
    </div>
    <div class="quote-card tv-hero-quote-box">
      <div class="tv-quote-head">
        <span class="badge" style="background:rgba(37,99,255,0.18); color:#38bdf8; font-weight:800; font-size:0.75rem; text-transform:uppercase; letter-spacing:0.06em; padding:4px 10px; border-radius:100px; display:inline-block; margin-bottom:8px;">Fast UAE Dispatch</span>
        <h3 style="margin:0; font-size:1.35rem; color:#fff;">Get Tyre Pricing in Minutes</h3>
        <p class="sub" style="margin-top:6px; color:rgba(255,255,255,0.7); font-size:0.9rem;">Send your size on WhatsApp for verified price options across 60+ brands.</p>
      </div>
      <form id="quoteForm" novalidate style="margin-top:16px;">
        <div class="field">
          <label for="tyreSize">Tyre size (e.g. 235/55 R19)</label>
          <input id="tyreSize" name="tyreSize" type="text" placeholder="235/55 R19" autocomplete="off" required>
        </div>
        <div class="field-row">
          <div class="field">
            <label for="carMake">Vehicle details</label>
            <input id="carMake" name="carMake" type="text" placeholder="e.g. Nissan Patrol / Model Y" autocomplete="off">
          </div>
          <div class="field">
            <label for="emirate">Emirate</label>
            <select id="emirate" name="emirate">
              <option>Dubai</option><option>Abu Dhabi</option><option>Sharjah</option>
              <option>Ajman</option><option>Ras Al Khaimah</option><option>Fujairah</option><option>Umm Al Quwain</option>
            </select>
          </div>
        </div>
        <button type="submit" class="btn btn-wa w-full" style="margin-top:10px; width:100%; justify-content:center;">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.46 1.32 4.96L2 22l5.25-1.38a9.9 9.9 0 004.79 1.22h.01c5.46 0 9.91-4.45 9.91-9.91C21.96 6.45 17.5 2 12.04 2zm5.8 14.06c-.24.68-1.42 1.31-1.96 1.36-.54.05-1.04.24-3.52-.73-2.99-1.18-4.86-4.29-5.01-4.49-.15-.2-1.2-1.6-1.2-3.05 0-1.45.76-2.16 1.03-2.46.27-.29.59-.37.78-.37s.39 0 .56.01c.18.01.42-.07.66.5.24.59.83 2.03.9 2.18.07.15.12.32.02.51-.1.2-.15.32-.29.5s-.3.4-.43.53c-.15.15-.3.31-.13.6.17.29.76 1.25 1.62 2.02 1.11.99 2.05 1.3 2.34 1.45.29.15.46.12.63-.07.17-.2.73-.85.92-1.14.2-.29.39-.24.66-.15.27.1 1.71.81 2 .96.29.15.49.22.56.34.07.13.07.75-.17 1.43z"/></svg>
          <span>Instant WhatsApp Quote</span>
        </button>
      </form>
    </div>
  </div>
</section>
"""


def build_features_html(eyebrow, title, lead, cards):
    cards_html = ""
    cols_class = "g2" if len(cards) == 2 else ("g4" if len(cards) == 4 else "g3")
    for c in cards:
        cards_html += f"""
      <div class="card tv-feature-card">
        <div class="icon-well" aria-hidden="true">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg>
        </div>
        <h3>{c['title']}</h3>
        <p>{c['desc']}</p>
      </div>
"""
    return f"""
<section class="why-section tv-section-block">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow">&mdash; {eyebrow}</span>
      <h2>{title}</h2>
      <p class="lead">{lead}</p>
    </div>
    <div class="grid {cols_class}" style="margin-top:36px">
      {cards_html}
    </div>
  </div>
</section>
"""


def build_table_html(eyebrow, title, lead, col1_header, col2_header, col3_header, col4_header, col5_header, rows, quote_prefix="Quote for"):
    rows_html = ""
    for r in rows:
        wa_quote_msg = f"Hi TyresVision, I would like a price quote for {r['col1']} ({r['col2']})."
        wa_quote_enc = urllib.parse.quote(wa_quote_msg)
        rows_html += f"""
        <tr>
          <td class="td-size">
            <span class="size-pill">{r['col1']}</span>
          </td>
          <td class="td-common">
            {r['col2']}
          </td>
          <td class="td-price">
            <span class="price-val">{r['col3']}</span>
          </td>
          <td class="td-price desktop-col">
            <span class="price-val">{r['col4']}</span>
          </td>
          <td class="td-price desktop-col">
            <span class="price-val">{r['col5']}</span>
          </td>
          <td style="text-align:right;">
            <a href="https://wa.me/971505069575?text={wa_quote_enc}" target="_blank" rel="noopener" class="tv-table-quote-btn">
              <span>Price Quote</span> &rarr;
            </a>
          </td>
        </tr>
"""
    return f"""
<section class="price-section tv-section-block">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow">&mdash; {eyebrow}</span>
      <h2>{title}</h2>
      <p class="lead">{lead}</p>
    </div>
    <div class="price-guarantees-grid" style="margin-top:24px; margin-bottom:28px;">
      <div class="price-guarantee-card">
        <div class="pg-icon"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg></div>
        <div class="pg-text"><div class="pg-title">No Hidden Extras</div><div class="pg-sub">Valves, balancing and fitting included</div></div>
      </div>
      <div class="price-guarantee-card">
        <div class="pg-icon"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg></div>
        <div class="pg-text"><div class="pg-title">100% Genuine Certified</div><div class="pg-sub">Official distributor warranty &amp; GCC spec</div></div>
      </div>
      <div class="price-guarantee-card">
        <div class="pg-icon"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg></div>
        <div class="pg-text"><div class="pg-title">Doorstep Mobile Vans</div><div class="pg-sub">Fitted right outside your villa or office</div></div>
      </div>
      <div class="price-guarantee-card">
        <div class="pg-icon"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg></div>
        <div class="pg-text"><div class="pg-title">Fresh Production Dates</div><div class="pg-sub">Compliant with ESMA regulations</div></div>
      </div>
    </div>
    <div class="price-table-card">
      <div class="price-table-scroll">
        <table class="price-table" aria-label="{title}">
          <thead>
            <tr>
              <th scope="col" class="th-size"><span class="th-content"><span>{col1_header}</span></span></th>
              <th scope="col" class="th-common"><span class="th-content"><span>{col2_header}</span></span></th>
              <th scope="col" class="th-tier"><span class="th-content"><span>{col3_header}</span></span></th>
              <th scope="col" class="th-tier desktop-col"><span class="th-content"><span>{col4_header}</span></span></th>
              <th scope="col" class="th-tier desktop-col"><span class="th-content"><span>{col5_header}</span></span></th>
              <th scope="col" style="text-align:right;"><span>Action</span></th>
            </tr>
          </thead>
          <tbody>
            {rows_html}
          </tbody>
        </table>
      </div>
    </div>
  </div>
</section>
"""


def build_advice_html(eyebrow, title, lead, cards, wa_msg):
    cards_html = ""
    for c in cards:
        cards_html += f"""
      <div class="card advice-card tv-advice-card">
        <div class="icon-well" aria-hidden="true">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
        </div>
        <h3>{c['title']}</h3>
        <p>{c['desc']}</p>
      </div>
"""
    wa_enc = urllib.parse.quote(wa_msg)
    return f"""
<section class="why-section advice-section tv-section-block">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow">&mdash; {eyebrow}</span>
      <h2>{title}</h2>
      <p class="lead">{lead}</p>
    </div>
    <div class="grid g3" style="margin-top:36px">
      {cards_html}
    </div>
    <div class="cta-row center" style="justify-content:center; margin-top: 36px;">
      <a class="btn btn-wa" href="https://wa.me/971505069575?text={wa_enc}" target="_blank" rel="noopener">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.46 1.32 4.96L2 22l5.25-1.38a9.9 9.9 0 004.79 1.22h.01c5.46 0 9.91-4.45 9.91-9.91C21.96 6.45 17.5 2 12.04 2zm5.8 14.06c-.24.68-1.42 1.31-1.96 1.36-.54.05-1.04.24-3.52-.73-2.99-1.18-4.86-4.29-5.01-4.49-.15-.2-1.2-1.6-1.2-3.05 0-1.45.76-2.16 1.03-2.46.27-.29.59-.37.78-.37s.39 0 .56.01c.18.01.42-.07.66.5.24.59.83 2.03.9 2.18.07.15.12.32.02.51-.1.2-.15.32-.29.5s-.3.4-.43.53c-.15.15-.3.31-.13.6.17.29.76 1.25 1.62 2.02 1.11.99 2.05 1.3 2.34 1.45.29.15.46.12.63-.07.17-.2.73-.85.92-1.14.2-.29.39-.24.66-.15.27.1 1.71.81 2 .96.29.15.49.22.56.34.07.13.07.75-.17 1.43z"/></svg>
        <span>Ask Our Tyre Specialists on WhatsApp</span>
      </a>
      <a class="btn btn-ghost" href="tel:+971505069575">+971 50 506 9575</a>
    </div>
  </div>
</section>
"""


def build_coverage_html(location_name, areas_heading, chips):
    chips_html = ""
    for c in chips:
        wa_chip_msg = f"Hi TyresVision, do you deliver and fit tyres in {c} ({location_name})?"
        wa_chip_enc = urllib.parse.quote(wa_chip_msg)
        chips_html += f"""
        <a class="svc chip-interactive" href="https://wa.me/971505069575?text={wa_chip_enc}" target="_blank" rel="noopener">
          <span class="dot" aria-hidden="true"></span>
          <span class="chip-text">{c}</span>
          <svg class="chip-wa-arrow" width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.46 1.32 4.96L2 22l5.25-1.38a9.9 9.9 0 004.79 1.22h.01c5.46 0 9.91-4.45 9.91-9.91C21.96 6.45 17.5 2 12.04 2zm5.8 14.06c-.24.68-1.42 1.31-1.96 1.36-.54.05-1.04.24-3.52-.73-2.99-1.18-4.86-4.29-5.01-4.49-.15-.2-1.2-1.6-1.2-3.05 0-1.45.76-2.16 1.03-2.46.27-.29.59-.37.78-.37s.39 0 .56.01c.18.01.42-.07.66.5.24.59.83 2.03.9 2.18.07.15.12.32.02.51-.1.2-.15.32-.29.5s-.3.4-.43.53c-.15.15-.3.31-.13.6.17.29.76 1.25 1.62 2.02 1.11.99 2.05 1.3 2.34 1.45.29.15.46.12.63-.07.17-.2.73-.85.92-1.14.2-.29.39-.24.66-.15.27.1 1.71.81 2 .96.29.15.49.22.56.34.07.13.07.75-.17 1.43z"/></svg>
        </a>
"""
    return f"""
<section class="coverage-section tv-section-block">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow">&mdash; {location_name.upper()} FITTING NETWORK</span>
      <h2>Delivery &amp; Fitting Coverage Across {location_name}</h2>
      <p class="lead">Choose free installation at any of our vetted partner garages, or have our certified mobile van fit and balance your tyres right on your driveway or office parking bay.</p>
    </div>
    <div class="coverage-options-grid" style="margin-top:32px;">
      <div class="coverage-option-card">
        <div class="coverage-card-head">
          <span class="coverage-tag coverage-tag-free">100% FREE FITTING</span>
          <h3>Free fitting at a partner centre in {location_name}</h3>
        </div>
        <p class="coverage-card-desc">We ship your tyres directly to our partner garage near you in {location_name}. Mounting, computerized 3D balancing, new standard valves, and old tyre eco-disposal are completely free of charge.</p>
        <div class="coverage-card-action">
          <a class="btn btn-wa btn-sm" href="https://wa.me/971505069575?text=Hi%20TyresVision%2C%20I%20would%20like%20to%20book%20free%20tyre%20fitting%20at%20a%20partner%20centre%20in%20{location_name}." target="_blank" rel="noopener">
            <span>Book at Partner Centre</span>
          </a>
        </div>
      </div>
      <div class="coverage-option-card">
        <div class="coverage-card-head">
          <span class="coverage-tag">DOORSTEP MOBILE VAN</span>
          <h3>Mobile van fitting at your location in {location_name}</h3>
        </div>
        <p class="coverage-card-desc">Our fully equipped mobile workshop vans arrive at your home, villa, or office in {location_name}. Complete tyre replacement and precision digital balancing on site with zero hassle.</p>
        <div class="coverage-card-action">
          <a class="btn btn-ghost btn-sm" href="https://wa.me/971505069575?text=Hi%20TyresVision%2C%20I%20would%20like%20to%20book%20mobile%20van%20fitting%20in%20{location_name}." target="_blank" rel="noopener">
            <span>Book Mobile Van</span>
          </a>
        </div>
      </div>
    </div>
    <div class="shop-by-group coverage-area-group" style="margin-top:36px;">
      <div class="shop-by-group-header">
        <h3 class="shop-by-group-title">{areas_heading}</h3>
      </div>
      <div class="svc-grid shop-by-grid">
        {chips_html}
      </div>
    </div>
  </div>
</section>
"""


def build_faq_html(title, faqs):
    faqs_html = ""
    for idx, f in enumerate(faqs):
        is_first = (idx == 0)
        faqs_html += f"""
      <div class="faq-item {'active' if is_first else ''}" data-faq-item>
        <button type="button" class="faq-summary" aria-expanded="{'true' if is_first else 'false'}">
          <span class="faq-question-text">{f['q']}</span>
          <span class="faq-chevron-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
          </span>
        </button>
        <div class="faq-answer">
          <div class="faq-answer-inner">
            <div class="body"><p>{f['a']}</p></div>
          </div>
        </div>
      </div>
"""
    return f"""
<section class="faq tv-section-block">
  <div class="wrap" style="max-width:860px">
    <div class="center tv-section-head">
      <span class="eyebrow">&mdash; FREQUENTLY ASKED QUESTIONS</span>
      <h2>{title}</h2>
    </div>
    <div class="faq-list" style="margin-top:36px;">
      {faqs_html}
    </div>
  </div>
</section>
"""


def build_cta_html(title, lead, wa_text, wa_msg):
    wa_enc = urllib.parse.quote(wa_msg)
    return f"""
<section class="final tv-cta-block">
  <div class="wrap">
    <h2>{title}</h2>
    <p>{lead}</p>
    <div class="cta-row" style="justify-content:center">
      <a class="btn btn-wa" href="https://wa.me/971505069575?text={wa_enc}" target="_blank" rel="noopener">
        <svg width="19" height="19" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.46 1.32 4.96L2 22l5.25-1.38a9.9 9.9 0 004.79 1.22h.01c5.46 0 9.91-4.45 9.91-9.91C21.96 6.45 17.5 2 12.04 2zm5.8 14.06c-.24.68-1.42 1.31-1.96 1.36-.54.05-1.04.24-3.52-.73-2.99-1.18-4.86-4.29-5.01-4.49-.15-.2-1.2-1.6-1.2-3.05 0-1.45.76-2.16 1.03-2.46.27-.29.59-.37.78-.37s.39 0 .56.01c.18.01.42-.07.66.5.24.59.83 2.03.9 2.18.07.15.12.32.02.51-.1.2-.15.32-.29.5s-.3.4-.43.53c-.15.15-.3.31-.13.6.17.29.76 1.25 1.62 2.02 1.11.99 2.05 1.3 2.34 1.45.29.15.46.12.63-.07.17-.2.73-.85.92-1.14.2-.29.39-.24.66-.15.27.1 1.71.81 2 .96.29.15.49.22.56.34.07.13.07.75-.17 1.43z"/></svg>
        <span>{wa_text}</span>
      </a>
      <a class="btn btn-white" href="tel:+971505069575">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M6.62 10.79a15.05 15.05 0 006.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1C10.4 21 3 13.6 3 4.5 3 3.95 3.45 3.5 4 3.5h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/></svg>
        <span>Call +971 50 506 9575</span>
      </a>
    </div>
    <p class="hours">Open daily across all 7 Emirates — fast mobile vans and partner fitting centers ready.</p>
  </div>
</section>
"""


# =============================================================================
# DATA DEFINITIONS FOR ALL 12 PAGES
# =============================================================================

PAGES_CONTENT = {}

# 1. EV Tyres
PAGES_CONTENT['ev-tyres'] = (
    build_hero_html(
        "EV & Hybrid Tyres in Dubai, Abu Dhabi & UAE",
        "ELECTRIC MOBILITY SPECIALISTS",
        "High-load rated (HL/XL), low rolling resistance tyres engineered for instantaneous electric torque and quiet cabin acoustics. Fitted free at a partner centre or doorstep mobile van across the UAE.",
        "WhatsApp for EV Tyre Quote",
        "Hi TyresVision, I need a tyre quote for my electric car.",
        "EV Tyres"
    ) +
    build_features_html(
        "ENGINEERING SPECIFICATIONS",
        "Why Electric Cars Need Dedicated EV Tyres",
        "Instantaneous electric torque and heavy battery packs put extraordinary shear stress on rubber. In UAE tarmac heat exceeding 55°C, standard passenger tyres wear out up to 40% faster.",
        [
            {'title': 'Stiffer Sidewall & HL Casing', 'desc': 'Engineered to support 2,000–2,600 kg curb weights without excessive tyre squirm, sidewall deflection, or rapid shoulder scrubbing.'},
            {'title': 'Acoustic Sound-Dampening Foam', 'desc': 'Without combustion engine sound, tyre cavity resonance dominates the cabin. Polyurethane inner foam absorbs road rumble for silent motoring.'},
            {'title': 'Low Rolling Resistance Silica', 'desc': 'Advanced compounds reduce energy loss per wheel rotation, protecting and extending battery driving range by 7% to 10%.'},
            {'title': 'Safe Doorstep Mobile Jacking', 'desc': 'Our mobile vans carry dedicated vehicle-specific rubber lifting pucks to safeguard underbody high-voltage battery trays during fitting.'}
        ]
    ) +
    build_table_html(
        "POPULAR UAE FITMENTS & PRICING",
        "Tyres by Electric & Hybrid Model",
        "Factory dimensions, recommended load indexes, and starting tyre prices for top electric and hybrid vehicles in Dubai and Abu Dhabi.",
        "Vehicle Model", "Common Tyre Sizes", "Budget From", "Mid-Range", "Premium EV",
        [
            {'col1': 'Tesla Model 3', 'col2': '235/45 R18, 235/40 R19, 235/35 R20', 'col3': 'AED 295', 'col4': 'AED 490', 'col5': 'AED 780'},
            {'col1': 'Tesla Model Y', 'col2': '255/45 R19, 255/40 R20, 275/35 R21', 'col3': 'AED 340', 'col4': 'AED 560', 'col5': 'AED 890'},
            {'col1': 'BYD Atto 3 / Seal', 'col2': '215/60 R17, 235/50 R18, 235/45 R19', 'col3': 'AED 260', 'col4': 'AED 420', 'col5': 'AED 640'},
            {'col1': 'Hyundai Ioniq 5 / Kia EV6', 'col2': '235/55 R19, 255/45 R20', 'col3': 'AED 320', 'col4': 'AED 510', 'col5': 'AED 790'},
            {'col1': 'Mercedes EQE / EQS', 'col2': '255/45 R19, 265/40 R20, 265/35 R21', 'col3': 'AED 480', 'col4': 'AED 740', 'col5': 'AED 1,180'},
            {'col1': 'Audi e-tron / Q8 e-tron', 'col2': '255/55 R19, 265/45 R21, 285/40 R22', 'col3': 'AED 490', 'col4': 'AED 760', 'col5': 'AED 1,220'},
            {'col1': 'Toyota / Lexus Hybrids', 'col2': '215/55 R17, 235/45 R18', 'col3': 'AED 210', 'col4': 'AED 340', 'col5': 'AED 520'},
            {'col1': 'Polestar 2', 'col2': '245/45 R19, 245/40 R20', 'col3': 'AED 380', 'col4': 'AED 590', 'col5': 'AED 890'}
        ]
    ) +
    build_advice_html(
        "SAFETY & LONGEVITY GUIDANCE",
        "Crucial Advice for UAE Electric Car Drivers",
        "Key technical guidelines to maximize tyre lifespan and protect your battery range across Dubai and Abu Dhabi.",
        [
            {'title': 'Check the "HL" (High Load) Rating', 'desc': 'If your door placard specifies an HL rating, never fit standard SL/XL tyres. Heavy batteries in 50°C summer heat demand full structural load ratings.'},
            {'title': 'Rotate Tyres Every 8,000–10,000 KM', 'desc': 'Instantaneous electric motor torque wears drive-axle tyres twice as fast as trailing tyres. Routine rotation balances tread wear across all four corners.'},
            {'title': 'Run-Flat vs Normal Tyre Swaps', 'desc': 'You can switch stiff run-flats for conventional tyres for a softer ride, but always carry a 12V portable compressor and emergency sealant kit.'}
        ],
        "Hi TyresVision, I need tyre maintenance advice for my electric vehicle."
    ) +
    build_faq_html(
        "Frequently Asked Questions About EV Tyres",
        [
            {'q': 'Do EV tyres really make a difference to battery range?', 'a': 'Yes. Independent tests demonstrate that low rolling resistance EV tyres improve driving range by 7% to 10% compared to standard generic tyres, equating to an extra 35–50 km per full charge on a 500 km battery.'},
            {'q': 'Can I put normal tyres on my Tesla or BYD?', 'a': 'Technically yes, provided the load and speed ratings match. However, normal tyres will wear up to 40% faster under electric torque, generate noticeable cabin road noise, and decrease battery efficiency.'},
            {'q': 'Why do EV tyres wear out faster than petrol car tyres?', 'a': 'Electric vehicles weigh 20% to 30% more because of heavy battery packs, and electric motors deliver 100% torque instantly from 0 RPM, putting intense friction on the tyre contact patch.'},
            {'q': 'Can run-flat tyres on EVs and luxury cars be repaired?', 'a': 'Generally no. Once driven with zero or low pressure, the internal sidewall structure suffers severe heat degradation that compromises structural safety. Manufacturers mandate replacement.'},
            {'q': 'Can your mobile fitting van change EV tyres at my villa or office?', 'a': 'Yes. Our mobile vans are fully equipped with low-clearance jacks, vehicle-specific rubber lifting pucks, and precision digital balancing machines to fit tyres at your home or workplace safely.'}
        ]
    ) +
    build_cta_html(
        "Ready to Fit the Right Tyres on Your EV?",
        "Send your tyre size or car model on WhatsApp. Our specialists confirm EV-rated options and book free mobile van fitting today.",
        "WhatsApp for EV Tyre Quote",
        "Hi TyresVision, I need a tyre quote for my electric car."
    )
)

# 2. 4x4 & Off-Road Tyres (Exact TyresVision-13-Page-Build-Plan 1.docx)
PAGES_CONTENT['off-road-4x4-tyres'] = build_page_off_road_4x4()

# 3. Tyre Brands
PAGES_CONTENT['tyre-brands'] = (
    build_hero_html(
        "Tyre Brands in the UAE — 60+ Certified Global Brands",
        "OFFICIAL DISTRIBUTOR SOURCED",
        "From world-renowned premium manufacturers to dependable value tiers. Every tyre is 100% genuine, date-fresh, and backed by official GCC warranty with free fitting across the UAE.",
        "Compare Brand Prices on WhatsApp",
        "Hi TyresVision, I would like to compare tyre brands.",
        "Tyre Brands"
    ) +
    build_features_html(
        "FIND YOUR BALANCE OF PERFORMANCE & BUDGET",
        "Tyre Brand Tiers in the UAE",
        "Understand the differences in compounds, treadwear ratings, and wet braking across brand tiers.",
        [
            {'title': 'Premium Tier — Michelin, Bridgestone, Continental, Pirelli', 'desc': 'Industry-leading braking distances, acoustic dampening, and OEM approvals on Porsche, Mercedes, BMW, and Ferrari. Maximum summer heat resistance.'},
            {'title': 'Mid-Range Tier — Hankook, Dunlop, Yokohama, Kumho, Falken', 'desc': 'Exceptional reliability, fresh compounds, and balanced wet/dry grip at 20% to 30% lower cost than top tier brands. Excellent value for daily drivers.'},
            {'title': 'Budget Tier — Sailun, Triangle, Nexen, Zeetex, Roadstone', 'desc': 'Cost-effective, ESMA-certified options for fleet vehicles, rideshare drivers, and budget-conscious motorists who want verified safety without high cost.'}
        ]
    ) +
    build_table_html(
        "ORIGIN, WARRANTY & STARTING PRICES",
        "Comprehensive Brand Comparison Matrix",
        "Quick reference overview of the 16 most popular tyre manufacturers supplied and fitted across Dubai and Abu Dhabi.",
        "Brand", "Country of Origin / Specialty", "Category", "Warranty", "Price Guide",
        [
            {'col1': 'Michelin', 'col2': 'France — Pilot Sport, Primacy, Latitude', 'col3': 'Premium', 'col4': '5-Year Official', 'col5': 'From AED 380'},
            {'col1': 'Bridgestone', 'col2': 'Japan — Potenza, Turanza, Dueler', 'col3': 'Premium', 'col4': '5-Year Official', 'col5': 'From AED 350'},
            {'col1': 'Continental', 'col2': 'Germany — SportContact, PremiumContact', 'col3': 'Premium', 'col4': '5-Year Official', 'col5': 'From AED 360'},
            {'col1': 'Pirelli', 'col2': 'Italy — P Zero, Scorpion, Cinturato', 'col3': 'Premium', 'col4': '5-Year Official', 'col5': 'From AED 390'},
            {'col1': 'Goodyear', 'col2': 'USA — Eagle F1, EfficientGrip, Wrangler', 'col3': 'Premium', 'col4': '5-Year Official', 'col5': 'From AED 340'},
            {'col1': 'Dunlop', 'col2': 'Japan / UK — Grandtrek, SP Sport', 'col3': 'Mid-Range', 'col4': '5-Year Official', 'col5': 'From AED 260'},
            {'col1': 'Hankook', 'col2': 'South Korea — Ventus, Dynapro, iON', 'col3': 'Mid-Range', 'col4': '5-Year Official', 'col5': 'From AED 240'},
            {'col1': 'Yokohama', 'col2': 'Japan — Advan, Geolandar, BluEarth', 'col3': 'Mid-Range', 'col4': '5-Year Official', 'col5': 'From AED 270'},
            {'col1': 'Kumho', 'col2': 'South Korea — Ecsta, Crugen, Solus', 'col3': 'Mid-Range', 'col4': '5-Year Official', 'col5': 'From AED 220'},
            {'col1': 'Falken', 'col2': 'Japan — Azenis, Wildpeak, Ziex', 'col3': 'Mid-Range', 'col4': '5-Year Official', 'col5': 'From AED 250'},
            {'col1': 'Nexen', 'col2': 'South Korea — N Fera, N Blue, Roadian', 'col3': 'Mid-Range', 'col4': '5-Year Official', 'col5': 'From AED 195'},
            {'col1': 'Toyo', 'col2': 'Japan — Proxes, Open Country', 'col3': 'Mid-Range', 'col4': '5-Year Official', 'col5': 'From AED 260'},
            {'col1': 'Sailun', 'col2': 'China — Atrezzo, Terramax', 'col3': 'Budget', 'col4': '3-Year Official', 'col5': 'From AED 165'},
            {'col1': 'Triangle', 'col2': 'China — AdvanteX, SporteX', 'col3': 'Budget', 'col4': '3-Year Official', 'col5': 'From AED 155'},
            {'col1': 'Zeetex', 'col2': 'UAE / Global — HP, SU, ZT', 'col3': 'Budget', 'col4': '3-Year Official', 'col5': 'From AED 150'}
        ]
    ) +
    build_advice_html(
        "BUYER PROTECTION & QUALITY",
        "GCC-Spec vs Grey Market Tyres",
        "Why buying officially imported tyres with ESMA certification protects your vehicle and warranty.",
        [
            {'title': 'Look for the ESMA RFID Tag', 'desc': 'Official UAE tyres carry an RFID sticker issued by the Emirates Authority for Standardization and Metrology, verifying they meet GCC heat and speed criteria.'},
            {'title': 'Check the DOT Date Code', 'desc': 'The 4-digit code (e.g. 2424 for 24th week of 2024) confirms fresh production. Beware grey market tyres that sat in uncooled sea containers for months.'},
            {'title': 'Warranty Validity', 'desc': 'Grey market tyres are not honored by local UAE brand distributors. TyresVision sources exclusively from official authorized dealer networks with valid warranty.'}
        ],
        "Hi TyresVision, I would like to verify tyre brand warranty and GCC specs."
    ) +
    build_faq_html(
        "Frequently Asked Questions: Tyre Brands",
        [
            {'q': 'Which tyre brand is best for Dubai summer heat?', 'a': 'Michelin and Bridgestone consistently rank highest in heat endurance and high-speed stability on UAE tarmac. Both use specialized silica compounds that resist softening and blistering above 50°C.'},
            {'q': 'Are budget Chinese tyres safe for highway driving in the UAE?', 'a': 'Yes, provided they are officially imported and bear the UAE ESMA certification. Brands like Sailun and Triangle pass stringent GCC braking and heat dissipation tests.'},
            {'q': 'How do I know if a tyre is officially GCC spec?', 'a': 'Look for the GCC conformity certification mark and the ESMA RFID label affixed to the tyre tread. TyresVision guarantees 100% GCC specification across all 60+ brands.'},
            {'q': 'Can I mix different tyre brands on my car?', 'a': 'You should never mix different brands or tread patterns across the same axle. While matching the front axle to one brand and the rear to another is permissible, keeping all four tyres identical is best for balanced handling.'},
            {'q': 'What does the manufacturer warranty actually cover?', 'a': 'The official distributor warranty protects against manufacturing defects, tread separation, and casing delamination. It does not cover road hazard punctures, curb damage, or improper alignment wear.'}
        ]
    ) +
    build_cta_html(
        "Need Help Choosing the Best Brand for Your Car?",
        "WhatsApp our specialists with your tyre size and budget. We quote verified options across premium, mid-range, and value brands.",
        "WhatsApp for Brand Recommendations",
        "Hi TyresVision, I would like to compare tyre brands."
    )
)

# 4. Tyre Sizes
PAGES_CONTENT['tyre-sizes'] = (
    build_hero_html(
        "Tyre Sizes in the UAE — Comprehensive Guide & Inventory",
        "FIND YOUR EXACT FITMENT",
        "In-stock inventory for every rim size from 14-inch to 24-inch. Learn how to decode your sidewall markings, check vehicle compatibility, and get instant pricing across 60+ brands.",
        "WhatsApp Your Tyre Size",
        "Hi TyresVision, I need a quote for my tyre size.",
        "Tyre Sizes"
    ) +
    build_features_html(
        "EXAMPLE: 235 / 55 R 19 105 W",
        "How to Read Your Tyre Sidewall Numbers",
        "Every character on your tyre sidewall reveals vital structural, dimensional, and performance criteria.",
        [
            {'title': '235 — Section Width (mm)', 'desc': 'The width of the tyre in millimeters from sidewall to sidewall when mounted on the recommended rim.'},
            {'title': '55 — Aspect Ratio (%)', 'desc': 'The height of the sidewall expressed as a percentage of the width. A 55 profile means height is 55% of 235mm (129.25mm).'},
            {'title': 'R 19 — Construction & Rim', 'desc': '"R" signifies radial ply construction; "19" indicates the wheel rim diameter in inches.'},
            {'title': '105 W — Load & Speed Rating', 'desc': '"105" means maximum load capacity of 925 kg per tyre; "W" certifies safe continuous operation up to 270 km/h.'}
        ]
    ) +
    build_table_html(
        "VEHICLE PAIRINGS & STARTING PRICES",
        "Top 12 Tyre Sizes in the UAE",
        "Starting prices and common vehicle applications for the most frequently purchased tyre dimensions across the Emirates.",
        "Tyre Size", "Common On Vehicles", "Budget From", "Mid-Range", "Premium",
        [
            {'col1': '195/65 R15', 'col2': 'Toyota Corolla, Nissan Sunny, Honda Civic', 'col3': 'AED 165', 'col4': 'AED 240', 'col5': 'AED 360'},
            {'col1': '205/55 R16', 'col2': 'VW Golf, Toyota Corolla, Hyundai Elantra', 'col3': 'AED 180', 'col4': 'AED 260', 'col5': 'AED 385'},
            {'col1': '215/60 R16', 'col2': 'Toyota Camry, Honda Accord, Nissan Altima', 'col3': 'AED 195', 'col4': 'AED 280', 'col5': 'AED 410'},
            {'col1': '215/55 R17', 'col2': 'Toyota Camry, Lexus ES, Nissan Altima', 'col3': 'AED 220', 'col4': 'AED 310', 'col5': 'AED 460'},
            {'col1': '225/65 R17', 'col2': 'Toyota RAV4, Nissan X-Trail, Honda CR-V', 'col3': 'AED 240', 'col4': 'AED 350', 'col5': 'AED 510'},
            {'col1': '225/45 R18', 'col2': 'BMW 3 Series, Mercedes C-Class, Audi A4', 'col3': 'AED 260', 'col4': 'AED 390', 'col5': 'AED 590'},
            {'col1': '235/55 R19', 'col2': 'Lexus RX, Audi Q5, Hyundai Santa Fe', 'col3': 'AED 295', 'col4': 'AED 440', 'col5': 'AED 670'},
            {'col1': '265/65 R17', 'col2': 'Toyota Prado, Pajero, Fortuner', 'col3': 'AED 310', 'col4': 'AED 460', 'col5': 'AED 650'},
            {'col1': '275/40 R20', 'col2': 'BMW X5, Range Rover Sport, Porsche Cayenne', 'col3': 'AED 390', 'col4': 'AED 580', 'col5': 'AED 880'},
            {'col1': '285/60 R18', 'col2': 'Toyota Land Cruiser LC200, Nissan Patrol', 'col3': 'AED 390', 'col4': 'AED 610', 'col5': 'AED 890'},
            {'col1': '275/60 R20', 'col2': 'Nissan Patrol Y62, Chevy Tahoe, GMC Yukon', 'col3': 'AED 410', 'col4': 'AED 640', 'col5': 'AED 920'},
            {'col1': '265/55 R20', 'col2': 'Toyota Land Cruiser LC300, Lexus LX', 'col3': 'AED 420', 'col4': 'AED 660', 'col5': 'AED 940'}
        ]
    ) +
    build_advice_html(
        "FITMENT INTEGRITY",
        "Can You Change Your Tyre Size?",
        "Key rules regarding plus-sizing, speedometer calibration, and wheel clearance.",
        [
            {'title': 'Keep Rolling Diameter Within ±3%', 'desc': 'Changing tyre dimensions is safe as long as total diameter matches within 3% to avoid speedometer errors and ABS sensor faults.'},
            {'title': 'Never Downgrade Load or Speed Rating', 'desc': 'Always equal or exceed the manufacturer placard. An under-rated tyre under heavy load in summer heat can experience sudden failure.'},
            {'title': 'Mind Wheel Well & Caliper Clearance', 'desc': 'Wider tyres or altered offsets must clear suspension struts, tie rods, and brake calipers at full steering lock.'}
        ],
        "Hi TyresVision, I have a question about changing my tyre size."
    ) +
    build_faq_html(
        "Frequently Asked Questions: Tyre Sizes",
        [
            {'q': 'Where can I find the correct tyre size for my car?', 'a': 'The most reliable location is the sticker on the driver’s door pillar (jamb), inside the glove compartment, or in your vehicle owner’s manual. You can also read the numbers directly on your existing tyre sidewall.'},
            {'q': 'Can I change my tyre size or rim size?', 'a': 'You can change rim and tyre dimensions as long as the overall rolling diameter remains within ±3% of factory specification. This prevents speedometer errors and rubbing against suspension struts or wheel arches.'},
            {'q': 'What happens if I fit a lower speed rating in UAE summer?', 'a': 'Fitting a speed rating lower than manufacturer specification is dangerous. In 50°C summer heat, an under-rated tyre accumulates excessive heat that can cause tread delamination or sudden blowouts at highway speeds.'},
            {'q': 'Are front and rear tyres always the same size?', 'a': 'Not always. Many rear-wheel-drive sports cars and performance SUVs (such as BMW M models, Mercedes-AMG, and Porsche) feature "staggered" fitments, where the rear tyres are wider than the front tyres.'},
            {'q': 'If I send a photo of my tyre on WhatsApp, can you confirm the size?', 'a': 'Absolutely! Just snap a photo of the raised lettering on your tyre sidewall and message it to our WhatsApp team at +971 50 506 9575. We will reply in minutes with exact prices.'}
        ]
    ) +
    build_cta_html(
        "Not Sure About Your Exact Tyre Size?",
        "Send us your car model or a quick photo of your tyre sidewall on WhatsApp. We find your exact fitment instantly.",
        "WhatsApp for Tyre Size Check",
        "Hi TyresVision, I need a quote for my tyre size."
    )
)

# 5. Tyres by Car Make & Model
PAGES_CONTENT['tyres-by-car'] = (
    build_hero_html(
        "Tyres by Car Make & Model in the UAE",
        "VEHICLE FITMENT DIRECTORY",
        "Exact manufacturer-matched tyre fitments for Toyota, Nissan, Mercedes, BMW, Ford, Tesla, Lexus, and Porsche. Guaranteed load and speed ratings with free local fitting across the Emirates.",
        "WhatsApp for Car Model Quote",
        "Hi TyresVision, I would like a tyre quote for my car.",
        "Tyres by Car"
    ) +
    build_features_html(
        "ORIGINAL EQUIPMENT EXCELLENCE",
        "OEM Manufacturer Homologation Approvals",
        "Understand why major automotive manufacturers engineer vehicle-specific tyre specifications.",
        [
            {'title': 'Mercedes-Benz "MO" & "MOE"', 'desc': 'Custom tuned for Mercedes chassis dynamics, ensuring precise road feel and high-speed stability on the E11.'},
            {'title': 'BMW "★" (Star Spec)', 'desc': 'Engineered to preserve BMW 50:50 weight balance and active suspension damping, reducing in-cabin road harshness.'},
            {'title': 'Audi "AO" & Porsche "N-Spec"', 'desc': 'Developed for Quattro AWD torque distribution and Porsche rear-engine cornering loads with specialized casing stiffness.'}
        ]
    ) +
    build_table_html(
        "TOP 12 UAE VEHICLES & FACTORY TYRE SIZES",
        "Vehicle Tyre Size Reference Table",
        "Factory tyre specifications and starting prices for the most driven passenger cars and SUVs in the UAE.",
        "Car Make & Model", "Factory Tyre Sizes", "Budget From", "Mid-Range", "Premium OE",
        [
            {'col1': 'Toyota Land Cruiser LC300', 'col2': '265/65 R18, 265/55 R20', 'col3': 'AED 390', 'col4': 'AED 620', 'col5': 'AED 940'},
            {'col1': 'Nissan Patrol Y62', 'col2': '265/70 R18, 275/60 R20', 'col3': 'AED 395', 'col4': 'AED 630', 'col5': 'AED 920'},
            {'col1': 'Toyota Prado', 'col2': '265/65 R17, 265/60 R18', 'col3': 'AED 310', 'col4': 'AED 470', 'col5': 'AED 680'},
            {'col1': 'Toyota Camry & Avalon', 'col2': '215/60 R16, 215/55 R17, 235/45 R18', 'col3': 'AED 195', 'col4': 'AED 290', 'col5': 'AED 440'},
            {'col1': 'Nissan Altima & Maxima', 'col2': '215/60 R16, 215/55 R17, 235/40 R19', 'col3': 'AED 195', 'col4': 'AED 295', 'col5': 'AED 460'},
            {'col1': 'Toyota Corolla & Yaris', 'col2': '195/65 R15, 205/55 R16', 'col3': 'AED 165', 'col4': 'AED 240', 'col5': 'AED 360'},
            {'col1': 'Tesla Model 3 & Model Y', 'col2': '235/45 R18, 255/45 R19, 255/40 R20', 'col3': 'AED 295', 'col4': 'AED 540', 'col5': 'AED 860'},
            {'col1': 'Mercedes-Benz C-Class / E-Class', 'col2': '225/45 R18, 245/45 R18, 245/40 R19', 'col3': 'AED 280', 'col4': 'AED 440', 'col5': 'AED 680'},
            {'col1': 'BMW 3 Series & 5 Series', 'col2': '225/45 R18, 245/45 R18, 245/40 R19', 'col3': 'AED 280', 'col4': 'AED 440', 'col5': 'AED 690'},
            {'col1': 'Lexus RX350 & ES350', 'col2': '235/55 R19, 235/60 R18, 215/55 R17', 'col3': 'AED 240', 'col4': 'AED 380', 'col5': 'AED 580'},
            {'col1': 'Porsche Cayenne & Macan', 'col2': '275/45 R20, 295/35 R21, 265/45 R20', 'col3': 'AED 450', 'col4': 'AED 690', 'col5': 'AED 1,080'},
            {'col1': 'Ford F-150 & Ranger', 'col2': '275/65 R18, 275/55 R20, 315/70 R17', 'col3': 'AED 390', 'col4': 'AED 590', 'col5': 'AED 890'}
        ]
    ) +
    build_advice_html(
        "VEHICLE INTEGRITY",
        "Original Equipment (OE) vs Aftermarket Tyres",
        "Essential insights on maintaining vehicle warranty and suspension calibration.",
        [
            {'title': 'Why Choose OE Homologation?', 'desc': 'Automakers spend up to 3 years co-developing tyres with Michelin, Pirelli, and Bridgestone to fine-tune steering precision, braking, and noise.'},
            {'title': 'Can You Use Aftermarket Tyres?', 'desc': 'Yes, aftermarket tyres meeting factory size, load, and speed specifications are completely road-legal and safe for annual RTA testing.'},
            {'title': 'Protecting High-End Alloys', 'desc': 'Our mobile vans and partner workshops utilize touchless tire machines and rubber-coated jaws that will never scuff luxury rims up to 24 inches.'}
        ],
        "Hi TyresVision, I would like to check OE homologated tyres for my vehicle."
    ) +
    build_faq_html(
        "Frequently Asked Questions: Tyres by Car Make",
        [
            {'q': 'What do manufacturer markings like "MO" or "Star" mean?', 'a': 'These indicate Original Equipment (OE) homologation. "MO" denotes Mercedes-Original, "★" is engineered specifically for BMW, "AO" is Audi-approved, and "N" is Porsche-certified. These tyres are custom-tuned to the vehicle chassis dynamics.'},
            {'q': 'Do I have to buy OE homologated tyres for my German car?', 'a': 'No, standard tyres with matching size, load, and speed ratings are completely legal and safe. However, OE marked tyres preserve the original steering feel and ride comfort tuned by factory engineers.'},
            {'q': 'Can I share my vehicle registration (Mulkiya) to get the right tyre size?', 'a': 'Yes! Simply take a photo of your Mulkiya card or tyre placard on WhatsApp. Our specialists cross-reference factory databases to suggest exact fitments and prices.'},
            {'q': 'Do you offer mobile van fitting for luxury and sports cars?', 'a': 'Yes. Our mobile fitting vans utilize touchless lever-free mounting machines and low-profile jacks that eliminate rim scratches on high-end forged alloys up to 24 inches.'}
        ]
    ) +
    build_cta_html(
        "Need the Exact Tyres for Your Car Make?",
        "Share your vehicle make, model, and year on WhatsApp. We reply with verified fitment options and schedule free local installation.",
        "WhatsApp Your Car Details",
        "Hi TyresVision, I would like a tyre quote for my car."
    )
)

# 6 through 12: The 7 Location Pages
EMIRATES_INFO = [
    {
        'slug': 'tyre-shop-dubai',
        'name': 'Dubai',
        'hero_title': 'Tyre Shop Dubai — Buy Tyres Online with Free Fitting',
        'hero_sub': 'DUBAI TYRE SUPPLY & MOBILE VAN SERVICE',
        'hero_lead': 'Skip the Al Quoz industrial area hassle. 60+ certified tyre brands with upfront transparent pricing, delivered free to a partner garage near you or fitted at your villa, apartment, or office by our mobile vans.',
        'areas_heading': 'Dubai Neighborhood Delivery & Mobile Fitting Coverage',
        'chips': ['Dubai Marina', 'JLT', 'JBR', 'Palm Jumeirah', 'Downtown Dubai', 'Business Bay', 'Al Quoz', 'Deira', 'Mirdif', 'Arabian Ranches', 'JVC', 'Dubai Hills', 'Silicon Oasis', 'Al Barsha'],
        'local_advice_p': 'High-speed runs on Sheikh Zayed Road (E11) and Al Khail Road elevate tyre temperatures rapidly. Meanwhile, steep basement parking ramps in Marina and Downtown cause front tyre scrub. Ensure you maintain correct tyre pressure and check tread depth regularly.'
    },
    {
        'slug': 'tyre-shop-abu-dhabi',
        'name': 'Abu Dhabi',
        'hero_title': 'Tyre Shop Abu Dhabi — Doorstep Mobile Van & Workshop Fitting',
        'hero_sub': 'ABU DHABI CAPITAL TYRE NETWORK',
        'hero_lead': 'Fast, professional tyre supply and fitting across Abu Dhabi city, Musaffah, and the islands. Upfront pricing across 60+ global brands with certified mobile vans and approved partner centres.',
        'areas_heading': 'Abu Dhabi Coverage Areas',
        'chips': ['Al Reem Island', 'Yas Island', 'Saadiyat Island', 'Khalifa City', 'Al Raha Beach', 'Musaffah', 'MBZ City', 'Corniche', 'Al Bateen', 'Al Shamkha', 'Al Reef'],
        'local_advice_p': 'Commuting between Abu Dhabi and Dubai or Al Ain on the E11 involves sustained 120–140 km/h speeds under 48°C summer sunshine. Check tyre pressure weekly when cold and ensure tyres carry a "Temperature A" rating.'
    },
    {
        'slug': 'tyre-shop-sharjah',
        'name': 'Sharjah',
        'hero_title': 'Tyre Shop Sharjah — Honest Upfront Pricing & Free Fitting',
        'hero_sub': 'SHARJAH COMMUTER & FLEET SPECIALISTS',
        'hero_lead': 'Avoid congested industrial areas and questionable grey-market imports. Get date-fresh, GCC-certified tyres from 60+ brands delivered and fitted at reputable partner workshops across Sharjah or at your doorstep.',
        'areas_heading': 'Sharjah Neighborhood Coverage',
        'chips': ['Industrial Area 1-17', 'Al Majaz', 'Al Nahda', 'Muwaileh', 'Al Taawun', 'Al Khan', 'University City', 'Al Qasimia', 'Al Yarmook', 'Al Mirgab'],
        'local_advice_p': 'Sharjah-Dubai daily commuters experience intense stop-and-go friction on Al Ittihad Road and Sheikh Mohammed Bin Zayed Road. Frequent low-speed crawling with heavy braking accelerates shoulder tread wear; rotating tyres every 10,000 km is critical.'
    },
    {
        'slug': 'tyre-shop-ajman',
        'name': 'Ajman',
        'hero_title': 'Tyre Shop Ajman — Quality Tyres with Free Local Installation',
        'hero_sub': 'AJMAN TYRE SUPPLY & MOBILE SERVICE',
        'hero_lead': 'Buy tyres online in Ajman with complete peace of mind. Genuine brands, fresh manufacturing dates, and verified warranties fitted free at partner garages or right outside your home.',
        'areas_heading': 'Ajman Coverage Areas',
        'chips': ['Al Nuaimiya', 'Al Rashidiya', 'Al Jurf', 'Al Rawda', 'Ajman Downtown', 'Ajman Corniche', 'Al Mowaihat', 'Al Helio', 'Al Bustan'],
        'local_advice_p': 'Proximity to the coast and windblown sand in developing sectors demands regular inspection of valve stems. Replace rubber valve stems with every new tyre set to prevent slow air leaks caused by fine sand intrusion.'
    },
    {
        'slug': 'tyre-shop-ras-al-khaimah',
        'name': 'Ras Al Khaimah',
        'hero_title': 'Tyre Shop Ras Al Khaimah — Built for Coast & Mountains',
        'hero_sub': 'RAK COASTAL & JEBEL JAIS FITMENTS',
        'hero_lead': 'Whether driving coastal highways in Al Hamra or climbing Jebel Jais mountain roads, equip your car with high-traction tyres from 60+ global manufacturers delivered and fitted across RAK.',
        'areas_heading': 'Ras Al Khaimah Coverage Areas',
        'chips': ['Al Nakheel', 'Al Hamra Village', 'Mina Al Arab', 'Khuzam', 'Dafan Al Khor', 'Al Dhait', 'Marjan Island', 'Al Jazirah Al Hamra', 'Jebel Jais Access'],
        'local_advice_p': 'Twisty climbs and steep descents on Jebel Jais place immense thermal and lateral load on your front tyres. Opt for tyres with stiff outer shoulder blocks and high wet/dry traction ratings (AA or A).'
    },
    {
        'slug': 'tyre-shop-fujairah',
        'name': 'Fujairah',
        'hero_title': 'Tyre Shop Fujairah — Mountain Inclines & Coastal Humidity',
        'hero_sub': 'EAST COAST TYRE SERVICE',
        'hero_lead': 'Premium, mid-range, and budget tyres for East Coast drivers. Engineered for mountain passes on the Sheikh Khalifa Highway and coastal road stability with free local fitting in Fujairah.',
        'areas_heading': 'Fujairah Coverage Areas',
        'chips': ['Fujairah City', 'Dibba Al Fujairah', 'Al Faseel', 'Mirbah', 'Qidfa', 'Khor Fakkan Border', 'Al Hayl', 'Sakamkam'],
        'local_advice_p': 'Driving the Sheikh Khalifa Highway through the Hajar Mountains requires robust brake grip and heat dissipation. Never drive on tyres with less than 3mm of tread remaining when navigating steep descents.'
    },
    {
        'slug': 'tyre-shop-umm-al-quwain',
        'name': 'Umm Al Quwain',
        'hero_title': 'Tyre Shop Umm Al Quwain — Reliable Tyres Delivered & Fitted',
        'hero_sub': 'UAQ FAST TYRE SERVICE',
        'hero_lead': 'Convenient tyre replacement for Umm Al Quwain residents. Upfront prices, date-fresh stock from 60+ brands, and free fitting at vetted partner garages or doorstep mobile van dispatch.',
        'areas_heading': 'Umm Al Quwain Coverage Areas',
        'chips': ['Al Salamah', 'Al Raas', 'Al Riqqah', 'Falaj Al Mualla', 'UAQ Marina', 'Old Town', 'Al Madar', 'Al Ramlah'],
        'local_advice_p': 'Roads in UAQ frequently encounter sand drift from desert winds. Tyres with longitudinal water and sand ejection grooves prevent slip and ensure confident directional stability.'
    }
]

for em in EMIRATES_INFO:
    name = em['name']
    slug = em['slug']
    PAGES_CONTENT[slug] = (
        build_hero_html(
            em['hero_title'],
            em['hero_sub'],
            em['hero_lead'],
            f"WhatsApp for {name} Tyre Quote",
            f"Hi TyresVision, I need a tyre quote in {name}.",
            name
        ) +
        build_coverage_html(name, em['areas_heading'], em['chips']) +
        build_table_html(
            "UPFRONT TRANSPARENT PRICING",
            f"Popular Tyre Sizes & Starting Prices in {name}",
            f"All prices include delivery to {name}, professional mounting, computerized 3D wheel balancing, new standard valves, and old tyre eco-disposal.",
            "Tyre Size", "Common Vehicle Fitment", "Budget Tier", "Mid-Range", "Premium Tier",
            [
                {'col1': '195/65 R15', 'col2': 'Corolla, Sunny, Civic', 'col3': 'AED 165', 'col4': 'AED 240', 'col5': 'AED 360'},
                {'col1': '205/55 R16', 'col2': 'Golf, Elantra, Corolla', 'col3': 'AED 180', 'col4': 'AED 260', 'col5': 'AED 385'},
                {'col1': '215/60 R16', 'col2': 'Camry, Altima, Accord', 'col3': 'AED 195', 'col4': 'AED 280', 'col5': 'AED 410'},
                {'col1': '265/65 R17', 'col2': 'Prado, Pajero, Fortuner', 'col3': 'AED 310', 'col4': 'AED 460', 'col5': 'AED 650'},
                {'col1': '285/60 R18', 'col2': 'Land Cruiser LC200, Patrol', 'col3': 'AED 390', 'col4': 'AED 610', 'col5': 'AED 890'},
                {'col1': '275/60 R20', 'col2': 'Patrol Y62, Tahoe, Yukon', 'col3': 'AED 410', 'col4': 'AED 640', 'col5': 'AED 920'}
            ]
        ) +
        build_advice_html(
            "LOCAL ROAD CONDITIONS",
            f"Driving & Tyre Maintenance in {name}",
            em['local_advice_p'],
            [
                {'title': 'Inspect Tyre Pressure Weekly', 'desc': f'High ambient heat in {name} increases tyre pressure by 3–5 PSI while driving. Always measure pressure in the morning when tyres are cold.'},
                {'title': 'Rotate Every 10,000 KM', 'desc': 'Even out tread wear across all four wheels and prolong tyre lifespan by scheduling routine tyre rotation with our mobile vans.'},
                {'title': 'Verify the ESMA RFID Tag', 'desc': f'Avoid roadside shops selling grey imports. Every tyre supplied in {name} by TyresVision has official UAE ESMA certification and warranty.'}
            ],
            f"Hi TyresVision, I need tyre advice for driving in {name}."
        ) +
        build_faq_html(
            f"Frequently Asked Questions: Tyre Fitting in {name}",
            [
                {'q': f'How does free tyre fitting work in {name}?', 'a': f'You select your tyres and choose your preferred partner workshop in {name}. We deliver the fresh tyres there free of charge. You drive in at your appointed time, and they fit, balance, and install new valves with zero additional fees.'},
                {'q': f'Can your mobile van come to my home or office in {name}?', 'a': f'Yes! Our mobile vans are fully self-sufficient with power generators, touchless tyre changers, and computer balancers. We can fit tyres in your villa driveway or office car park anywhere in {name}.'},
                {'q': f'How fast can tyres be fitted in {name}?', 'a': f'Most popular sizes are delivered same-day or within 24 hours across {name}. Send us your size on WhatsApp and we will confirm the fastest fitting slot.'},
                {'q': 'What is included in the tyre price?', 'a': 'Every quoted price includes the tyre itself, free delivery, professional mounting, computerized dynamic wheel balancing, new standard valves, and eco-friendly disposal of your old tyres.'},
                {'q': 'How do I pay for my tyres?', 'a': 'We offer flexible payment options including credit/debit card online, payment link via WhatsApp, or cash/card upon fitting completion at the workshop.'}
            ]
        ) +
        build_cta_html(
            f"Ready to Get New Tyres in {name}?",
            f"Message our tyre specialists on WhatsApp with your tyre size. We reply in minutes with verified quotes and book your fitting in {name}.",
            f"WhatsApp Us for {name} Tyres",
            f"Hi TyresVision, I need a tyre quote in {name}."
        )
    )


def seed_ckeditor_content():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            print(f"Updating {len(PAGES_CONTENT)} pages with complete CKEditor Super-Design HTML...")
            update_sql = "UPDATE pages SET content = %s, banner_image = '/static/uploads/pages/banner_1788954653_64dd43ed.png' WHERE slug = %s"
            for slug, html_content in PAGES_CONTENT.items():
                content_json = json.dumps({'en': html_content}, ensure_ascii=False)
                cursor.execute(update_sql, (content_json, slug))
                print(f" - Updated '{slug}' (HTML length: {len(html_content)} chars)")
            conn.commit()
            print("Successfully updated all 12 pages in pages table!")
    finally:
        conn.close()


if __name__ == '__main__':
    seed_ckeditor_content()
