"""
scripts/page_builders_sizes.py
Generates Page 5: Tyre Sizes and Prices in the UAE (/tyre-sizes)
Exact match to specifications in 'TyresVision-13-Page-Build-Plan 1.docx'.
"""

from page_shared_components import (
    build_hero_section,
    build_guarantees_strip,
    build_faq_section,
    build_bottom_cta,
    build_internal_links_card
)

def build_page_sizes():
    hero = build_hero_section(
        title="Tyre Sizes and Prices in the UAE",
        eyebrow="FIND YOUR EXACT FITMENT",
        lead="Find your tyre size and see UAE prices. Popular sizes from 195/65 R15 to 305/40 R22, what each number means, and which cars use them.",
        wa_text="WhatsApp Your Tyre Size",
        wa_msg="Hi TyresVision, I'd like to check prices for my tyre size.",
        breadcrumb_label="Tyre Sizes",
        default_emirate="Dubai"
    )

    faqs = [
        {
            "q": "What do the letters and numbers on my tyre sidewall mean?",
            "a": "Take 235/55 R19 105W as an example: '235' is the tyre width in millimetres; '55' is the aspect ratio (sidewall height is 55% of 235 mm); 'R' stands for Radial construction; '19' is the rim diameter in inches; '105' is the load index (maximum 925 kg); and 'W' is the speed rating (up to 270 km/h)."
        },
        {
            "q": "Can I mix different tyre sizes between front and rear axles?",
            "a": "Only if your car originally came with a 'staggered' factory fitment from the manufacturer (common on BMW M-Sport, Mercedes-AMG, Porsche, and Tesla Model Y Performance). Otherwise, all four tyres must be identical in dimension to prevent drivetrain binding and ESP faults."
        },
        {
            "q": "What is the four-digit number at the end of the DOT code?",
            "a": "The last four digits represent the week and year of manufacture. For example, '2425' indicates the tyre was produced in the 24th week of 2025. In the UAE, tyres must not be sold if older than 2 years from production."
        },
        {
            "q": "Where can I find my vehicle's recommended tyre pressure?",
            "a": "Recommended cold tyre pressures are printed on a placard sticker located on the driver's door jamb, inside the fuel filler flap, or in the owner's handbook."
        },
        {
            "q": "Can I fit a slightly wider tyre on my existing wheels?",
            "a": "Going slightly wider (for example, 225 mm instead of 215 mm) is sometimes possible if wheel rim width allows, but it alters speedometer calibration, increases rolling resistance, and may cause wheel-well rubbing at full steering lock. We recommend adhering to factory specifications."
        },
        {
            "q": "Why do two tyres of the same size have vastly different prices?",
            "a": "Price differences reflect tread compound technology, silica content, load index, speed capability, acoustic noise suppression foam, and brand warranty coverage. A premium tyre typically lasts 20,000 to 30,000 km longer than a budget alternative."
        }
    ]

    popular_sizes = [
        ("195/65 R15", "Toyota Corolla, Honda Civic, Nissan Sunny", "AED 160", "AED 240", "AED 340"),
        ("205/55 R16", "Hyundai Elantra, VW Golf, Mazda 3", "AED 185", "AED 280", "AED 390"),
        ("215/55 R17", "Toyota Camry, Honda Accord, Nissan Altima", "AED 210", "AED 310", "AED 460"),
        ("225/45 R18", "BMW 3 Series, Mercedes C-Class, Audi A4", "AED 260", "AED 390", "AED 580"),
        ("225/65 R17", "Toyota RAV4, Honda CR-V, Nissan X-Trail", "AED 240", "AED 340", "AED 490"),
        ("235/55 R19", "Kia Sorento, Hyundai Santa Fe, Lexus RX", "AED 290", "AED 420", "AED 620"),
        ("235/45 R18", "Tesla Model 3, Lexus ES350", "AED 295", "AED 410", "AED 610"),
        ("255/45 R19", "Tesla Model Y, Audi Q5", "AED 340", "AED 480", "AED 720"),
        ("265/65 R17", "Toyota Prado, Fortuner, Hilux, Pajero", "AED 290", "AED 420", "AED 610"),
        ("265/60 R18", "Toyota Prado, Land Cruiser, Pajero", "AED 310", "AED 460", "AED 670"),
        ("275/50 R20", "Mercedes G-Class, GLE, GLS", "AED 420", "AED 610", "AED 980"),
        ("275/60 R20", "Nissan Patrol, Chevy Tahoe, GMC Yukon", "AED 380", "AED 540", "AED 840"),
        ("285/60 R18", "Toyota Land Cruiser LC200 / LC300", "AED 380", "AED 520", "AED 790"),
        ("285/50 R20", "Nissan Patrol Y62, Land Cruiser", "AED 390", "AED 560", "AED 890"),
        ("275/40 R21", "BMW X5, Range Rover Sport", "AED 460", "AED 680", "AED 1,090"),
        ("285/40 R22", "Range Rover Vogue, Audi Q8, Defender", "AED 510", "AED 780", "AED 1,280"),
        ("305/40 R22", "Cadillac Escalade, Ram 1500 TRX", "AED 540", "AED 840", "AED 1,350")
    ]

    size_rows = ""
    for size, cars, val_p, mid_p, prem_p in popular_sizes:
        wa_text = f"Hi TyresVision, I'd like a price quote for size {size} ({cars})."
        import urllib.parse
        wa_enc = urllib.parse.quote(wa_text)
        size_rows += f"""
            <tr>
              <td style="font-weight:800; color:#0F172A; white-space:nowrap;">{size}</td>
              <td style="color:#475569; font-size:0.9rem;">{cars}</td>
              <td style="font-weight:700; color:#0F172A;">{val_p}</td>
              <td style="font-weight:700; color:#2563FF;">{mid_p}</td>
              <td style="font-weight:700; color:#0F172A;">{prem_p}</td>
              <td style="text-align:right;"><a class="get-quote-link" href="https://wa.me/971505069575?text={wa_enc}" target="_blank" rel="noopener"><span>Quote</span> &rarr;</a></td>
            </tr>
"""

    content = f"""{hero}

<!-- 2. HOW TO READ YOUR TYRE SIZE -->
<section class="tv-section-block" style="background:#ffffff;">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow">&mdash; SIDEWALL GUIDE &mdash;</span>
      <h2 class="center tv-section-title">How to read your tyre size</h2>
      <p class="center tv-section-subtitle" style="max-width:840px; margin:0 auto 36px auto; font-size:1.06rem; line-height:1.75; color:#475569;">
        Every tyre sidewall contains a sequence of numbers and letters that dictate its width, aspect ratio, construction, rim diameter, load carrying capacity, and maximum speed.
      </p>
    </div>

    <div style="background:#F8FAFC; border:2px solid #E2E8F0; border-radius:20px; padding:32px; max-width:920px; margin:0 auto;">
      <div style="text-align:center; margin-bottom:24px;">
        <span style="font-size:clamp(1.8rem, 4vw, 2.5rem); font-weight:900; color:#2563FF; letter-spacing:0.04em; font-family:monospace; background:#ffffff; padding:8px 24px; border-radius:12px; border:1px solid #CBD5E1; display:inline-block;">
          235 / 55 R19 105W
        </span>
      </div>

      <div class="grid g3" style="gap:16px;">
        <div style="background:#ffffff; padding:18px; border-radius:12px; border:1px solid #E2E8F0;">
          <div style="font-weight:800; color:#2563FF; font-size:1.2rem; margin-bottom:4px;">235</div>
          <div style="font-weight:700; color:#0F172A; font-size:0.95rem; margin-bottom:4px;">Section Width</div>
          <div style="font-size:0.85rem; color:#64748B;">Width of tyre in millimetres from sidewall to sidewall.</div>
        </div>

        <div style="background:#ffffff; padding:18px; border-radius:12px; border:1px solid #E2E8F0;">
          <div style="font-weight:800; color:#2563FF; font-size:1.2rem; margin-bottom:4px;">55</div>
          <div style="font-weight:700; color:#0F172A; font-size:0.95rem; margin-bottom:4px;">Aspect Ratio</div>
          <div style="font-size:0.85rem; color:#64748B;">Sidewall profile height as a percentage of the width (55% of 235 mm).</div>
        </div>

        <div style="background:#ffffff; padding:18px; border-radius:12px; border:1px solid #E2E8F0;">
          <div style="font-weight:800; color:#2563FF; font-size:1.2rem; margin-bottom:4px;">R19</div>
          <div style="font-weight:700; color:#0F172A; font-size:0.95rem; margin-bottom:4px;">Radial &amp; Rim Size</div>
          <div style="font-size:0.85rem; color:#64748B;">Radial construction designed for a 19-inch wheel rim diameter.</div>
        </div>

        <div style="background:#ffffff; padding:18px; border-radius:12px; border:1px solid #E2E8F0;">
          <div style="font-weight:800; color:#2563FF; font-size:1.2rem; margin-bottom:4px;">105</div>
          <div style="font-weight:700; color:#0F172A; font-size:0.95rem; margin-bottom:4px;">Load Index</div>
          <div style="font-size:0.85rem; color:#64748B;">Maximum safe load capacity: index 105 equals 925 kg per tyre.</div>
        </div>

        <div style="background:#ffffff; padding:18px; border-radius:12px; border:1px solid #E2E8F0;">
          <div style="font-weight:800; color:#2563FF; font-size:1.2rem; margin-bottom:4px;">W</div>
          <div style="font-weight:700; color:#0F172A; font-size:0.95rem; margin-bottom:4px;">Speed Rating</div>
          <div style="font-size:0.85rem; color:#64748B;">Maximum speed capability: rating 'W' is certified up to 270 km/h.</div>
        </div>

        <div style="background:#ffffff; padding:18px; border-radius:12px; border:1px solid #E2E8F0;">
          <div style="font-weight:800; color:#2563FF; font-size:1.2rem; margin-bottom:4px;">DOT 2425</div>
          <div style="font-weight:700; color:#0F172A; font-size:0.95rem; margin-bottom:4px;">Production Date</div>
          <div style="font-size:0.85rem; color:#64748B;">Manufactured in the 24th week of 2025. Always check fresh dates.</div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- 3. WHERE TO FIND YOUR SIZE -->
<section class="tv-section-block" style="background:#F8FAFC;">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow">&mdash; LOCATING YOUR FITMENT &mdash;</span>
      <h2>Where to find your size</h2>
      <p class="lead">Two quick places to check your correct vehicle tyre dimensions.</p>
    </div>

    <div class="grid g2" style="max-width:880px; margin:0 auto;">
      <div class="card" style="background:#ffffff; border:1px solid #E2E8F0; border-radius:16px; padding:28px;">
        <div style="font-size:1.2rem; font-weight:800; color:#0F172A; margin-bottom:8px;">1. On the Current Tyre Sidewall</div>
        <p style="font-size:0.95rem; line-height:1.65; color:#475569; margin:0 0 14px 0;">Look at the raised lettering on the outer rubber sidewall of your front and rear tyres. Ensure both front and rear match (unless your car has staggered tyres).</p>
        <span style="font-size:0.85rem; color:#2563FF; font-weight:700;">Tip: Take a quick photo and send it to our WhatsApp team.</span>
      </div>

      <div class="card" style="background:#ffffff; border:1px solid #E2E8F0; border-radius:16px; padding:28px;">
        <div style="font-size:1.2rem; font-weight:800; color:#0F172A; margin-bottom:8px;">2. Driver's Door Placard Sticker</div>
        <p style="font-size:0.95rem; line-height:1.65; color:#475569; margin:0 0 14px 0;">Open the driver's door and inspect the B-pillar jamb. A factory sticker lists approved tyre sizes, load indexes, and recommended PSI inflation values for unladen and fully laden driving.</p>
        <span style="font-size:0.85rem; color:#2563FF; font-weight:700;">Tip: The door placard is the definitive factory reference.</span>
      </div>
    </div>

    <div style="text-align:center; margin-top:28px;">
      <a class="tv-btn-wa-green" href="https://wa.me/971505069575?text=Hi%20TyresVision%2C%20here%20is%20a%20photo%20of%20my%20tyre%20sidewall.%20Please%20recommend%20options." target="_blank" rel="noopener" style="display:inline-flex;">
        <span>Send a Photo of Your Tyre on WhatsApp</span>
      </a>
    </div>
  </div>
</section>

<!-- 4. POPULAR TYRE SIZES IN THE UAE -->
<section class="price-section tv-section-block" style="background:#ffffff;">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow">&bull; POPULAR UAE SIZES &bull;</span>
      <h2>Popular tyre sizes in the UAE</h2>
      <p class="lead">From compact 15-inch commuter fitments to 22-inch luxury SUV sizes, with starting price points across value, mid-range and premium tiers.</p>
    </div>

    {build_guarantees_strip()}

    <div class="price-table-card" style="margin-top:28px;">
      <div class="price-table-scroll">
        <table class="price-table tv-4x4-table" aria-label="Popular Tyre Sizes and Prices in the UAE">
          <thead>
            <tr>
              <th scope="col">Tyre Size</th>
              <th scope="col">Common Vehicle Models</th>
              <th scope="col">Value Tier</th>
              <th scope="col">Mid-Range</th>
              <th scope="col">Premium Tier</th>
              <th scope="col" style="text-align:right;">Action</th>
            </tr>
          </thead>
          <tbody>
            {size_rows}
          </tbody>
        </table>
      </div>
    </div>
  </div>
</section>

<!-- 5. LOAD INDEX AND SPEED RATING -->
<section class="tv-section-block" style="background:#F8FAFC;">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow">&mdash; TECHNICAL SPECIFICATIONS &mdash;</span>
      <h2>Load index and speed rating</h2>
      <p class="lead">Why you must never install a tyre with ratings below your vehicle manufacturer's specification.</p>
    </div>

    <div class="grid g2" style="max-width:940px; margin:0 auto;">
      <div class="card" style="background:#ffffff; border:1px solid #E2E8F0; border-radius:16px; padding:26px;">
        <h3 style="font-size:1.15rem; font-weight:800; color:#0F172A; margin:0 0 12px 0;">Common Load Indexes (kg per tyre)</h3>
        <table style="width:100%; font-size:0.9rem; border-collapse:collapse;">
          <tr style="border-bottom:1px solid #E2E8F0;"><td style="padding:6px 0; font-weight:700;">88: 560 kg</td><td style="padding:6px 0; font-weight:700;">91: 615 kg</td><td style="padding:6px 0; font-weight:700;">94: 670 kg</td></tr>
          <tr style="border-bottom:1px solid #E2E8F0;"><td style="padding:6px 0; font-weight:700;">98: 750 kg</td><td style="padding:6px 0; font-weight:700;">102: 850 kg</td><td style="padding:6px 0; font-weight:700;">105: 925 kg</td></tr>
          <tr style="border-bottom:1px solid #E2E8F0;"><td style="padding:6px 0; font-weight:700;">111: 1,090 kg</td><td style="padding:6px 0; font-weight:700;">116: 1,250 kg</td><td style="padding:6px 0; font-weight:700;">121: 1,450 kg</td></tr>
        </table>
        <p style="font-size:0.85rem; color:#64748B; margin:12px 0 0 0;">Never drop below the load index specified on your door placard. Doing so causes sidewall failure under vehicle weight.</p>
      </div>

      <div class="card" style="background:#ffffff; border:1px solid #E2E8F0; border-radius:16px; padding:26px;">
        <h3 style="font-size:1.15rem; font-weight:800; color:#0F172A; margin:0 0 12px 0;">Speed Ratings (Max km/h)</h3>
        <table style="width:100%; font-size:0.9rem; border-collapse:collapse;">
          <tr style="border-bottom:1px solid #E2E8F0;"><td style="padding:6px 0; font-weight:700;">S: 180 km/h</td><td style="padding:6px 0; font-weight:700;">T: 190 km/h</td><td style="padding:6px 0; font-weight:700;">H: 210 km/h</td></tr>
          <tr style="border-bottom:1px solid #E2E8F0;"><td style="padding:6px 0; font-weight:700;">V: 240 km/h</td><td style="padding:6px 0; font-weight:700;">W: 270 km/h</td><td style="padding:6px 0; font-weight:700;">Y: 300 km/h</td></tr>
          <tr style="border-bottom:1px solid #E2E8F0;"><td style="padding:6px 0; font-weight:700;">(Y): 300+ km/h</td><td style="padding:6px 0; font-weight:700;">VR: 210+ km/h</td><td style="padding:6px 0; font-weight:700;">ZR: 240+ km/h</td></tr>
        </table>
        <p style="font-size:0.85rem; color:#64748B; margin:12px 0 0 0;">For UAE highway commuting at 120&ndash;140 km/h in summer heat, minimum ratings of V (240 km/h) or higher are strongly advised.</p>
      </div>
    </div>
  </div>
</section>

<!-- 6. CAN I FIT A DIFFERENT SIZE? -->
<section class="tv-section-block" style="background:#ffffff;">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow">&mdash; PRACTICAL ADVICE &mdash;</span>
      <h2>Can I fit a different size?</h2>
      <p class="lead" style="max-width:820px; margin:0 auto 28px auto;">Small changes affect speedometer accuracy, insurance and sometimes the warranty. We fit the manufacturer size unless there is a good reason.</p>
    </div>

    <div class="card" style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:18px; padding:32px; max-width:880px; margin:0 auto;">
      <p style="font-size:1.02rem; line-height:1.75; color:#334155; margin:0 0 16px 0;">Altering your overall tyre diameter by more than 2% causes speedometer inaccuracies, changes gearbox shift points on automatic transmissions, and can trigger false alerts from ABS and electronic stability control systems.</p>
      <p style="font-size:0.98rem; line-height:1.7; color:#475569; margin:0;">In the UAE, non-standard tyre sizes that protrude beyond vehicle fender arches or rub on suspension components during full articulation will fail official RTA (Dubai) or ADNOC (Abu Dhabi) annual vehicle fitness inspections. We always verify manufacturer compatibility before fitting.</p>
    </div>

    {build_internal_links_card('Look up fitment for your vehicle under <a href="/tyres-by-car" style="color:#2563FF; font-weight:700; text-decoration:underline;">tyres for your car model</a>, compare leading <a href="/tyre-brands" style="color:#2563FF; font-weight:700; text-decoration:underline;">tyre brands</a>, view rugged <a href="/off-road-4x4-tyres" style="color:#2563FF; font-weight:700; text-decoration:underline;">4x4 and SUV tyres</a>, or schedule convenient doorstep <a href="/mobile-tyre-fitting" style="color:#2563FF; font-weight:700; text-decoration:underline;">mobile tyre fitting</a>.')}
  </div>
</section>

<!-- 7. TYRE SIZE FAQS -->
{build_faq_section("Tyre size FAQs", faqs, eyebrow="TYRE SIZE FAQS")}

<!-- 8. BOTTOM CTA -->
{build_bottom_cta(
    heading="Need Help Finding the Right Tyre Size?",
    lead="Send a photo of your tyre sidewall or car registration card on WhatsApp. We confirm compatible sizes and verified prices.",
    wa_msg="Hi TyresVision, please help me identify and price the correct tyre size for my vehicle.",
    wa_btn_text="WhatsApp Your Tyre Size"
)}
"""
    return content
