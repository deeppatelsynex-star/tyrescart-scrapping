"""
scripts/page_builders_locations.py
Generates Pages 7 through 13: The 7 Location Pages
Exact match to specifications in 'TyresVision-13-Page-Build-Plan 1.docx'.
Shared structure, fresh unique copy, distinct local angles, and strict internal linking.
"""

import urllib.parse
from page_shared_components import (
    build_hero_section,
    build_guarantees_strip,
    build_faq_section,
    build_bottom_cta,
    build_internal_links_card
)

def build_location_common_price_table(emirate_name):
    sizes = [
        ("195/65 R15", "Corolla, Sunny, Civic", "From AED 160", "From AED 240", "From AED 340"),
        ("205/55 R16", "Elantra, Golf, Cerato", "From AED 185", "From AED 280", "From AED 390"),
        ("215/55 R17", "Camry, Accord, Altima", "From AED 210", "From AED 310", "From AED 460"),
        ("225/65 R17", "RAV4, CR-V, X-Trail", "From AED 240", "From AED 340", "From AED 490"),
        ("235/55 R19", "Santa Fe, Sorento, RX", "From AED 290", "From AED 420", "From AED 620"),
        ("265/65 R17", "Prado, Fortuner, Hilux", "From AED 290", "From AED 420", "From AED 610"),
        ("285/60 R18", "Land Cruiser LC200/300", "From AED 380", "From AED 520", "From AED 790"),
        ("275/60 R20", "Patrol, Tahoe, Yukon", "From AED 380", "From AED 540", "From AED 840")
    ]
    rows = ""
    for sz, cars, val_p, mid_p, prem_p in sizes:
        msg = f"Hi TyresVision, I need tyre prices for {sz} ({cars}) in {emirate_name}."
        enc = urllib.parse.quote(msg)
        rows += f"""
        <tr>
          <td style="font-weight:800; color:#0F172A; white-space:nowrap;">{sz}</td>
          <td style="color:#475569; font-size:0.9rem;">{cars}</td>
          <td style="font-weight:700; color:#0F172A;">{val_p}</td>
          <td style="font-weight:700; color:#2563FF;">{mid_p}</td>
          <td style="font-weight:700; color:#0F172A;">{prem_p}</td>
          <td style="text-align:right;"><a class="get-quote-link" href="https://wa.me/971505069575?text={enc}" target="_blank" rel="noopener"><span>Quote</span> &rarr;</a></td>
        </tr>
        """
    return f"""
    <div class="price-table-card" style="margin-top:28px;">
      <div class="price-table-scroll">
        <table class="price-table tv-4x4-table" aria-label="Tyre Prices in {emirate_name}">
          <thead>
            <tr>
              <th scope="col">Tyre Size</th>
              <th scope="col">Common Vehicles</th>
              <th scope="col">Value Tier</th>
              <th scope="col">Mid-Range</th>
              <th scope="col">Premium Tier</th>
              <th scope="col" style="text-align:right;">Action</th>
            </tr>
          </thead>
          <tbody>
            {rows}
          </tbody>
        </table>
      </div>
    </div>
    """

def build_how_it_works_section(emirate_name):
    return f"""
<!-- HOW IT WORKS -->
<section class="tv-section-block" style="background:#ffffff;">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow">&mdash; SIMPLE 4-STEP PROCESS &mdash;</span>
      <h2>How it works</h2>
      <p class="lead">Ordering new tyres in {emirate_name} takes less than 3 minutes on WhatsApp.</p>
    </div>

    <div class="grid g4" style="margin-top:28px;">
      <div class="card" style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:14px; padding:22px; text-align:center;">
        <div style="width:42px; height:42px; border-radius:50%; background:#2563FF; color:#fff; display:flex; align-items:center; justify-content:center; font-weight:800; margin:0 auto 12px auto;">1</div>
        <h3 style="font-size:1.05rem; font-weight:800; color:#0F172A; margin:0 0 8px 0;">Share Tyre Size</h3>
        <p style="font-size:0.86rem; color:#64748B; margin:0;">Send your tyre size, vehicle make, or a photo of your sidewall to our WhatsApp number.</p>
      </div>

      <div class="card" style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:14px; padding:22px; text-align:center;">
        <div style="width:42px; height:42px; border-radius:50%; background:#2563FF; color:#fff; display:flex; align-items:center; justify-content:center; font-weight:800; margin:0 auto 12px auto;">2</div>
        <h3 style="font-size:1.05rem; font-weight:800; color:#0F172A; margin:0 0 8px 0;">Receive Live Options</h3>
        <p style="font-size:0.86rem; color:#64748B; margin:0;">We send transparent quotes across value, mid-range, and premium tiers with verified DOT dates.</p>
      </div>

      <div class="card" style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:14px; padding:22px; text-align:center;">
        <div style="width:42px; height:42px; border-radius:50%; background:#2563FF; color:#fff; display:flex; align-items:center; justify-content:center; font-weight:800; margin:0 auto 12px auto;">3</div>
        <h3 style="font-size:1.05rem; font-weight:800; color:#0F172A; margin:0 0 8px 0;">Select Fitting Choice</h3>
        <p style="font-size:0.86rem; color:#64748B; margin:0;">Choose free installation at a partner garage in {emirate_name} or book our doorstep mobile van.</p>
      </div>

      <div class="card" style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:14px; padding:22px; text-align:center;">
        <div style="width:42px; height:42px; border-radius:50%; background:#2563FF; color:#fff; display:flex; align-items:center; justify-content:center; font-weight:800; margin:0 auto 12px auto;">4</div>
        <h3 style="font-size:1.05rem; font-weight:800; color:#0F172A; margin:0 0 8px 0;">Fitted &amp; Balanced</h3>
        <p style="font-size:0.86rem; color:#64748B; margin:0;">Tyres mounted, computerized 3D laser balanced, new valves installed, and old tyres recycled.</p>
      </div>
    </div>
  </div>
</section>
"""

# ==============================================================================
# PAGE 7: Tyre Shop Dubai (/tyre-shop-dubai)
# ==============================================================================
def build_page_dubai():
    hero = build_hero_section(
        title="Tyre Shop in Dubai — Tyres Fitted Near You",
        eyebrow="DUBAI FITTING HUBS & DOORSTEP MOBILE VANS",
        lead="Looking for a tyre shop in Dubai? 60+ brands delivered and fitted free at a centre near you, from Al Quoz to Deira. Send your size on WhatsApp.",
        wa_text="WhatsApp for Dubai Quote",
        wa_msg="Hi TyresVision, I'd like a tyre price in Dubai.",
        breadcrumb_label="Tyre Shop Dubai",
        default_emirate="Dubai"
    )

    faqs = [
        {
            "q": "Where are your partner tyre fitting centres in Dubai?",
            "a": "We have certified partner fitting workshops across Al Quoz (Industrial 1, 3, 4), Deira, Bur Dubai, Al Barsha, JLT/Marina vicinity, Mirdif, Al Qusais, and Dubai Investment Park (DIP)."
        },
        {
            "q": "How fast can you fit tyres in Dubai?",
            "a": "Same-day fitting is available 7 days a week. For warehouse stock, tyres are dispatched to your chosen partner garage or loaded onto our mobile van within 2 to 4 hours."
        },
        {
            "q": "Is wheel balancing and valve replacement included in Dubai?",
            "a": "Yes! All tyre purchases include free tyre fitting, computerized dynamic wheel balancing, new rubber valves, and environmental disposal of your old tyres."
        },
        {
            "q": "Can you change tyres in my apartment car park in Dubai Marina or Downtown?",
            "a": "Yes. Our mobile fitting vans carry low-profile jacks and compact tyre changers. As long as building security grants visitor access to parking bays, our technicians complete the entire service on site."
        },
        {
            "q": "How does Dubai summer heat affect tyre life?",
            "a": "Sustained high speeds on Sheikh Zayed Road combined with asphalt temperatures exceeding 55°C accelerate rubber oxidation. In Dubai, tyres should be replaced after 40,000 to 50,000 km or 4 to 5 years regardless of remaining tread."
        }
    ]

    return f"""{hero}

<!-- FITTING CENTRES ACROSS DUBAI -->
<section class="tv-section-block" style="background:#ffffff;">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow">&mdash; LOCAL WORKSHOP NETWORK &mdash;</span>
      <h2>Tyre fitting centres across Dubai</h2>
      <p class="lead">Conveniently located partner workshops grouped across Dubai's major commercial and residential hubs.</p>
    </div>

    <div class="grid g3" style="margin-top:28px;">
      <div class="card" style="border:1px solid #E2E8F0; border-radius:14px; padding:24px;">
        <h3 style="font-size:1.15rem; font-weight:800; color:#0F172A; margin:0 0 10px 0;">Al Quoz &amp; Business Bay</h3>
        <p style="font-size:0.9rem; line-height:1.65; color:#475569; margin:0;">Serving Downtown, Business Bay, DIFC, and Al Quoz Industrial 1, 3 &amp; 4 with rapid workshop access.</p>
      </div>
      <div class="card" style="border:1px solid #E2E8F0; border-radius:14px; padding:24px;">
        <h3 style="font-size:1.15rem; font-weight:800; color:#0F172A; margin:0 0 10px 0;">Deira &amp; Bur Dubai</h3>
        <p style="font-size:0.9rem; line-height:1.65; color:#475569; margin:0;">Established fitting locations in Port Saeed, Al Rigga, Karama, and central Old Dubai communities.</p>
      </div>
      <div class="card" style="border:1px solid #E2E8F0; border-radius:14px; padding:24px;">
        <h3 style="font-size:1.15rem; font-weight:800; color:#0F172A; margin:0 0 10px 0;">Marina, JLT &amp; Al Barsha</h3>
        <p style="font-size:0.9rem; line-height:1.65; color:#475569; margin:0;">Close to Dubai Marina, JBR, Jumeirah Lake Towers, The Greens, Al Barsha 1, and Barsha Heights.</p>
      </div>
      <div class="card" style="border:1px solid #E2E8F0; border-radius:14px; padding:24px;">
        <h3 style="font-size:1.15rem; font-weight:800; color:#0F172A; margin:0 0 10px 0;">Mirdif, Al Qusais &amp; Silicon Oasis</h3>
        <p style="font-size:0.9rem; line-height:1.65; color:#475569; margin:0;">East Dubai coverage across Al Qusais Industrial 1&ndash;5, Mirdif, Warqa'a, and Dubai Silicon Oasis.</p>
      </div>
      <div class="card" style="border:1px solid #E2E8F0; border-radius:14px; padding:24px;">
        <h3 style="font-size:1.15rem; font-weight:800; color:#0F172A; margin:0 0 10px 0;">Jebel Ali &amp; Dubai South</h3>
        <p style="font-size:0.9rem; line-height:1.65; color:#475569; margin:0;">Equipped for heavy commercial, fleet, and private vehicles near DIP 1 &amp; 2, Expo City, and Jebel Ali.</p>
      </div>
      <div class="card" style="border:1px solid #E2E8F0; border-radius:14px; padding:24px;">
        <h3 style="font-size:1.15rem; font-weight:800; color:#0F172A; margin:0 0 10px 0;">Jumeirah &amp; Umm Suqeim</h3>
        <p style="font-size:0.9rem; line-height:1.65; color:#475569; margin:0;">Premium workshops catering to luxury saloons and family SUVs across Jumeirah 1&ndash;3 and Umm Suqeim.</p>
      </div>
    </div>
  </div>
</section>

<!-- DELIVERED FREE & OR WE COME TO YOU -->
<section class="tv-section-block" style="background:#F8FAFC;">
  <div class="wrap">
    <div class="grid g2">
      <div class="card" style="background:#ffffff; border:1px solid #E2E8F0; border-radius:18px; padding:32px;">
        <span class="eyebrow" style="color:#2563FF; font-weight:800; font-size:0.8rem;">WORKSHOP INSTALLATION</span>
        <h2 style="font-size:1.5rem; font-weight:800; color:#0F172A; margin:8px 0 12px 0;">Tyres delivered free to your nearest centre</h2>
        <p style="font-size:0.98rem; line-height:1.7; color:#475569; margin:0 0 16px 0;">Order your tyres online through WhatsApp, and we dispatch them straight from climate-controlled central logistics to your chosen partner centre in Dubai. When you arrive, the tyres are waiting &mdash; mounting and 3D balancing take under 45 minutes.</p>
      </div>

      <div class="card" style="background:#ffffff; border:1px solid #E2E8F0; border-radius:18px; padding:32px;">
        <span class="eyebrow" style="color:#2563FF; font-weight:800; font-size:0.8rem;">DOORSTEP CONVENIENCE</span>
        <h2 style="font-size:1.5rem; font-weight:800; color:#0F172A; margin:8px 0 12px 0;">Or we come to you</h2>
        <p style="font-size:0.98rem; line-height:1.7; color:#475569; margin:0 0 16px 0;">Don't want to spend your weekend in an industrial area? Our fully equipped <a href="/mobile-tyre-fitting" style="color:#2563FF; font-weight:700; text-decoration:underline;">mobile tyre fitting</a> vans come directly to your villa driveway or office parking bay anywhere in Dubai.</p>
      </div>
    </div>
  </div>
</section>

<!-- TYRE PRICES IN DUBAI -->
<section class="price-section tv-section-block" style="background:#ffffff;">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow">&bull; CLEAR DUBAI PRICING &bull;</span>
      <h2>Tyre prices in Dubai</h2>
      <p class="lead">Transparent pricing with free fitting, wheel balancing, and valves included.</p>
    </div>
    {build_guarantees_strip()}
    {build_location_common_price_table("Dubai")}
  </div>
</section>

<!-- POPULAR TYRES FOR DUBAI DRIVERS & WHAT DUBAI DRIVING DOES -->
<section class="tv-section-block" style="background:#F8FAFC;">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow">&mdash; LOCAL DRIVING REALITIES &mdash;</span>
      <h2>What driving in Dubai does to your tyres</h2>
      <p class="lead" style="max-width:820px; margin:0 auto 28px auto;">High-mileage Sheikh Zayed Road commuting, 50-degree summer tarmac, weekend runs to Al Qudra, and kerbing in older communities.</p>
    </div>

    <div class="card" style="background:#ffffff; border:1px solid #E2E8F0; border-radius:18px; padding:32px; max-width:880px; margin:0 auto;">
      <p style="font-size:1.02rem; line-height:1.75; color:#334155; margin:0 0 16px 0;">
        Dubai drivers subject tyres to extreme thermal cycles: high-speed 120&ndash;140 km/h cruising on Sheikh Zayed Road generates massive internal friction, while ambient temperatures exceeding 45&deg;C heat the tarmac past 55&deg;C. In older commercial districts like Deira, Karama, and narrow residential streets in Jumeirah, tight parallel parking causes repeated kerb scuffing.
      </p>
      <p style="font-size:0.98rem; line-height:1.7; color:#475569; margin:0;">
        <strong>Kerb damage to sidewalls is the quiet killer in Dubai:</strong> A pinched sidewall cord might show only a tiny outward bulge, but at 120 km/h on the highway to Abu Dhabi, that compromised area can rupture. Check your sidewalls monthly for bulges or tears.
      </p>
    </div>

    <div style="margin-top:36px;">
      <h3 style="text-align:center; font-size:1.3rem; font-weight:800; color:#0F172A; margin-bottom:18px;">Popular tyres for Dubai drivers</h3>
      <p style="text-align:center; color:#64748B; max-width:760px; margin:0 auto 24px auto;">Vehicles featured daily in our Dubai fitting network: <strong>Toyota Land Cruiser, Nissan Patrol, Toyota Corolla, Camry, Honda Civic, Ford Explorer, and Tesla Model 3 and Model Y.</strong></p>
    </div>

    {build_internal_links_card('Need help choosing? Explore all <a href="/tyre-brands" style="color:#2563FF; font-weight:700; text-decoration:underline;">tyre brands</a>, verify your fitment with <a href="/tyre-sizes" style="color:#2563FF; font-weight:700; text-decoration:underline;">find your tyre size</a>, book our certified <a href="/mobile-tyre-fitting" style="color:#2563FF; font-weight:700; text-decoration:underline;">mobile tyre fitting</a> van, or explore specialized <a href="/ev-tyres" style="color:#2563FF; font-weight:700; text-decoration:underline;">EV tyres</a>.')}
  </div>
</section>

{build_how_it_works_section("Dubai")}

<!-- DUBAI FAQS -->
{build_faq_section("Dubai tyre FAQs", faqs, eyebrow="DUBAI TYRE QUESTIONS")}

<!-- BOTTOM CTA -->
{build_bottom_cta(
    heading="Need Tyres Fitted Today in Dubai?",
    lead="Send your tyre size on WhatsApp. We provide exact quotes across 60+ brands with free fitting at a partner garage or your doorstep.",
    wa_msg="Hi TyresVision, I'd like a tyre price in Dubai.",
    wa_btn_text="WhatsApp Dubai Team"
)}
"""


# ==============================================================================
# PAGE 8: Tyre Shop Abu Dhabi (/tyre-shop-abu-dhabi)
# ==============================================================================
def build_page_abu_dhabi():
    hero = build_hero_section(
        title="Tyre Shop in Abu Dhabi — Tyres Fitted Near You",
        eyebrow="ABU DHABI FITTING NETWORK & DOORSTEP VANS",
        lead="Looking for a tyre shop in Abu Dhabi? 60+ brands delivered and fitted free at a centre near you, from Musaffah to Khalifa City. WhatsApp your size.",
        wa_text="WhatsApp for Abu Dhabi Quote",
        wa_msg="Hi TyresVision, I'd like a tyre price in Abu Dhabi.",
        breadcrumb_label="Tyre Shop Abu Dhabi",
        default_emirate="Abu Dhabi"
    )

    faqs = [
        {
            "q": "Where can I get tyres fitted in Abu Dhabi?",
            "a": "Our partner fitting workshops are located throughout Musaffah Industrial Area (M9, M14, M37), downtown Abu Dhabi Island (Al Khalidiyah, Corniche), and we provide mobile van fitting across Khalifa City, Yas Island, and Al Reem Island."
        },
        {
            "q": "Do you offer mobile tyre fitting in Abu Dhabi suburbs?",
            "a": "Yes! Our mobile tyre service vans cover Khalifa City A & B, Al Raha Beach, Yas Island, Saadiyat Island, Mohamed Bin Zayed City (MBZ), and Al Reef."
        },
        {
            "q": "What makes driving in Abu Dhabi tough on tyres?",
            "a": "Abu Dhabi drivers rack up exceptionally high annual highway mileage on long straight stretches (E11 towards Dubai, E22 towards Al Ain, and E11 towards Tarif/Liwa). High sustained speed in 50°C heat means thermal rating and proper load index are vital."
        },
        {
            "q": "Can you service government or commercial fleet vehicles in Abu Dhabi?",
            "a": "Yes, we supply heavy-duty, ESMA-certified tyres for commercial fleets, pickups, and SUVs across ICAD and Musaffah industrial areas."
        },
        {
            "q": "Is fitting and balancing included at Abu Dhabi centres?",
            "a": "Yes, all prices quoted include professional mounting, computerized balancing, new standard valves, and disposal of your old tyres."
        }
    ]

    return f"""{hero}

<!-- FITTING CENTRES ACROSS ABU DHABI -->
<section class="tv-section-block" style="background:#ffffff;">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow">&mdash; EMIRATE COVERAGE &mdash;</span>
      <h2>Tyre fitting centres across Abu Dhabi</h2>
      <p class="lead">Partner garages and mobile service routes across Abu Dhabi Island and the Capital District.</p>
    </div>

    <div class="grid g3" style="margin-top:28px;">
      <div class="card" style="border:1px solid #E2E8F0; border-radius:14px; padding:24px;">
        <h3 style="font-size:1.15rem; font-weight:800; color:#0F172A; margin:0 0 10px 0;">Abu Dhabi Island</h3>
        <p style="font-size:0.9rem; line-height:1.65; color:#475569; margin:0;">Corniche, Al Khalidiyah, Al Bateen, Al Mushrif, and central city fitting centres.</p>
      </div>
      <div class="card" style="border:1px solid #E2E8F0; border-radius:14px; padding:24px;">
        <h3 style="font-size:1.15rem; font-weight:800; color:#0F172A; margin:0 0 10px 0;">Al Reem &amp; Al Maryah</h3>
        <p style="font-size:0.9rem; line-height:1.65; color:#475569; margin:0;">Rapid mobile van dispatch and close garage locations for residential towers and financial hubs.</p>
      </div>
      <div class="card" style="border:1px solid #E2E8F0; border-radius:14px; padding:24px;">
        <h3 style="font-size:1.15rem; font-weight:800; color:#0F172A; margin:0 0 10px 0;">Khalifa City &amp; Al Raha</h3>
        <p style="font-size:0.9rem; line-height:1.65; color:#475569; margin:0;">Convenient villa doorstep fitting and nearby workshop services across Khalifa City, Al Raha, and Al Reef.</p>
      </div>
      <div class="card" style="border:1px solid #E2E8F0; border-radius:14px; padding:24px;">
        <h3 style="font-size:1.15rem; font-weight:800; color:#0F172A; margin:0 0 10px 0;">MBZ City &amp; Shakhbout</h3>
        <p style="font-size:0.9rem; line-height:1.65; color:#475569; margin:0;">Serving Mohamed Bin Zayed City, Shakhbout City, and Zayed City with doorstep mobile vans.</p>
      </div>
      <div class="card" style="border:1px solid #E2E8F0; border-radius:14px; padding:24px;">
        <h3 style="font-size:1.15rem; font-weight:800; color:#0F172A; margin:0 0 10px 0;">Musaffah &amp; ICAD</h3>
        <p style="font-size:0.9rem; line-height:1.65; color:#475569; margin:0;">Heavy-duty 4x4, commercial, and passenger car workshops located throughout Musaffah Industrial Zones.</p>
      </div>
      <div class="card" style="border:1px solid #E2E8F0; border-radius:14px; padding:24px;">
        <h3 style="font-size:1.15rem; font-weight:800; color:#0F172A; margin:0 0 10px 0;">Yas &amp; Saadiyat</h3>
        <p style="font-size:0.9rem; line-height:1.65; color:#475569; margin:0;">Doorstep mobile van service for villas and residential communities across Yas Island and Saadiyat.</p>
      </div>
    </div>
  </div>
</section>

<!-- FREE DELIVERY & OR WE COME TO YOU -->
<section class="tv-section-block" style="background:#F8FAFC;">
  <div class="wrap">
    <div class="grid g2">
      <div class="card" style="background:#ffffff; border:1px solid #E2E8F0; border-radius:18px; padding:32px;">
        <span class="eyebrow" style="color:#2563FF; font-weight:800; font-size:0.8rem;">WORKSHOP INSTALLATION</span>
        <h2 style="font-size:1.5rem; font-weight:800; color:#0F172A; margin:8px 0 12px 0;">Tyres delivered free to your nearest centre</h2>
        <p style="font-size:0.98rem; line-height:1.7; color:#475569; margin:0 0 16px 0;">We dispatch fresh tyres directly to our partner garage nearest to your home or office in Abu Dhabi. Your appointment is confirmed on WhatsApp, so you drive in and drive out without waiting in long industrial queues.</p>
      </div>

      <div class="card" style="background:#ffffff; border:1px solid #E2E8F0; border-radius:18px; padding:32px;">
        <span class="eyebrow" style="color:#2563FF; font-weight:800; font-size:0.8rem;">DOORSTEP CONVENIENCE</span>
        <h2 style="font-size:1.5rem; font-weight:800; color:#0F172A; margin:8px 0 12px 0;">Or we come to you</h2>
        <p style="font-size:0.98rem; line-height:1.7; color:#475569; margin:0 0 16px 0;">Avoid the drive down to Musaffah. Our <a href="/mobile-tyre-fitting" style="color:#2563FF; font-weight:700; text-decoration:underline;">mobile tyre fitting</a> vans bring the workshop directly to your villa in Khalifa City, Yas Island, or corporate parking bay in downtown Abu Dhabi.</p>
      </div>
    </div>
  </div>
</section>

<!-- TYRE PRICES IN ABU DHABI -->
<section class="price-section tv-section-block" style="background:#ffffff;">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow">&bull; CLEAR ABU DHABI PRICING &bull;</span>
      <h2>Tyre prices in Abu Dhabi</h2>
      <p class="lead">Transparent pricing with free fitting, wheel balancing, and valves included.</p>
    </div>
    {build_guarantees_strip()}
    {build_location_common_price_table("Abu Dhabi")}
  </div>
</section>

<!-- LOCAL DRIVING REALITIES ABU DHABI -->
<section class="tv-section-block" style="background:#F8FAFC;">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow">&mdash; LOCAL ANGLE &mdash;</span>
      <h2>What driving in Abu Dhabi does to your tyres</h2>
      <p class="lead" style="max-width:820px; margin:0 auto 28px auto;">The daily commute in from Khalifa City and MBZ, long highway stretches to Al Ain and Dubai, weekend trips to Liwa, and heavy industrial traffic around Musaffah.</p>
    </div>

    <div class="card" style="background:#ffffff; border:1px solid #E2E8F0; border-radius:18px; padding:32px; max-width:880px; margin:0 auto;">
      <p style="font-size:1.02rem; line-height:1.75; color:#334155; margin:0 0 16px 0;">
        Abu Dhabi highway mileage is significantly higher than Dubai's. Commuters frequently cover 60 to 100 km each day on high-speed expressways where temperatures remain above 45&deg;C for five months of the year. Under these conditions, heat resistance and load rating matter far more than aggressive tread design.
      </p>
      <p style="font-size:0.98rem; line-height:1.7; color:#475569; margin:0;">
        For heavy SUVs heading south towards Liwa dunes or west along the coastal highway, fitting a tyre with verified Temperature Grade A and proper load index (116 or 121) is essential to eliminate high-speed sidewall delamination.
      </p>
    </div>

    <div style="margin-top:36px;">
      <h3 style="text-align:center; font-size:1.3rem; font-weight:800; color:#0F172A; margin-bottom:18px;">Popular tyres for Abu Dhabi drivers</h3>
      <p style="text-align:center; color:#64748B; max-width:760px; margin:0 auto 24px auto;">Vehicles featured across the Capital: <strong>Nissan Patrol, Toyota Land Cruiser, Prado, government and corporate fleet vehicles, and pickups.</strong></p>
    </div>

    {build_internal_links_card('Explore our rugged <a href="/off-road-4x4-tyres" style="color:#2563FF; font-weight:700; text-decoration:underline;">4x4 and SUV tyres</a>, compare 60+ <a href="/tyre-brands" style="color:#2563FF; font-weight:700; text-decoration:underline;">tyre brands</a>, verify your exact size with <a href="/tyre-sizes" style="color:#2563FF; font-weight:700; text-decoration:underline;">find your tyre size</a>, or book our certified <a href="/mobile-tyre-fitting" style="color:#2563FF; font-weight:700; text-decoration:underline;">mobile tyre fitting</a> van.')}
  </div>
</section>

{build_how_it_works_section("Abu Dhabi")}

<!-- ABU DHABI FAQS -->
{build_faq_section("Abu Dhabi tyre FAQs", faqs, eyebrow="ABU DHABI TYRE QUESTIONS")}

<!-- BOTTOM CTA -->
{build_bottom_cta(
    heading="Need Tyres Fitted in Abu Dhabi?",
    lead="Send your tyre size on WhatsApp. We provide exact quotes across 60+ brands with free fitting at a partner garage or your doorstep.",
    wa_msg="Hi TyresVision, I'd like a tyre price in Abu Dhabi.",
    wa_btn_text="WhatsApp Abu Dhabi Team"
)}
"""


# ==============================================================================
# PAGE 9: Tyre Shop Sharjah (/tyre-shop-sharjah)
# ==============================================================================
def build_page_sharjah():
    hero = build_hero_section(
        title="Tyre Shop in Sharjah — Tyres Delivered and Fitted",
        eyebrow="SHARJAH HUBS & SAME-DAY FITTING",
        lead="Tyre shop serving Sharjah. 60+ brands delivered free to a fitting centre near you in Al Nahda, Al Majaz or Muwaileh. WhatsApp your tyre size.",
        wa_text="WhatsApp for Sharjah Quote",
        wa_msg="Hi TyresVision, I'd like a tyre price in Sharjah.",
        breadcrumb_label="Tyre Shop Sharjah",
        default_emirate="Sharjah"
    )

    faqs = [
        {
            "q": "Where are your partner fitting centres in Sharjah?",
            "a": "We have partner workshops across Industrial Areas 1 through 18, Al Nahda (near the Dubai border), Al Majaz, Al Khan, and Muwaileh Commercial."
        },
        {
            "q": "Why do Sharjah commuters need to change tyres more frequently?",
            "a": "Daily commuters between Sharjah and Dubai face 40 to 60 km of heavy stop-start traffic on Al Ittihad Road and Sheikh Mohammed Bin Zayed Road. Constant braking and crawling on sun-baked tarmac generates elevated surface heat, causing accelerated shoulder and tread wear."
        },
        {
            "q": "Do you offer budget and mid-range tyres in Sharjah?",
            "a": "Yes! We specialize in cost-effective mid-range and value tier tyres (Hankook, Kumho, Nexen, Laufenn, Giti, Zeetex) that deliver high durability for daily commuters at competitive rates."
        },
        {
            "q": "Can you deliver tyres to my home in Sharjah?",
            "a": "Mobile fitting in Sharjah is available upon request for residential areas like Al Majaz, Al Taawun, and Muwaileh. Contact us on WhatsApp to confirm technician availability."
        },
        {
            "q": "Are all tyres sold in Sharjah covered by warranty?",
            "a": "Yes, all tyres supplied by TyresVision are 100% genuine GCC-specification units with full distributor warranties and verified fresh DOT production dates."
        }
    ]

    return f"""{hero}

<!-- FITTING CENTRES ACROSS SHARJAH -->
<section class="tv-section-block" style="background:#ffffff;">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow">&mdash; SHARJAH HUBS &mdash;</span>
      <h2>Tyre fitting centres across Sharjah</h2>
      <p class="lead">Certified partner garages strategically positioned across Sharjah's main residential and industrial districts.</p>
    </div>

    <div class="grid g4" style="margin-top:28px;">
      <div class="card" style="border:1px solid #E2E8F0; border-radius:14px; padding:20px;">
        <h3 style="font-size:1.1rem; font-weight:800; color:#0F172A; margin:0 0 8px 0;">Al Nahda &amp; Al Taawun</h3>
        <p style="font-size:0.86rem; color:#475569; margin:0;">Right on the border with Dubai, convenient for daily commuters.</p>
      </div>
      <div class="card" style="border:1px solid #E2E8F0; border-radius:14px; padding:20px;">
        <h3 style="font-size:1.1rem; font-weight:800; color:#0F172A; margin:0 0 8px 0;">Al Majaz &amp; Al Khan</h3>
        <p style="font-size:0.86rem; color:#475569; margin:0;">Accessible fitting options for corniche and waterfront residential communities.</p>
      </div>
      <div class="card" style="border:1px solid #E2E8F0; border-radius:14px; padding:20px;">
        <h3 style="font-size:1.1rem; font-weight:800; color:#0F172A; margin:0 0 8px 0;">Muwaileh &amp; University City</h3>
        <p style="font-size:0.86rem; color:#475569; margin:0;">Serving student and family communities near Muwaileh Commercial.</p>
      </div>
      <div class="card" style="border:1px solid #E2E8F0; border-radius:14px; padding:20px;">
        <h3 style="font-size:1.1rem; font-weight:800; color:#0F172A; margin:0 0 8px 0;">Industrial Areas 1–18</h3>
        <p style="font-size:0.86rem; color:#475569; margin:0;">Extensive automotive workshops equipped for passenger cars, SUVs, and vans.</p>
      </div>
    </div>
  </div>
</section>

<!-- FREE DELIVERY & OR WE COME TO YOU -->
<section class="tv-section-block" style="background:#F8FAFC;">
  <div class="wrap">
    <div class="grid g2">
      <div class="card" style="background:#ffffff; border:1px solid #E2E8F0; border-radius:18px; padding:32px;">
        <span class="eyebrow" style="color:#2563FF; font-weight:800; font-size:0.8rem;">FREE CENTRE DELIVERY</span>
        <h2 style="font-size:1.5rem; font-weight:800; color:#0F172A; margin:8px 0 12px 0;">Tyres delivered free to your nearest centre</h2>
        <p style="font-size:0.98rem; line-height:1.7; color:#475569; margin:0 0 16px 0;">No delivery fees when fitting at any of our vetted partner garages in Sharjah. Your tyres are dispatched directly from temperature-controlled warehouses to the workshop before you arrive.</p>
      </div>

      <div class="card" style="background:#ffffff; border:1px solid #E2E8F0; border-radius:18px; padding:32px;">
        <span class="eyebrow" style="color:#2563FF; font-weight:800; font-size:0.8rem;">DOORSTEP SERVICE</span>
        <h2 style="font-size:1.5rem; font-weight:800; color:#0F172A; margin:8px 0 12px 0;">Or we come to you</h2>
        <p style="font-size:0.98rem; line-height:1.7; color:#475569; margin:0 0 16px 0;">Need mobile service? Our <a href="/mobile-tyre-fitting" style="color:#2563FF; font-weight:700; text-decoration:underline;">mobile tyre fitting</a> vans can fit and balance your new tyres at home or office on request across selected Sharjah areas.</p>
      </div>
    </div>
  </div>
</section>

<!-- TYRE PRICES IN SHARJAH -->
<section class="price-section tv-section-block" style="background:#ffffff;">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow">&bull; VALUE &amp; MID-RANGE PRICING &bull;</span>
      <h2>Tyre prices in Sharjah</h2>
      <p class="lead">Competitive pricing with free fitting, laser balancing, and valves included.</p>
    </div>
    {build_guarantees_strip()}
    {build_location_common_price_table("Sharjah")}
  </div>
</section>

<!-- LOCAL ANGLE: SHARJAH-DUBAI COMMUTE -->
<section class="tv-section-block" style="background:#F8FAFC;">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow">&mdash; LOCAL DRIVING REALITIES &mdash;</span>
      <h2>What driving in Sharjah does to your tyres</h2>
      <p class="lead" style="max-width:820px; margin:0 auto 28px auto;">The Sharjah–Dubai commute: 40–60 km a day in stop-start traffic and summer heat is harder on tyres than simple mileage suggests.</p>
    </div>

    <div class="card" style="background:#ffffff; border:1px solid #E2E8F0; border-radius:18px; padding:32px; max-width:880px; margin:0 auto;">
      <p style="font-size:1.02rem; line-height:1.75; color:#334155; margin:0 0 16px 0;">
        If you live in Sharjah and work in Dubai, you cover 40 to 60 km daily in heavy stop-start traffic under intense summer sunshine. Stop-start driving places repeated shear stress on tyre shoulders during braking and acceleration, while tarmac radiating 55&deg;C heat prevents tyre rubber from cooling down.
      </p>
      <p style="font-size:0.98rem; line-height:1.7; color:#475569; margin:0;">
        Because Sharjah commuters replace tyres more frequently, our lineup leads with high-value mid-range brands (Hankook, Kumho, Yokohama, Nexen) that balance thermal endurance with wallet-friendly prices.
      </p>
    </div>

    <div style="margin-top:36px;">
      <h3 style="text-align:center; font-size:1.3rem; font-weight:800; color:#0F172A; margin-bottom:18px;">Popular tyres for Sharjah drivers</h3>
      <p style="text-align:center; color:#64748B; max-width:760px; margin:0 auto 24px auto;">Vehicles featured daily in Sharjah: <strong>Toyota Corolla, Nissan Sunny, Hyundai Elantra, Honda Civic, older SUVs, family cars, and taxis.</strong></p>
    </div>

    {build_internal_links_card('Need to check prices? Explore our <a href="/tyre-brands" style="color:#2563FF; font-weight:700; text-decoration:underline;">budget and mid-range tyre brands</a>, find your exact dimensions with <a href="/tyre-sizes" style="color:#2563FF; font-weight:700; text-decoration:underline;">find your tyre size</a>, or book our <a href="/mobile-tyre-fitting" style="color:#2563FF; font-weight:700; text-decoration:underline;">mobile tyre fitting</a> service.')}
  </div>
</section>

{build_how_it_works_section("Sharjah")}

<!-- SHARJAH FAQS -->
{build_faq_section("Sharjah tyre FAQs", faqs, eyebrow="SHARJAH TYRE QUESTIONS")}

<!-- BOTTOM CTA -->
{build_bottom_cta(
    heading="Need Tyres Fitted in Sharjah Today?",
    lead="Message your size on WhatsApp. We confirm compatible options and book free installation at a Sharjah centre near you.",
    wa_msg="Hi TyresVision, I'd like a tyre price in Sharjah.",
    wa_btn_text="WhatsApp Sharjah Team"
)}
"""


# ==============================================================================
# PAGE 10: Tyre Shop Ajman (/tyre-shop-ajman)
# ==============================================================================
def build_page_ajman():
    hero = build_hero_section(
        title="Tyre Shop in Ajman — Tyres Delivered and Fitted",
        eyebrow="FAST LOCAL DELIVERY & VERIFIED DATES",
        lead="Tyre shop serving Ajman. 60+ brands delivered free to a fitting centre near you in Al Nuaimiya, Al Jurf or Ajman city. WhatsApp your tyre size.",
        wa_text="WhatsApp for Ajman Quote",
        wa_msg="Hi TyresVision, I'd like a tyre price in Ajman.",
        breadcrumb_label="Tyre Shop Ajman",
        default_emirate="Ajman"
    )

    faqs = [
        {
            "q": "Why is the DOT production date so critical for Ajman drivers?",
            "a": "Many Ajman car owners cover modest annual mileage (e.g. 8,000 to 12,000 km/year). A tyre will hit its 5-year replacement age long before its tread wears out. At TyresVision, we guarantee fresh DOT production dates so your tyres remain legal and safe for their full 5-year lifespan."
        },
        {
            "q": "Where are your partner fitting centres located in Ajman?",
            "a": "We have certified partner fitting garages across Al Nuaimiya, Al Jurf, Al Rashidiya, and Ajman Industrial Area."
        },
        {
            "q": "How quickly can tyres be delivered to an Ajman workshop?",
            "a": "Because Ajman is compact and close to central regional warehouses, tyres are frequently delivered within 2 to 4 hours for same-day fitting."
        },
        {
            "q": "Can you provide mobile tyre fitting in Ajman?",
            "a": "Yes, our mobile tyre service vans can travel to Ajman for residential doorstep fitting upon booking confirmation on WhatsApp."
        },
        {
            "q": "Do you stock tyres for older SUVs and pickups in Ajman?",
            "a": "Yes, we maintain deep stock for popular models including older Pajero, Prado, Toyota Hilux, Land Cruiser pickups, and Nissan Sunny."
        }
    ]

    return f"""{hero}

<!-- FITTING CENTRES ACROSS AJMAN -->
<section class="tv-section-block" style="background:#ffffff;">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow">&mdash; AJMAN LOCATIONS &mdash;</span>
      <h2>Tyre fitting centres across Ajman</h2>
      <p class="lead">Fast delivery and professional fitting across all central Ajman districts.</p>
    </div>

    <div class="grid g4" style="margin-top:28px;">
      <div class="card" style="border:1px solid #E2E8F0; border-radius:14px; padding:20px;">
        <h3 style="font-size:1.1rem; font-weight:800; color:#0F172A; margin:0 0 8px 0;">Al Nuaimiya</h3>
        <p style="font-size:0.86rem; color:#475569; margin:0;">Fast access right near Kuwait Street and the Sharjah border.</p>
      </div>
      <div class="card" style="border:1px solid #E2E8F0; border-radius:14px; padding:20px;">
        <h3 style="font-size:1.1rem; font-weight:800; color:#0F172A; margin:0 0 8px 0;">Al Jurf &amp; Al Rawda</h3>
        <p style="font-size:0.86rem; color:#475569; margin:0;">Convenient workshops serving university and residential villa zones.</p>
      </div>
      <div class="card" style="border:1px solid #E2E8F0; border-radius:14px; padding:20px;">
        <h3 style="font-size:1.1rem; font-weight:800; color:#0F172A; margin:0 0 8px 0;">Al Rashidiya &amp; City Centre</h3>
        <p style="font-size:0.86rem; color:#475569; margin:0;">Central locations close to Ajman Corniche and downtown apartments.</p>
      </div>
      <div class="card" style="border:1px solid #E2E8F0; border-radius:14px; padding:20px;">
        <h3 style="font-size:1.1rem; font-weight:800; color:#0F172A; margin:0 0 8px 0;">Ajman Industrial Area</h3>
        <p style="font-size:0.86rem; color:#475569; margin:0;">Specialized equipment for commercial vans, pickups, and heavy 4x4s.</p>
      </div>
    </div>
  </div>
</section>

<!-- FREE DELIVERY & OR WE COME TO YOU -->
<section class="tv-section-block" style="background:#F8FAFC;">
  <div class="wrap">
    <div class="grid g2">
      <div class="card" style="background:#ffffff; border:1px solid #E2E8F0; border-radius:18px; padding:32px;">
        <span class="eyebrow" style="color:#2563FF; font-weight:800; font-size:0.8rem;">RAPID LOCAL DISPATCH</span>
        <h2 style="font-size:1.5rem; font-weight:800; color:#0F172A; margin:8px 0 12px 0;">Tyres delivered free to your nearest centre</h2>
        <p style="font-size:0.98rem; line-height:1.7; color:#475569; margin:0 0 16px 0;">Ajman is compact, so delivery is exceptionally fast &mdash; most of the emirate is within a short run of our partner depots, and sets of four are frequently delivered same-day with free fitting and balancing.</p>
      </div>

      <div class="card" style="background:#ffffff; border:1px solid #E2E8F0; border-radius:18px; padding:32px;">
        <span class="eyebrow" style="color:#2563FF; font-weight:800; font-size:0.8rem;">DOORSTEP CONVENIENCE</span>
        <h2 style="font-size:1.5rem; font-weight:800; color:#0F172A; margin:8px 0 12px 0;">Or we come to you</h2>
        <p style="font-size:0.98rem; line-height:1.7; color:#475569; margin:0 0 16px 0;">Prefer fitting at home? Our <a href="/mobile-tyre-fitting" style="color:#2563FF; font-weight:700; text-decoration:underline;">mobile tyre fitting</a> vans bring precision balancing and mounting equipment straight to your villa or apartment parking in Ajman.</p>
      </div>
    </div>
  </div>
</section>

<!-- TYRE PRICES IN AJMAN -->
<section class="price-section tv-section-block" style="background:#ffffff;">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow">&bull; HONEST AJMAN PRICING &bull;</span>
      <h2>Tyre prices in Ajman</h2>
      <p class="lead">Affordable pricing tiers with free fitting and computerized balancing.</p>
    </div>
    {build_guarantees_strip()}
    {build_location_common_price_table("Ajman")}
  </div>
</section>

<!-- LOCAL ANGLE: TYRE AGE & DOT DATE CODES -->
<section class="tv-section-block" style="background:#F8FAFC;">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow">&mdash; LOCAL ANGLE: DOT DATE CODE &mdash;</span>
      <h2>What driving in Ajman does to your tyres</h2>
      <p class="lead" style="max-width:820px; margin:0 auto 28px auto;">In Ajman, tyre age matters far more than tread depth: a car doing 8,000 km a year can hit the 5-year replacement limit with plenty of tread remaining.</p>
    </div>

    <div class="card" style="background:#ffffff; border:1px solid #E2E8F0; border-radius:18px; padding:32px; max-width:880px; margin:0 auto;">
      <p style="font-size:1.02rem; line-height:1.75; color:#334155; margin:0 0 16px 0;">
        Many Ajman drivers keep their vehicles for extended ownership cycles and drive shorter daily distances. However, in the UAE's fierce summer climate, rubber compound oxidizes and hardens over time. Even if your tread looks deep, an aged tyre loses elasticity and becomes prone to sudden delamination.
      </p>
      <p style="font-size:0.98rem; line-height:1.7; color:#475569; margin:0;">
        <strong>Always verify the 4-digit DOT date code:</strong> At TyresVision, we guarantee every tyre delivered in Ajman is factory-fresh, so you get the full 5 years of safe, legal driving before age-related replacement.
      </p>
    </div>

    <div style="margin-top:36px;">
      <h3 style="text-align:center; font-size:1.3rem; font-weight:800; color:#0F172A; margin-bottom:18px;">Popular tyres for Ajman drivers</h3>
      <p style="text-align:center; color:#64748B; max-width:760px; margin:0 auto 24px auto;">Vehicles featured across Ajman: <strong>Toyota Corolla, Nissan Sunny, Hyundai Accent, older Pajero and Prado, and pickups.</strong></p>
    </div>

    {build_internal_links_card('Book convenient <a href="/mobile-tyre-fitting" style="color:#2563FF; font-weight:700; text-decoration:underline;">mobile tyre fitting</a> in Ajman, compare our roster of <a href="/tyre-brands" style="color:#2563FF; font-weight:700; text-decoration:underline;">tyre brands</a>, or <a href="/tyre-sizes" style="color:#2563FF; font-weight:700; text-decoration:underline;">find your tyre size</a>.')}
  </div>
</section>

{build_how_it_works_section("Ajman")}

<!-- AJMAN FAQS -->
{build_faq_section("Ajman tyre FAQs", faqs, eyebrow="AJMAN TYRE QUESTIONS")}

<!-- BOTTOM CTA -->
{build_bottom_cta(
    heading="Need Tyres Delivered & Fitted in Ajman?",
    lead="Send your tyre size on WhatsApp. We provide exact quotes across 60+ brands with free fitting at a local Ajman garage or your home.",
    wa_msg="Hi TyresVision, I'd like a tyre price in Ajman.",
    wa_btn_text="WhatsApp Ajman Team"
)}
"""


# ==============================================================================
# PAGE 11: Tyre Shop Ras Al Khaimah (/tyre-shop-ras-al-khaimah)
# ==============================================================================
def build_page_rak():
    hero = build_hero_section(
        title="Tyre Shop in Ras Al Khaimah",
        eyebrow="MOUNTAIN & QUARRY DURABILITY",
        lead="Tyre shop serving Ras Al Khaimah. 60+ brands delivered free to a fitting centre near you, from Al Nakheel to Al Hamra. WhatsApp your tyre size.",
        wa_text="WhatsApp for RAK Quote",
        wa_msg="Hi TyresVision, I'd like a tyre price in Ras Al Khaimah.",
        breadcrumb_label="Tyre Shop RAK",
        default_emirate="Ras Al Khaimah"
    )

    faqs = [
        {
            "q": "Why does mountain driving on Jebel Jais demand higher load ratings?",
            "a": "Jebel Jais climbs to over 1,900 metres. Long, steep descents place continuous lateral and braking load on tyre sidewalls, generating substantial friction heat. Fitting robust tyres with reinforced plies prevents sidewall flex and heat degradation."
        },
        {
            "q": "How do quarry and heavy truck traffic in RAK impact tyres?",
            "a": "RAK's quarry and industrial roads carry heavy gravel trucks, increasing loose aggregate and sharp rock debris. Pickups and 4x4s require puncture-resistant carcasses and cut-chip resistant tread compounds."
        },
        {
            "q": "Where are your partner fitting centres in Ras Al Khaimah?",
            "a": "We have certified partner fitting workshops across Al Nakheel, Al Dhait, Al Hamra, and the RAK Industrial Area."
        },
        {
            "q": "Can you supply heavy-duty pickup tyres in RAK?",
            "a": "Yes, we maintain dedicated stock for Toyota Hilux, Land Cruiser 70-series pickups, Nissan Patrol, and light commercial vehicles."
        },
        {
            "q": "Is fitting and balancing included at RAK partner centres?",
            "a": "Yes, all quotes include professional mounting, dynamic balancing, new valves, and environmental disposal of old tyres."
        }
    ]

    return f"""{hero}

<!-- FITTING CENTRES ACROSS RAK -->
<section class="tv-section-block" style="background:#ffffff;">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow">&mdash; RAK WORKSHOPS &mdash;</span>
      <h2>Tyre fitting centres across Ras Al Khaimah</h2>
      <p class="lead">Partner garages across RAK city, coastal resorts, and industrial hubs.</p>
    </div>

    <div class="grid g4" style="margin-top:28px;">
      <div class="card" style="border:1px solid #E2E8F0; border-radius:14px; padding:20px;">
        <h3 style="font-size:1.1rem; font-weight:800; color:#0F172A; margin:0 0 8px 0;">Al Nakheel &amp; Khuzam</h3>
        <p style="font-size:0.86rem; color:#475569; margin:0;">Central city workshops close to commercial districts and government offices.</p>
      </div>
      <div class="card" style="border:1px solid #E2E8F0; border-radius:14px; padding:20px;">
        <h3 style="font-size:1.1rem; font-weight:800; color:#0F172A; margin:0 0 8px 0;">Al Dhait &amp; Digdaga</h3>
        <p style="font-size:0.86rem; color:#475569; margin:0;">Serving residential suburbs, farms, and utility vehicle owners.</p>
      </div>
      <div class="card" style="border:1px solid #E2E8F0; border-radius:14px; padding:20px;">
        <h3 style="font-size:1.1rem; font-weight:800; color:#0F172A; margin:0 0 8px 0;">Al Hamra &amp; Mina Al Arab</h3>
        <p style="font-size:0.86rem; color:#475569; margin:0;">Fast fitting service for coastal resort communities and private residents.</p>
      </div>
      <div class="card" style="border:1px solid #E2E8F0; border-radius:14px; padding:20px;">
        <h3 style="font-size:1.1rem; font-weight:800; color:#0F172A; margin:0 0 8px 0;">RAK Industrial &amp; Quarry</h3>
        <p style="font-size:0.86rem; color:#475569; margin:0;">Heavy-duty equipment for 4x4s, commercial haulers, and commercial fleets.</p>
      </div>
    </div>
  </div>
</section>

<!-- FREE DELIVERY & OR WE COME TO YOU -->
<section class="tv-section-block" style="background:#F8FAFC;">
  <div class="wrap">
    <div class="grid g2">
      <div class="card" style="background:#ffffff; border:1px solid #E2E8F0; border-radius:18px; padding:32px;">
        <span class="eyebrow" style="color:#2563FF; font-weight:800; font-size:0.8rem;">WORKSHOP INSTALLATION</span>
        <h2 style="font-size:1.5rem; font-weight:800; color:#0F172A; margin:8px 0 12px 0;">Tyres delivered free to your nearest centre</h2>
        <p style="font-size:0.98rem; line-height:1.7; color:#475569; margin:0 0 16px 0;">We deliver your tyres directly to our certified fitting workshop in Ras Al Khaimah free of charge. Your fitting slot is confirmed on WhatsApp for quick, hassle-free installation.</p>
      </div>

      <div class="card" style="background:#ffffff; border:1px solid #E2E8F0; border-radius:18px; padding:32px;">
        <span class="eyebrow" style="color:#2563FF; font-weight:800; font-size:0.8rem;">DOORSTEP CONVENIENCE</span>
        <h2 style="font-size:1.5rem; font-weight:800; color:#0F172A; margin:8px 0 12px 0;">Or we come to you</h2>
        <p style="font-size:0.98rem; line-height:1.7; color:#475569; margin:0 0 16px 0;">Need on-site installation at your villa in Al Hamra or Mina Al Arab? Book our mobile service van via our <a href="/mobile-tyre-fitting" style="color:#2563FF; font-weight:700; text-decoration:underline;">mobile tyre fitting</a> service.</p>
      </div>
    </div>
  </div>
</section>

<!-- TYRE PRICES IN RAK -->
<section class="price-section tv-section-block" style="background:#ffffff;">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow">&bull; TRANSPARENT RAK PRICING &bull;</span>
      <h2>Tyre prices in Ras Al Khaimah</h2>
      <p class="lead">Competitive pricing with free fitting and computerized balancing.</p>
    </div>
    {build_guarantees_strip()}
    {build_location_common_price_table("Ras Al Khaimah")}
  </div>
</section>

<!-- LOCAL ANGLE: MOUNTAIN & QUARRY REALITIES -->
<section class="tv-section-block" style="background:#F8FAFC;">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow">&mdash; LOCAL ANGLE: MOUNTAINS &amp; QUARRIES &mdash;</span>
      <h2>What driving in Ras Al Khaimah does to your tyres</h2>
      <p class="lead" style="max-width:820px; margin:0 auto 28px auto;">RAK is the mountain and quarry emirate: Jebel Jais descents and quarry roads demand extra sidewall strength and high load ratings.</p>
    </div>

    <div class="card" style="background:#ffffff; border:1px solid #E2E8F0; border-radius:18px; padding:32px; max-width:880px; margin:0 auto;">
      <p style="font-size:1.02rem; line-height:1.75; color:#334155; margin:0 0 16px 0;">
        The Jebel Jais mountain road climbs to over 1,900 metres. Long descents and sustained mountain climbing load tyres differently from flat highway driving &mdash; repeated braking and steep hairpins build intense heat in tyre sidewalls on the descent.
      </p>
      <p style="font-size:0.98rem; line-height:1.7; color:#475569; margin:0;">
        Furthermore, quarry and cement truck traffic on RAK roads creates loose gravel and sharp stone hazards that cut through delicate passenger tyre plies. <strong>Load rating and sidewall strength are paramount in RAK</strong>, where pickups and heavy 4x4s make up a major share of all vehicles.
      </p>
    </div>

    <div style="margin-top:36px;">
      <h3 style="text-align:center; font-size:1.3rem; font-weight:800; color:#0F172A; margin-bottom:18px;">Popular tyres for Ras Al Khaimah drivers</h3>
      <p style="text-align:center; color:#64748B; max-width:760px; margin:0 auto 24px auto;">Vehicles featured across RAK: <strong>Toyota Hilux, Land Cruiser pickup, Nissan Patrol, Toyota Prado, older 4x4s, and light commercial haulers.</strong></p>
    </div>

    {build_internal_links_card('Equip your rig with rugged <a href="/off-road-4x4-tyres" style="color:#2563FF; font-weight:700; text-decoration:underline;">off-road and 4x4 tyres</a>, schedule convenient <a href="/mobile-tyre-fitting" style="color:#2563FF; font-weight:700; text-decoration:underline;">mobile tyre fitting</a>, or <a href="/tyre-sizes" style="color:#2563FF; font-weight:700; text-decoration:underline;">find your tyre size</a>.')}
  </div>
</section>

{build_how_it_works_section("Ras Al Khaimah")}

<!-- RAK FAQS -->
{build_faq_section("Ras Al Khaimah tyre FAQs", faqs, eyebrow="RAK TYRE QUESTIONS")}

<!-- BOTTOM CTA -->
{build_bottom_cta(
    heading="Need Rugged Tyres in Ras Al Khaimah?",
    lead="Send your tyre size on WhatsApp. We provide exact quotes across 60+ brands with free fitting at a partner centre near you.",
    wa_msg="Hi TyresVision, I'd like a tyre price in Ras Al Khaimah.",
    wa_btn_text="WhatsApp RAK Team"
)}
"""


# ==============================================================================
# PAGE 12: Tyre Shop Fujairah (/tyre-shop-fujairah)
# ==============================================================================
def build_page_fujairah():
    hero = build_hero_section(
        title="Tyre Shop in Fujairah and the East Coast",
        eyebrow="EAST COAST & MOUNTAIN PASS SERVICE",
        lead="Tyre shop serving Fujairah and the east coast. 60+ brands delivered free to a fitting centre near you. Send your tyre size on WhatsApp.",
        wa_text="WhatsApp for Fujairah Quote",
        wa_msg="Hi TyresVision, I'd like a tyre price in Fujairah.",
        breadcrumb_label="Tyre Shop Fujairah",
        default_emirate="Fujairah"
    )

    faqs = [
        {
            "q": "Why is uneven shoulder wear common on Fujairah cars?",
            "a": "The winding Masafi mountain passes and coastal road curves force vehicles through repeated lateral cornering and heavy downhill braking. This places disproportionate friction on the outer tyre shoulders, causing them to wear significantly faster than the centre tread."
        },
        {
            "q": "How does east coast humidity and sea salt affect tyres?",
            "a": "Fujairah and the east coast experience higher humidity than inland emirates. High moisture combined with port debris and heat accelerates rubber degradation and valve stem corrosion if wheels are not inspected regularly."
        },
        {
            "q": "Where can I get tyres fitted on the East Coast?",
            "a": "We have partner workshops in Fujairah City, Dibba Al Fujairah, Kalba, and Khor Fakkan."
        },
        {
            "q": "Do you deliver commercial and 4x4 tyres to Fujairah Port?",
            "a": "Yes, we provide heavy-duty 4x4, commercial, and fleet tyres delivered directly to Fujairah Port and Free Zone areas."
        },
        {
            "q": "Is 3D wheel balancing included with East Coast fitting?",
            "a": "Yes, all tyres include free mounting, computerized dynamic balancing, new valves, and disposal of your old tyres."
        }
    ]

    return f"""{hero}

<!-- FITTING CENTRES ACROSS FUJAIRAH -->
<section class="tv-section-block" style="background:#ffffff;">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow">&mdash; EAST COAST NETWORK &mdash;</span>
      <h2>Tyre fitting centres across Fujairah</h2>
      <p class="lead">Partner garages serving Fujairah City and key East Coast communities.</p>
    </div>

    <div class="grid g4" style="margin-top:28px;">
      <div class="card" style="border:1px solid #E2E8F0; border-radius:14px; padding:20px;">
        <h3 style="font-size:1.1rem; font-weight:800; color:#0F172A; margin:0 0 8px 0;">Fujairah City</h3>
        <p style="font-size:0.86rem; color:#475569; margin:0;">Central automotive hubs near Hamad Bin Abdulla Road.</p>
      </div>
      <div class="card" style="border:1px solid #E2E8F0; border-radius:14px; padding:20px;">
        <h3 style="font-size:1.1rem; font-weight:800; color:#0F172A; margin:0 0 8px 0;">Dibba Al Fujairah</h3>
        <p style="font-size:0.86rem; color:#475569; margin:0;">Northern east coast workshops serving private cars and commercial utility rigs.</p>
      </div>
      <div class="card" style="border:1px solid #E2E8F0; border-radius:14px; padding:20px;">
        <h3 style="font-size:1.1rem; font-weight:800; color:#0F172A; margin:0 0 8px 0;">Khor Fakkan &amp; Kalba</h3>
        <p style="font-size:0.86rem; color:#475569; margin:0;">Convenient partner workshops for east coast coastal commuters.</p>
      </div>
      <div class="card" style="border:1px solid #E2E8F0; border-radius:14px; padding:20px;">
        <h3 style="font-size:1.1rem; font-weight:800; color:#0F172A; margin:0 0 8px 0;">Masafi &amp; Port Areas</h3>
        <p style="font-size:0.86rem; color:#475569; margin:0;">Workshops equipped for mountain driving and port transport fleets.</p>
      </div>
    </div>
  </div>
</section>

<!-- FREE DELIVERY & OR WE COME TO YOU -->
<section class="tv-section-block" style="background:#F8FAFC;">
  <div class="wrap">
    <div class="grid g2">
      <div class="card" style="background:#ffffff; border:1px solid #E2E8F0; border-radius:18px; padding:32px;">
        <span class="eyebrow" style="color:#2563FF; font-weight:800; font-size:0.8rem;">WORKSHOP INSTALLATION</span>
        <h2 style="font-size:1.5rem; font-weight:800; color:#0F172A; margin:8px 0 12px 0;">Tyres delivered free to your nearest centre</h2>
        <p style="font-size:0.98rem; line-height:1.7; color:#475569; margin:0 0 16px 0;">We deliver your tyres directly to our vetted partner garage in Fujairah or Khor Fakkan. Once your shipment arrives, you simply drive in for prompt mounting and balancing.</p>
      </div>

      <div class="card" style="background:#ffffff; border:1px solid #E2E8F0; border-radius:18px; padding:32px;">
        <span class="eyebrow" style="color:#2563FF; font-weight:800; font-size:0.8rem;">DOORSTEP CONVENIENCE</span>
        <h2 style="font-size:1.5rem; font-weight:800; color:#0F172A; margin:8px 0 12px 0;">Or we come to you</h2>
        <p style="font-size:0.98rem; line-height:1.7; color:#475569; margin:0 0 16px 0;">Prefer doorstep fitting at home or office? Inquire about our <a href="/mobile-tyre-fitting" style="color:#2563FF; font-weight:700; text-decoration:underline;">mobile tyre fitting</a> coverage for your east coast location on WhatsApp.</p>
      </div>
    </div>
  </div>
</section>

<!-- TYRE PRICES IN FUJAIRAH -->
<section class="price-section tv-section-block" style="background:#ffffff;">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow">&bull; EAST COAST PRICING &bull;</span>
      <h2>Tyre prices in Fujairah</h2>
      <p class="lead">Transparent pricing with free fitting, wheel balancing, and valves included.</p>
    </div>
    {build_guarantees_strip()}
    {build_location_common_price_table("Fujairah")}
  </div>
</section>

<!-- LOCAL ANGLE: MOUNTAIN DESCENTS & UNEVEN SHOULDER WEAR -->
<section class="tv-section-block" style="background:#F8FAFC;">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow">&mdash; LOCAL ANGLE: SHOULDER WEAR &mdash;</span>
      <h2>What driving in Fujairah does to your tyres</h2>
      <p class="lead" style="max-width:820px; margin:0 auto 28px auto;">Fujairah is the only emirate where drivers do real mountain descents weekly: the Masafi passes heat tyres and wear outer shoulders faster than tread centres.</p>
    </div>

    <div class="card" style="background:#ffffff; border:1px solid #E2E8F0; border-radius:18px; padding:32px; max-width:880px; margin:0 auto;">
      <p style="font-size:1.02rem; line-height:1.75; color:#334155; margin:0 0 16px 0;">
        Navigating the mountain passes down to the East Coast entails repeated heavy braking and sharp cornering. This dynamic transfer scrub wears outer tyre shoulders much faster than the centre tread grooves. <strong>Uneven shoulder wear is the defining tyre issue in Fujairah.</strong>
      </p>
      <p style="font-size:0.98rem; line-height:1.7; color:#475569; margin:0;">
        In addition, the East Coast is noticeably more humid than inland UAE, while heavy port container trucks along the coastal corridor deposit more metal and gravel debris. Selecting tyres with reinforced shoulder blocks and scheduling wheel alignment every 10,000 km is critical.
      </p>
    </div>

    <div style="margin-top:36px;">
      <h3 style="text-align:center; font-size:1.3rem; font-weight:800; color:#0F172A; margin-bottom:18px;">Popular tyres for Fujairah drivers</h3>
      <p style="text-align:center; color:#64748B; max-width:760px; margin:0 auto 24px auto;">Vehicles featured across the East Coast: <strong>4x4s, pickups, light commercial vans, and family SUVs.</strong></p>
    </div>

    {build_internal_links_card('Explore durable <a href="/off-road-4x4-tyres" style="color:#2563FF; font-weight:700; text-decoration:underline;">off-road and 4x4 tyres</a>, arrange <a href="/mobile-tyre-fitting" style="color:#2563FF; font-weight:700; text-decoration:underline;">mobile tyre fitting</a>, or compare leading <a href="/tyre-brands" style="color:#2563FF; font-weight:700; text-decoration:underline;">tyre brands</a>.')}
  </div>
</section>

{build_how_it_works_section("Fujairah")}

<!-- FUJAIRAH FAQS -->
{build_faq_section("Fujairah tyre FAQs", faqs, eyebrow="FUJAIRAH TYRE QUESTIONS")}

<!-- BOTTOM CTA -->
{build_bottom_cta(
    heading="Need Tyres Delivered in Fujairah or the East Coast?",
    lead="Send your tyre size on WhatsApp. We provide exact quotes across 60+ brands with free fitting at an East Coast partner garage.",
    wa_msg="Hi TyresVision, I'd like a tyre price in Fujairah.",
    wa_btn_text="WhatsApp Fujairah Team"
)}
"""


# ==============================================================================
# PAGE 13: Tyre Shop Umm Al Quwain (/tyre-shop-umm-al-quwain)
# ==============================================================================
def build_page_uaq():
    hero = build_hero_section(
        title="Tyre Shop in Umm Al Quwain",
        eyebrow="COASTAL COMMUTING & RURAL ROADS",
        lead="Tyre shop serving Umm Al Quwain. 60+ brands delivered free to a fitting centre near you, with mobile fitting on request. WhatsApp your size.",
        wa_text="WhatsApp for UAQ Quote",
        wa_msg="Hi TyresVision, I'd like a tyre price in Umm Al Quwain.",
        breadcrumb_label="Tyre Shop UAQ",
        default_emirate="Umm Al Quwain"
    )

    faqs = [
        {
            "q": "Why is monthly tyre pressure monitoring vital in Umm Al Quwain?",
            "a": "UAQ driving combines short local coastal trips with high-speed 120 km/h highway runs down the E11 or E311. If a tyre is under-inflated on short trips, it flexes severely once hitting highway speeds, building hazardous internal heat."
        },
        {
            "q": "How does sand and gravel in Falaj Al Mualla affect tyre tread?",
            "a": "Inland farming areas around Falaj Al Mualla have sand-drifted tarmac and gravel access roads. Sharp sand and grit can lodge between tread sipes, accelerating bead wear and slow pressure leakage."
        },
        {
            "q": "Where are your partner fitting centres in Umm Al Quwain?",
            "a": "Our partner workshops are situated across UAQ City, Al Salamah, and the UAQ Industrial Area."
        },
        {
            "q": "Can I get mobile tyre fitting in Umm Al Quwain?",
            "a": "Yes! Our mobile tyre service vans can be scheduled for villa doorstep fitting in UAQ upon WhatsApp booking."
        },
        {
            "q": "Are all tyres sold in UAQ compliant with UAE regulations?",
            "a": "Yes, all tyres supplied by TyresVision are 100% genuine GCC-spec units with fresh DOT production dates and full manufacturer warranties."
        }
    ]

    return f"""{hero}

<!-- FITTING CENTRES ACROSS UAQ -->
<section class="tv-section-block" style="background:#ffffff;">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow">&mdash; UAQ LOCATIONS &mdash;</span>
      <h2>Tyre fitting centres across Umm Al Quwain</h2>
      <p class="lead">Convenient partner garages serving coastal communities and inland districts.</p>
    </div>

    <div class="grid g4" style="margin-top:28px;">
      <div class="card" style="border:1px solid #E2E8F0; border-radius:14px; padding:20px;">
        <h3 style="font-size:1.1rem; font-weight:800; color:#0F172A; margin:0 0 8px 0;">UAQ City &amp; Old Town</h3>
        <p style="font-size:0.86rem; color:#475569; margin:0;">Central city workshops serving residential and municipal areas.</p>
      </div>
      <div class="card" style="border:1px solid #E2E8F0; border-radius:14px; padding:20px;">
        <h3 style="font-size:1.1rem; font-weight:800; color:#0F172A; margin:0 0 8px 0;">Al Salamah &amp; Al Raas</h3>
        <p style="font-size:0.86rem; color:#475569; margin:0;">Accessible fitting points for primary suburban residential communities.</p>
      </div>
      <div class="card" style="border:1px solid #E2E8F0; border-radius:14px; padding:20px;">
        <h3 style="font-size:1.1rem; font-weight:800; color:#0F172A; margin:0 0 8px 0;">UAQ Industrial Area</h3>
        <p style="font-size:0.86rem; color:#475569; margin:0;">Full-scale workshop facilities for commercial trucks, pickups, and 4x4s.</p>
      </div>
      <div class="card" style="border:1px solid #E2E8F0; border-radius:14px; padding:20px;">
        <h3 style="font-size:1.1rem; font-weight:800; color:#0F172A; margin:0 0 8px 0;">Falaj Al Mualla &amp; Rafaah</h3>
        <p style="font-size:0.86rem; color:#475569; margin:0;">Serving inland agricultural and rural community utility vehicles.</p>
      </div>
    </div>
  </div>
</section>

<!-- FREE DELIVERY & OR WE COME TO YOU -->
<section class="tv-section-block" style="background:#F8FAFC;">
  <div class="wrap">
    <div class="grid g2">
      <div class="card" style="background:#ffffff; border:1px solid #E2E8F0; border-radius:18px; padding:32px;">
        <span class="eyebrow" style="color:#2563FF; font-weight:800; font-size:0.8rem;">WORKSHOP INSTALLATION</span>
        <h2 style="font-size:1.5rem; font-weight:800; color:#0F172A; margin:8px 0 12px 0;">Tyres delivered free to your nearest centre</h2>
        <p style="font-size:0.98rem; line-height:1.7; color:#475569; margin:0 0 16px 0;">Order through WhatsApp and we deliver your tyres straight to our certified partner centre in Umm Al Quwain with zero shipping fee. Fitting, laser balancing, and valves are included.</p>
      </div>

      <div class="card" style="background:#ffffff; border:1px solid #E2E8F0; border-radius:18px; padding:32px;">
        <span class="eyebrow" style="color:#2563FF; font-weight:800; font-size:0.8rem;">DOORSTEP SERVICE</span>
        <h2 style="font-size:1.5rem; font-weight:800; color:#0F172A; margin:8px 0 12px 0;">Or we come to you</h2>
        <p style="font-size:0.98rem; line-height:1.7; color:#475569; margin:0 0 16px 0;">Mobile tyre fitting in UAQ is available upon request! Our <a href="/mobile-tyre-fitting" style="color:#2563FF; font-weight:700; text-decoration:underline;">mobile tyre fitting</a> van visits your villa or farm location equipped with on-site balancing tools.</p>
      </div>
    </div>
  </div>
</section>

<!-- TYRE PRICES IN UAQ -->
<section class="price-section tv-section-block" style="background:#ffffff;">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow">&bull; UAQ VALUE PRICING &bull;</span>
      <h2>Tyre prices in Umm Al Quwain</h2>
      <p class="lead">Clear upfront pricing tiers with free workshop balancing or doorstep mobile fitting.</p>
    </div>
    {build_guarantees_strip()}
    {build_location_common_price_table("Umm Al Quwain")}
  </div>
</section>

<!-- LOCAL ANGLE: SHORT TRIPS VS HIGHWAY HEAT & MONTHLY PRESSURE -->
<section class="tv-section-block" style="background:#F8FAFC;">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow">&mdash; LOCAL ANGLE: PRESSURE &amp; TERRAIN &mdash;</span>
      <h2>What driving in Umm Al Quwain does to your tyres</h2>
      <p class="lead" style="max-width:820px; margin:0 auto 28px auto;">UAQ driving is short trips plus long runs down the E11: tyres that never fully warm up locally then face sustained highway heat.</p>
    </div>

    <div class="card" style="background:#ffffff; border:1px solid #E2E8F0; border-radius:18px; padding:32px; max-width:880px; margin:0 auto;">
      <p style="font-size:1.02rem; line-height:1.75; color:#334155; margin:0 0 16px 0;">
        UAQ is quiet and coastal. Much driving consists of short local errands where tyres never reach optimal operating temperature, interspersed with high-speed runs down the E11 or E311 to Sharjah or Dubai. That combination &mdash; cold short trips followed by sudden sustained 120 km/h highway heat &mdash; is remarkably taxing on rubber compounds.
      </p>
      <p style="font-size:0.98rem; line-height:1.7; color:#475569; margin:0;">
        Inland around Falaj Al Mualla, farm and sand-blown roads lead to sand and grit packing into tyre sipes, causing gradual bead pressure loss. <strong>Check your tyre cold pressure monthly</strong> to protect your tyres and preserve maximum fuel economy.
      </p>
    </div>

    <div style="margin-top:36px;">
      <h3 style="text-align:center; font-size:1.3rem; font-weight:800; color:#0F172A; margin-bottom:18px;">Popular tyres for Umm Al Quwain drivers</h3>
      <p style="text-align:center; color:#64748B; max-width:760px; margin:0 auto 24px auto;">Vehicles featured across UAQ: <strong>pickups, older sedans, farm and utility vehicles, and family SUVs.</strong></p>
    </div>

    {build_internal_links_card('Book convenient doorstep <a href="/mobile-tyre-fitting" style="color:#2563FF; font-weight:700; text-decoration:underline;">mobile tyre fitting</a>, <a href="/tyre-sizes" style="color:#2563FF; font-weight:700; text-decoration:underline;">find your tyre size</a>, or browse all <a href="/tyre-brands" style="color:#2563FF; font-weight:700; text-decoration:underline;">tyre brands</a>.')}
  </div>
</section>

{build_how_it_works_section("Umm Al Quwain")}

<!-- UAQ FAQS -->
{build_faq_section("Umm Al Quwain tyre FAQs", faqs, eyebrow="UAQ TYRE QUESTIONS")}

<!-- BOTTOM CTA -->
{build_bottom_cta(
    heading="Need Tyres Delivered in Umm Al Quwain?",
    lead="Send your tyre size on WhatsApp. We provide exact quotes across 60+ brands with free fitting at a partner centre near you.",
    wa_msg="Hi TyresVision, I'd like a tyre price in Umm Al Quwain.",
    wa_btn_text="WhatsApp UAQ Team"
)}
"""
