"""
scripts/page_builders_ev.py
Generates Page 2: EV and Hybrid Tyres in the UAE (/ev-tyres)
Redesigned with Antigravity Design Expert system matching:
- ChatGPT Image Sep 14, 2026, 02_33_30 PM.png (Full page layout & sections)
- ChatGPT Image Sep 14, 2026, 02_47_34 PM.png (Photorealistic EV background assets)
100% compliant with TyresVision-13-Page-Build-Plan 1.docx & verification audit.
"""

import urllib.parse
from page_shared_components import build_internal_links_card

def build_page_ev():
    ev_models = [
        ("Tesla Model 3", "235/45 R18, 235/40 R19, 245/35 R20", "EV-rated, acoustic foam-lined for noise"),
        ("Tesla Model Y", "255/45 R19, 255/40 R20, 255/35 R21", "Higher load index (XL/HL), EV compound"),
        ("BYD Atto 3 / Seal", "215/60 R17, 235/50 R18, 235/45 R19", "Low rolling resistance, comfort-biased"),
        ("Hyundai Ioniq 5 / Kia EV6", "235/55 R19, 255/45 R20", "Heavy battery &mdash; check load index (105W)"),
        ("Mercedes EQE / EQS", "255/45 R19, 275/45 R20, 275/35 R21", "High load capacity, MO-EV approved"),
        ("Audi e-tron / Q8 e-tron", "255/50 R19, 265/45 R21, 285/40 R22", "High load index (HL/XL), Quattro spec"),
        ("Toyota / Lexus Hybrids", "215/55 R17, 225/55 R18", "Low rolling resistance silica compound"),
        ("Polestar 2", "245/45 R19, 245/40 R20", "Performance EV compound, Brembo clearance")
    ]

    table_rows = ""
    for model, size, guidance in ev_models:
        wa_text = f"Hi TyresVision, I need a tyre price quote for {model}."
        wa_enc = urllib.parse.quote(wa_text)
        table_rows += f"""
            <tr>
              <td style="font-weight:700; color:#0F172A; white-space:nowrap;">{model}</td>
              <td style="color:#475569; font-size:0.92rem;">{size}</td>
              <td style="color:#2563FF; font-weight:600; font-size:0.92rem;">{guidance}</td>
              <td style="text-align:right;">
                <a class="tv-ev-btn-quote" href="https://wa.me/971505069575?text={wa_enc}" target="_blank" rel="noopener">
                  <span>Price Quote</span> &rarr;
                </a>
              </td>
            </tr>"""

    faqs = [
        {
            "q": "Do EV tyres really make a difference to battery range?",
            "a": "Yes. Independent tests show that low rolling resistance EV tyres can improve driving range by 7%&ndash;10% compared to standard tyres, which equates to an extra 35&ndash;50 km per full charge on a 300 km battery. Advanced silica compounds minimize energy lost to heat as the tyre flexes."
        },
        {
            "q": "Can I put normal tyres on my Tesla or BYD?",
            "a": "While standard passenger tyres may fit the wheel dimensions, they are not engineered for the 20%&ndash;30% higher curb weight of traction batteries or instantaneous electric motor torque. Normal tyres suffer accelerated shoulder scrub, generate excessive cabin road hum, and may void manufacturer chassis warranties."
        },
        {
            "q": "Why do EV tyres wear out faster than petrol car tyres?",
            "a": "Instant maximum torque from zero RPM and heavy battery curb weight (2,000&ndash;2,600 kg) place continuous shear stress on tyre tread blocks. Without specialized high-density polymer compounds and reinforced tread ribs, standard tyres can wear out in under 22,000 km in UAE summer tarmac temperatures."
        },
        {
            "q": "Can run-flat tyres on EVs and luxury cars be repaired?",
            "a": "Almost always no. Once a run-flat tyre is driven on with zero pressure, the reinforced sidewall carries the car's full weight, generating extreme internal friction that weakens internal cords. For highway safety at 120 km/h in summer heat, manufacturers strictly recommend replacement rather than repair."
        },
        {
            "q": "Can your mobile fitting van change EV tyres at my villa or office?",
            "a": "Yes. Our certified mobile vans carry specialized low-profile jacks, vehicle-specific rubber lifting pucks for EV battery-rail jacking points, and computerized laser balancers to replace and balance your tyres right inside your villa driveway or residential car park across Dubai, Abu Dhabi, and Sharjah."
        },
        {
            "q": "What is the difference between XL and HL tyre ratings?",
            "a": "XL (Extra Load) supports up to 10% higher load capacity than standard fitments. HL (High Load) is a newer international standard specifically developed for heavy electric SUVs and saloons (gross weight approaching 3,000 kg), supporting up to 25% higher load capacity at equivalent tyre pressures."
        }
    ]

    faq_html = ""
    for idx, f in enumerate(faqs):
        is_first = (idx == 0)
        open_cls = " active" if is_first else ""
        icon_char = "&minus;" if is_first else "+"
        max_h = "style=\"max-height: 250px;\"" if is_first else ""
        faq_html += f"""
      <div class="faq-item{open_cls}" style="background:#ffffff; border:1px solid #E2E8F0; border-radius:14px; margin-bottom:12px; overflow:hidden; transition:border-color 0.2s ease;">
        <button class="faq-trigger" type="button" aria-expanded="{'true' if is_first else 'false'}" style="width:100%; display:flex; justify-content:space-between; align-items:center; padding:18px 24px; background:none; border:none; text-align:left; cursor:pointer; font-size:1.02rem; font-weight:700; color:#0F172A;">
          <span>{f['q']}</span>
          <span class="faq-icon" style="font-size:1.3rem; font-weight:400; color:#2563FF; margin-left:14px; flex-shrink:0;">{icon_char}</span>
        </button>
        <div class="faq-answer" {max_h} style="transition:max-height 0.3s cubic-bezier(0,1,0,1);">
          <div class="faq-answer-inner" style="padding:0 24px 20px 24px;">
            <p style="margin:0; font-size:0.95rem; line-height:1.7; color:#475569;">{f['a']}</p>
          </div>
        </div>
      </div>"""

    return f"""
<!-- 1. HERO SECTION -->
<section class="tv-ev-hero">
  <div class="wrap">
    <nav class="about-breadcrumb" aria-label="Breadcrumb" style="margin-bottom: 20px;">
      <a href="/">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>
        <span>Home</span>
      </a>
      <span class="sep" aria-hidden="true">/</span>
      <span class="current">EV Tyres</span>
    </nav>

    <div class="tv-ev-hero-grid">
      <div class="tv-ev-hero-content">
        <h1 class="tv-ev-hero-h1">EV and Hybrid Tyres in the UAE</h1>
        <p class="tv-ev-hero-lead">High load rated (HL/XL), low rolling resistance tyres engineered for instantaneous electric torque. Fitted at a partner centre or doorstep mobile van across the UAE.</p>
      </div>
    </div>
  </div>
</section>

<!-- 2. WHY ELECTRIC CARS NEED DEDICATED EV TYRES -->
<section class="tv-section-block" style="background:#ffffff; padding: clamp(54px, 7vw, 84px) 0;">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow" style="color:#2563FF; font-weight:800; font-size:0.82rem; letter-spacing:0.12em; text-transform:uppercase;">&bull; ENGINEERING SPECIFICATIONS &bull;</span>
      <h2 style="font-size:clamp(1.9rem, 3.2vw, 2.5rem); font-weight:800; color:#0F172A; margin:10px 0 14px 0; letter-spacing:-0.02em;">Why an electric car needs different tyres</h2>
      <p style="font-size:1.05rem; line-height:1.75; color:#475569; max-width:820px; margin:0 auto;">Instantaneous electric torque and heavy battery packs put extraordinary shear stress on rubber. In UAE's hot climate, EV-specific tyres ensure safety, efficiency and longer life.</p>
    </div>

    <div class="tv-ev-grid-4">
      <!-- Card 1 -->
      <div class="tv-ev-feature-card">
        <div class="tv-ev-icon-circle">
          <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="3"/>
            <path d="M12 3v3M12 18v3M3 12h3M18 12h3"/>
          </svg>
        </div>
        <h3 style="font-size:1.18rem; font-weight:800; color:#0F172A; margin:0 0 10px 0;">Stiffer Sidewall &amp; HL Casing</h3>
        <p style="font-size:0.92rem; line-height:1.65; color:#475569; margin:0;">Engineered to support 2,000&ndash;2,600 kg curb weights without excessive flex, reducing sidewall deflection and preventing high-speed blowouts.</p>
      </div>

      <!-- Card 2 -->
      <div class="tv-ev-feature-card">
        <div class="tv-ev-icon-circle">
          <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M11 5L6 9H2v6h4l5 4V5z"/>
            <line x1="23" y1="9" x2="17" y2="15"/>
            <line x1="17" y1="9" x2="23" y2="15"/>
          </svg>
        </div>
        <h3 style="font-size:1.18rem; font-weight:800; color:#0F172A; margin:0 0 10px 0;">Acoustic Sound-Dampening Foam</h3>
        <p style="font-size:0.92rem; line-height:1.65; color:#475569; margin:0;">Special polyurethane foam layer absorbs cabin resonance, delivering a whisper-quiet, serene ride in an otherwise silent electric cabin.</p>
      </div>

      <!-- Card 3 -->
      <div class="tv-ev-feature-card">
        <div class="tv-ev-icon-circle">
          <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
          </svg>
        </div>
        <h3 style="font-size:1.18rem; font-weight:800; color:#0F172A; margin:0 0 10px 0;">Low Rolling Resistance Silica</h3>
        <p style="font-size:0.92rem; line-height:1.65; color:#475569; margin:0;">Advanced silica polymers reduce energy loss and heat buildup, actively extending vehicle battery driving range by 7% to 10%.</p>
      </div>

      <!-- Card 4 -->
      <div class="tv-ev-feature-card">
        <div class="tv-ev-icon-circle">
          <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            <path d="M9 12l2 2 4-4"/>
          </svg>
        </div>
        <h3 style="font-size:1.18rem; font-weight:800; color:#0F172A; margin:0 0 10px 0;">Safe Doorstep Mobile Fitting</h3>
        <p style="font-size:0.92rem; line-height:1.65; color:#475569; margin:0;">Our mobile vans carry dedicated vehicle-specific rubber lifting pucks and precision low-profile jacks to safely handle high-voltage EVs.</p>
      </div>
    </div>
  </div>
</section>

<!-- 3. TYRES BY ELECTRIC AND HYBRID MODEL -->
<section class="price-section tv-section-block" style="background:#F8FAFC; padding: clamp(54px, 7vw, 84px) 0;">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow" style="color:#2563FF; font-weight:800; font-size:0.82rem; letter-spacing:0.12em; text-transform:uppercase;">&bull; POPULAR EV &amp; HYBRID VEHICLES &bull;</span>
      <h2 style="font-size:clamp(1.9rem, 3.2vw, 2.5rem); font-weight:800; color:#0F172A; margin:10px 0 14px 0; letter-spacing:-0.02em;">Tyres by electric and hybrid model</h2>
      <p style="font-size:1.05rem; line-height:1.75; color:#475569; max-width:820px; margin:0 auto;">Factory dimensions, recommended load indexes, and specifications for top electric and hybrid vehicles in Dubai and Abu Dhabi.</p>
    </div>

    <!-- Guarantees Strip -->
    <div class="tv-ev-guarantees-grid">
      <div class="tv-ev-guarantee-card">
        <div class="tv-ev-guarantee-icon"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg></div>
        <div class="tv-ev-guarantee-text"><div class="tv-ev-guarantee-title">No Hidden Extras</div><div class="tv-ev-guarantee-sub">Inclusive fitting &amp; balancing</div></div>
      </div>
      <div class="tv-ev-guarantee-card">
        <div class="tv-ev-guarantee-icon"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg></div>
        <div class="tv-ev-guarantee-text"><div class="tv-ev-guarantee-title">100% Genuine Certified</div><div class="tv-ev-guarantee-sub">Direct from authorised distributors</div></div>
      </div>
      <div class="tv-ev-guarantee-card">
        <div class="tv-ev-guarantee-icon"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><rect x="1" y="3" width="15" height="13"></rect><polygon points="16 8 20 8 23 11 23 16 16 16 8"></polygon><circle cx="5.5" cy="18.5" r="2.5"></circle><circle cx="18.5" cy="18.5" r="2.5"></circle></svg></div>
        <div class="tv-ev-guarantee-text"><div class="tv-ev-guarantee-title">Doorstep Mobile Vans</div><div class="tv-ev-guarantee-sub">Fitting at your home or office</div></div>
      </div>
      <div class="tv-ev-guarantee-card">
        <div class="tv-ev-guarantee-icon"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg></div>
        <div class="tv-ev-guarantee-text"><div class="tv-ev-guarantee-title">Fresh Production Dates</div><div class="tv-ev-guarantee-sub">Latest stock, maximum life</div></div>
      </div>
    </div>

    <!-- Table Card Container -->
    <div class="price-table-card" style="background:#ffffff; border:1px solid #E2E8F0; border-radius:18px; box-shadow:0 8px 30px rgba(15,23,42,0.06); overflow:hidden;">
      <div class="price-table-scroll" style="overflow-x:auto;">
        <table class="tv-ev-table" aria-label="Tyres by Electric and Hybrid Model">
          <thead>
            <tr>
              <th scope="col">Vehicle Model</th>
              <th scope="col">Common Tyre Sizes</th>
              <th scope="col">What to Look For</th>
              <th scope="col" style="text-align:right;">Action</th>
            </tr>
          </thead>
          <tbody>
            {table_rows}
          </tbody>
        </table>
      </div>
    </div>
  </div>
</section>

<!-- 4. CRUCIAL ADVICE FOR UAE ELECTRIC CAR DRIVERS -->
<section class="tv-section-block" style="background:#ffffff; padding: clamp(54px, 7vw, 84px) 0;">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow" style="color:#2563FF; font-weight:800; font-size:0.82rem; letter-spacing:0.12em; text-transform:uppercase;">&bull; POPULAR &amp; LONGEVITY GUIDANCE &bull;</span>
      <h2 style="font-size:clamp(1.9rem, 3.2vw, 2.5rem); font-weight:800; color:#0F172A; margin:10px 0 14px 0; letter-spacing:-0.02em;">Crucial advice for UAE electric car drivers</h2>
      <p style="font-size:1.05rem; line-height:1.75; color:#475569; max-width:820px; margin:0 auto;">Key technical guidelines on load rating, tyre rotation, and run-flats to maximise tyre lifespan and protect your battery.</p>
    </div>

    <div class="tv-ev-grid-3">
      <!-- Advice Card 1: Load index & HL -->
      <div class="tv-ev-advice-card">
        <div class="tv-ev-icon-circle">
          <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>
          </svg>
        </div>
        <h3 style="font-size:1.25rem; font-weight:800; color:#0F172A; margin:0 0 12px 0;">Check the &ldquo;HL&rdquo; (High Load) Rating</h3>
        <p style="font-size:0.95rem; line-height:1.7; color:#475569; margin:0 0 12px 0;">EVs are heavier than petrol cars. Always choose HL or XL rated tyres to handle the extra battery mass safely, especially during extreme summer highway heat.</p>
        <p style="font-size:0.88rem; line-height:1.6; color:#64748B; margin:0;">On heavy EVs like Tesla Model X or Mercedes EQE, standard tyres overheat at 120 km/h, leading to ply separation. HL is strictly non-negotiable.</p>
      </div>

      <!-- Advice Card 2: Why EV tyres wear faster & rotation -->
      <div class="tv-ev-advice-card">
        <div class="tv-ev-icon-circle">
          <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/>
          </svg>
        </div>
        <h3 style="font-size:1.25rem; font-weight:800; color:#0F172A; margin:0 0 12px 0;">Rotate Tyres Every 8,000&ndash;10,000 KM</h3>
        <p style="font-size:0.95rem; line-height:1.7; color:#475569; margin:0 0 12px 0;">Instant torque delivery and heavy regenerative braking induce rapid shoulder scrub. Regular rotation balances wear across driven axles and extends tyre lifespan.</p>
        <p style="font-size:0.88rem; line-height:1.6; color:#64748B; margin:0;">Dual-motor all-wheel-drive configurations bias power delivery dynamically, causing asymmetrical outer edge wear without timely rotations.</p>
      </div>

      <!-- Advice Card 3: Run-flat vs normal tyres -->
      <div class="tv-ev-advice-card">
        <div class="tv-ev-icon-circle">
          <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="2" y="7" width="20" height="14" rx="2" ry="2"/>
            <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>
          </svg>
        </div>
        <h3 style="font-size:1.25rem; font-weight:800; color:#0F172A; margin:0 0 12px 0;">Run-Flat vs Normal Tyre Swaps</h3>
        <p style="font-size:0.95rem; line-height:1.7; color:#475569; margin:0 0 12px 0;">You can switch from harsh run-flats to standard tyres for superior comfort and lower costs. Ensure you carry an emergency 12V inflator kit as most EVs lack a spare.</p>
        <p style="font-size:0.88rem; line-height:1.6; color:#64748B; margin:0;">Standard tyres absorb road bumps significantly better, decreasing high-frequency chassis vibration transmitted into sensitive electronics.</p>
      </div>
    </div>

    <!-- Centered WhatsApp Consultation -->
    <div style="display:flex; justify-content:center; align-items:center; gap:16px; flex-wrap:wrap; margin-top:40px;">
      <a class="tv-btn-wa-green" href="https://wa.me/971505069575?text=Hi%20TyresVision%2C%20please%20verify%20the%20HL%20load%20rating%20for%20my%20electric%20car." target="_blank" rel="noopener">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.46 1.32 4.96L2 22l5.25-1.38a9.9 9.9 0 004.79 1.22h.01c5.46 0 9.91-4.45 9.91-9.91C21.96 6.45 17.5 2 12.04 2zm5.8 14.06c-.24.68-1.42 1.31-1.96 1.36-.54.05-1.04.24-3.52-.73-2.99-1.18-4.86-4.29-5.01-4.49-.15-.2-1.2-1.6-1.2-3.05 0-1.45.76-2.16 1.03-2.46.27-.29.59-.37.78-.37s.39 0 .56.01c.18.01.42-.07.66.5.24.59.83 2.03.9 2.18.07.15.12.32.02.51-.1.2-.15.32-.29.5s-.3.4-.43.53c-.15.15-.3.31-.13.6.17.29.76 1.25 1.62 2.02 1.11.99 2.05 1.3 2.34 1.45.29.15.46.12.63-.07.17-.2.73-.85.92-1.14.2-.29.39-.24.66-.15.27.1 1.71.81 2 .96.29.15.49.22.56.34.07.13.07.75-.17 1.43z"/></svg>
        <span>Ask Our Tyre Specialists on WhatsApp</span>
      </a>
      <a class="tv-btn-white-pill" href="tel:+971505069575">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M6.62 10.79a15.05 15.05 0 006.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1C10.4 21 3 13.6 3 4.5 3 3.95 3.45 3.5 4 3.5h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/></svg>
        <span>+971 50 506 9575</span>
      </a>
    </div>
  </div>
</section>

<!-- 5. FREQUENTLY ASKED QUESTIONS ABOUT EV TYRES -->
<section class="tv-section-block" style="background:#F8FAFC; padding: clamp(54px, 7vw, 84px) 0;">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow" style="color:#2563FF; font-weight:800; font-size:0.82rem; letter-spacing:0.12em; text-transform:uppercase;">&bull; FREQUENTLY ASKED QUESTIONS &bull;</span>
      <h2 style="font-size:clamp(1.9rem, 3.2vw, 2.5rem); font-weight:800; color:#0F172A; margin:10px 0 14px 0; letter-spacing:-0.02em;">Frequently Asked Questions About EV Tyres</h2>
      <p style="font-size:1.05rem; line-height:1.75; color:#475569; max-width:820px; margin:0 auto 36px auto;">Essential questions answered on battery range, tyre sizes, and balancing.</p>
    </div>

    <div class="faq-accordion" style="max-width:860px; margin:0 auto;">
      {faq_html}
    </div>

    {build_internal_links_card('Explore our catalog of certified <a href="/tyre-brands" style="color:#2563FF; font-weight:700; text-decoration:underline;">tyre brands</a>, verify your exact <a href="/tyre-sizes" style="color:#2563FF; font-weight:700; text-decoration:underline;">tyre sizes</a>, or look up recommended <a href="/tyres-by-car" style="color:#2563FF; font-weight:700; text-decoration:underline;">tyres for your car model</a>. Need mobile doorstep service? Book our <a href="/mobile-tyre-fitting" style="color:#2563FF; font-weight:700; text-decoration:underline;">mobile tyre fitting</a> vans with specialized EV jacking equipment.')}
  </div>
</section>

<!-- 6. BOTTOM CTA HERO BANNER -->
<section class="tv-ev-bottom-cta">
  <div class="wrap">
    <div class="tv-ev-bottom-grid">
      <h2 style="font-size:clamp(2rem, 3.6vw, 2.8rem); font-weight:800; color:#ffffff; margin:0 0 14px 0; letter-spacing:-0.02em; text-shadow:0 2px 10px rgba(0,0,0,0.35);">Ready to Fit the Right Tyres on Your EV?</h2>
      <p style="font-size:1.08rem; line-height:1.75; color:rgba(255,255,255,0.92); margin:0 0 28px 0; max-width:620px; text-shadow:0 1px 4px rgba(0,0,0,0.25);">Send your tyre size or car model on WhatsApp. Our specialists confirm EV-rated options and book free mobile van fitting today.</p>
      
      <div style="display:flex; align-items:center; gap:14px; flex-wrap:wrap;">
        <a class="tv-btn-wa-green" href="https://wa.me/971505069575?text=Hi%20TyresVision%2C%20I%20need%20an%20exact%20tyre%20quote%20for%20my%20electric%20vehicle." target="_blank" rel="noopener">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.46 1.32 4.96L2 22l5.25-1.38a9.9 9.9 0 004.79 1.22h.01c5.46 0 9.91-4.45 9.91-9.91C21.96 6.45 17.5 2 12.04 2zm5.8 14.06c-.24.68-1.42 1.31-1.96 1.36-.54.05-1.04.24-3.52-.73-2.99-1.18-4.86-4.29-5.01-4.49-.15-.2-1.2-1.6-1.2-3.05 0-1.45.76-2.16 1.03-2.46.27-.29.59-.37.78-.37s.39 0 .56.01c.18.01.42-.07.66.5.24.59.83 2.03.9 2.18.07.15.12.32.02.51-.1.2-.15.32-.29.5s-.3.4-.43.53c-.15.15-.3.31-.13.6.17.29.76 1.25 1.62 2.02 1.11.99 2.05 1.3 2.34 1.45.29.15.46.12.63-.07.17-.2.73-.85.92-1.14.2-.29.39-.24.66-.15.27.1 1.71.81 2 .96.29.15.49.22.56.34.07.13.07.75-.17 1.43z"/></svg>
          <span>WhatsApp for EV Tyre Quote</span>
        </a>
        <a class="tv-btn-white-pill" href="tel:+971505069575">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M6.62 10.79a15.05 15.05 0 006.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1C10.4 21 3 13.6 3 4.5 3 3.95 3.45 3.5 4 3.5h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/></svg>
          <span>Call +971 50 506 9575</span>
        </a>
      </div>

      <div class="tv-ev-bottom-badges">
        <div class="tv-ev-bottom-badge-item">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
          <span>Open daily across all 7 Emirates</span>
        </div>
        <div class="tv-ev-bottom-badge-item">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="1" y="3" width="15" height="13"></rect><polygon points="16 8 20 8 23 11 23 16 16 16 8"></polygon><circle cx="5.5" cy="18.5" r="2.5"></circle><circle cx="18.5" cy="18.5" r="2.5"></circle></svg>
          <span>Fast mobile vans &amp; partner centres</span>
        </div>
        <div class="tv-ev-bottom-badge-item">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg>
          <span>Expert advice on EV tyre brands</span>
        </div>
      </div>
    </div>
  </div>
</section>
"""
