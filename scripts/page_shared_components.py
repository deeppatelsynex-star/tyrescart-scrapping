"""
scripts/page_shared_components.py
Shared high-fidelity UI components for TyresVision 13 CMS pages.
Uses brand blue #2563FF, emerald CTAs, responsive tables, interactive FAQ accordions,
and full mobile-friendly layout.
"""

import urllib.parse

def build_hero_section(title, eyebrow, lead, wa_text, wa_msg, breadcrumb_label="Page", default_emirate="Dubai"):
    wa_encoded = urllib.parse.quote(wa_msg)
    emirates = ["Dubai", "Abu Dhabi", "Sharjah", "Ajman", "Ras Al Khaimah", "Fujairah", "Umm Al Quwain"]
    options_html = ""
    for em in emirates:
        sel = " selected" if em.lower() == default_emirate.lower() else ""
        options_html += f'<option{sel}>{em}</option>'

    return f"""
<!-- 1. HERO SECTION -->
<section class="tv-page-hero">
  <div class="wrap hero-grid">
    <div class="tv-hero-left">
      <nav class="about-breadcrumb" aria-label="Breadcrumb" style="margin-bottom: 20px; display: flex; align-items: center; flex-wrap: wrap; gap: 6px;">
        <a href="/">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>
          <span>Home</span>
        </a>
        <span class="sep" aria-hidden="true">/</span>
        <span class="current">{breadcrumb_label}</span>
        <span class="breadcrumb-eyebrow" style="color:#38bdf8; font-weight:700; font-size:0.84rem; letter-spacing:0.06em; margin-left:4px;">&mdash; {eyebrow}</span>
      </nav>
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
              {options_html}
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


def build_guarantees_strip():
    return """
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
"""


def build_faq_section(title, faqs, eyebrow="FREQUENTLY ASKED QUESTIONS"):
    items_html = ""
    for idx, f in enumerate(faqs):
        is_active = " active" if idx == 0 else ""
        expanded = "true" if idx == 0 else "false"
        items_html += f"""
      <div class="faq-item{is_active}" data-faq-item>
        <button type="button" class="faq-summary" aria-expanded="{expanded}">
          <span class="faq-question-text">{f['q']}</span>
          <span class="faq-chevron-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
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
<!-- FAQ SECTION -->
<section class="faq tv-section-block" style="background:#F8FAFC;">
  <div class="wrap" style="max-width:860px">
    <div class="center tv-section-head">
      <span class="eyebrow">&mdash; {eyebrow} &mdash;</span>
      <h2>{title}</h2>
      <p class="lead">Answers to key questions from drivers across the Emirates.</p>
    </div>
    <div class="faq-list" style="margin-top:36px;">
{items_html}
    </div>
  </div>
</section>
"""


def build_bottom_cta(heading, lead, wa_msg, wa_btn_text="WhatsApp Our Specialists"):
    wa_encoded = urllib.parse.quote(wa_msg)
    return f"""
<!-- BOTTOM CTA SECTION -->
<section class="tv-4x4-bottom-cta">
  <div class="wrap">
    <div class="tv-4x4-bottom-grid">
      <div>
        <h2 style="font-size:clamp(1.9rem, 3.4vw, 2.6rem); font-weight:800; color:#ffffff; margin:0 0 14px 0; letter-spacing:-0.02em;">{heading}</h2>
        <p style="font-size:1.05rem; line-height:1.7; color:rgba(255,255,255,0.92); margin:0 0 28px 0; max-width:620px;">{lead}</p>
        <div style="display:flex; align-items:center; gap:14px; flex-wrap:wrap;">
          <a class="tv-btn-wa-green" href="https://wa.me/971505069575?text={wa_encoded}" target="_blank" rel="noopener">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.46 1.32 4.96L2 22l5.25-1.38a9.9 9.9 0 004.79 1.22h.01c5.46 0 9.91-4.45 9.91-9.91C21.96 6.45 17.5 2 12.04 2zm5.8 14.06c-.24.68-1.42 1.31-1.96 1.36-.54.05-1.04.24-3.52-.73-2.99-1.18-4.86-4.29-5.01-4.49-.15-.2-1.2-1.6-1.2-3.05 0-1.45.76-2.16 1.03-2.46.27-.29.59-.37.78-.37s.39 0 .56.01c.18.01.42-.07.66.5.24.59.83 2.03.9 2.18.07.15.12.32.02.51-.1.2-.15.32-.29.5s-.3.4-.43.53c-.15.15-.3.31-.13.6.17.29.76 1.25 1.62 2.02 1.11.99 2.05 1.3 2.34 1.45.29.15.46.12.63-.07.17-.2.73-.85.92-1.14.2-.29.39-.24.66-.15.27.1 1.71.81 2 .96.29.15.49.22.56.34.07.13.07.75-.17 1.43z"/></svg>
            <span>{wa_btn_text}</span>
          </a>
          <a class="tv-btn-white-pill" href="tel:+971505069575">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M6.62 10.79a15.05 15.05 0 006.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1C10.4 21 3 13.6 3 4.5 3 3.95 3.45 3.5 4 3.5h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/></svg>
            <span>Call +971 50 506 9575</span>
          </a>
        </div>
      </div>
      <div class="tv-4x4-bottom-badges-list">
        <div class="tv-4x4-bottom-badge-item">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg>
          <span>Free fitting across Dubai, Abu Dhabi &amp; Sharjah</span>
        </div>
        <div class="tv-4x4-bottom-badge-item">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>
          <span>Expert advice on tyre sizes &amp; brands</span>
        </div>
        <div class="tv-4x4-bottom-badge-item">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="1" y="3" width="15" height="13"></rect><polygon points="16 8 20 8 23 11 23 16 16 16 8"></polygon><circle cx="5.5" cy="18.5" r="2.5"></circle><circle cx="18.5" cy="18.5" r="2.5"></circle></svg>
          <span>Mobile van fitting at your location</span>
        </div>
        <div class="tv-4x4-bottom-badge-item">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>
          <span>Trusted by 7,000+ UAE drivers</span>
        </div>
      </div>
    </div>
  </div>
</section>
"""


def build_internal_links_card(text_content):
    return f"""
    <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:14px; padding:20px 24px; text-align:center; margin-top:24px;">
      <p style="margin:0; font-size:1rem; line-height:1.7; color:#334155;">
        {text_content}
      </p>
    </div>
"""
