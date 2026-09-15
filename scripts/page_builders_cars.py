"""
scripts/page_builders_cars.py
Generates Page 6: Find Tyres for Your Car Model (/tyres-by-car)
Exact match to specifications in 'TyresVision-13-Page-Build-Plan 1.docx'.
"""

import urllib.parse
from page_shared_components import (
    build_hero_section,
    build_guarantees_strip,
    build_faq_section,
    build_bottom_cta,
    build_internal_links_card
)

def build_page_cars():
    hero = build_hero_section(
        title="Find Tyres for Your Car Model",
        eyebrow="SEARCH BY VEHICLE",
        lead="Find the right tyre size for your car. Land Cruiser, Patrol, Corolla, Camry, Civic, Tesla and more, with UAE prices and free fitting near you.",
        wa_text="WhatsApp for Car Model Quote",
        wa_msg="Hi TyresVision, I need tyre recommendations for my car model.",
        breadcrumb_label="Tyres by Car",
        default_emirate="Dubai"
    )

    faqs = [
        {
            "q": "My car model is not listed in the table, can you still help?",
            "a": "Yes! We stock and supply tyres for over 450 vehicle models across the UAE. Simply send us your car make, model, year, or a photo of your tyre sidewall on WhatsApp and our team will provide compatible options immediately."
        },
        {
            "q": "Do I have to use the exact tyre size the car originally came with?",
            "a": "We strongly recommend sticking to the manufacturer's specified dimensions printed on your driver's door jamb sticker. Changing tyre dimensions alters your speedometer reading, can void warranties, and may cause tyre rubbing during full steering turns."
        },
        {
            "q": "How do I know which trim level or tyre size I have?",
            "a": "The quickest and most reliable method is to read the numbers directly off your current tyre's sidewall (e.g. 215/55 R17) or check the factory certification plate on the driver's door B-pillar."
        },
        {
            "q": "Are tyres for luxury cars different from standard car tyres?",
            "a": "Luxury and performance cars (like BMW, Mercedes-Benz, Porsche, and Audi) frequently require vehicle-specific homologation tyres marked with OEM codes (e.g., MO for Mercedes, Star for BMW, AO for Audi). These have tailored internal belt structures for optimal chassis dynamics."
        },
        {
            "q": "Can TyresVision fit tyres for my car at my home?",
            "a": "Yes! Our certified mobile tyre fitting vans carry pneumatic mounting machines, dynamic balancers, and precision torque tools directly to your home, office, or apartment car park across Dubai and Abu Dhabi."
        },
        {
            "q": "Does my SUV require light truck (LT) or passenger (P) tyres?",
            "a": "Mid-size crossovers and highway SUVs (like the RAV4 or Explorer) use passenger (P/Metric) tyres for comfort, while heavy 4x4s and utility pickups (like Patrol, Land Cruiser, and Hilux) often benefit from reinforced LT or high load index (116/121) ratings."
        }
    ]

    popular_cars = [
        ("Toyota Land Cruiser", "285/60 R18, 275/60 R20", "Highway / All-Terrain", "From AED 380"),
        ("Nissan Patrol", "285/50 R20, 275/60 R20", "Highway / All-Terrain", "From AED 390"),
        ("Toyota Prado", "265/65 R17, 265/60 R18", "Highway / All-Terrain", "From AED 310"),
        ("Mitsubishi Pajero", "265/60 R18", "Highway-Terrain", "From AED 290"),
        ("Toyota Fortuner", "265/65 R17", "Highway / All-Terrain", "From AED 310"),
        ("Toyota Hilux", "265/65 R17, 265/60 R18", "All-Terrain (A/T)", "From AED 280"),
        ("Ford Explorer", "255/50 R20, 235/55 R19", "Highway-Terrain", "From AED 340"),
        ("Chevrolet Tahoe", "275/60 R20", "Highway-Terrain", "From AED 360"),
        ("Jeep Wrangler", "255/75 R17, 285/70 R17", "All-Terrain / Mud-Terrain", "From AED 420"),
        ("Mercedes G-Class", "275/50 R20", "Highway / All-Terrain", "From AED 580"),
        ("Toyota Corolla", "195/65 R15, 205/55 R16", "Comfort / Fuel Saver", "From AED 160"),
        ("Honda Civic", "215/55 R16, 215/50 R17", "Comfort / Balanced Touring", "From AED 185"),
        ("Nissan Sunny", "185/65 R15, 195/65 R15", "Comfort / Value Commuter", "From AED 150"),
        ("Hyundai Elantra", "205/55 R16, 225/45 R17", "Mid-Range Touring", "From AED 185"),
        ("Toyota Camry", "215/55 R17, 235/45 R18", "Quiet Highway Touring", "From AED 210"),
        ("Honda Accord", "225/50 R17, 235/40 R19", "Touring / Low Noise", "From AED 225"),
        ("Kia Cerato", "205/55 R16, 225/45 R17", "Comfort / Commuter", "From AED 180"),
        ("Volkswagen Jetta", "205/55 R16, 225/45 R17", "Touring / Wet Grip", "From AED 195"),
        ("Tesla Model 3", "235/45 R18, 235/40 R19", "EV-Rated / Acoustic Foam", "From AED 385"),
        ("Tesla Model Y", "255/45 R19, 255/40 R20", "High Load (HL/XL) / Low RR", "From AED 420"),
        ("BMW 3 Series", "225/45 R18, 255/40 R18", "Run-Flat / Ultra High Perf", "From AED 340"),
        ("Mercedes C-Class", "225/45 R18, 245/40 R18", "Run-Flat (MOE) / Comfort", "From AED 350"),
        ("Audi A4 / A6", "225/50 R17, 245/40 R18", "Comfort / High Speed Touring", "From AED 330"),
        ("Range Rover Sport", "275/45 R21, 285/40 R22", "High Load / Air Suspension", "From AED 560"),
        ("Porsche Cayenne", "275/45 R20, 285/40 R21", "N-Spec High-Performance", "From AED 580")
    ]

    car_rows = ""
    for car, size, ttype, _ in popular_cars:
        wa_text = f"Hi TyresVision, I need a tyre price quote for my {car}."
        wa_enc = urllib.parse.quote(wa_text)
        car_rows += f"""
            <tr>
              <td style="font-weight:800; color:#0F172A; white-space:nowrap;">{car}</td>
              <td style="color:#475569; font-size:0.9rem;">{size}</td>
              <td style="color:#2563FF; font-weight:600; font-size:0.9rem;">{ttype}</td>
              <td style="text-align:right;"><a class="get-quote-link" href="https://wa.me/971505069575?text={wa_enc}" target="_blank" rel="noopener"><span>Get Quote</span> &rarr;</a></td>
            </tr>
"""

    vehicle_chips = [
        "Toyota Land Cruiser", "Nissan Patrol", "Toyota Prado", "Toyota Camry",
        "Toyota Corolla", "Nissan Sunny", "Honda Civic", "Honda Accord",
        "Hyundai Elantra", "Kia Sportage", "Ford Explorer", "Chevrolet Tahoe",
        "Jeep Wrangler", "Tesla Model 3", "Tesla Model Y", "BMW 3 Series",
        "Mercedes C-Class", "Mercedes G-Class", "Range Rover Sport", "Audi Q7"
    ]

    chips_html = ""
    for v in vehicle_chips:
        wa_v_msg = f"Hi TyresVision, I need a tyre quote for {v}."
        wa_v_enc = urllib.parse.quote(wa_v_msg)
        chips_html += f"""
        <a class="svc chip-interactive" href="https://wa.me/971505069575?text={wa_v_enc}" target="_blank" rel="noopener">
          <span class="dot" aria-hidden="true"></span>
          <span class="chip-text">{v}</span>
          <svg class="chip-wa-arrow" width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.46 1.32 4.96L2 22l5.25-1.38a9.9 9.9 0 004.79 1.22h.01c5.46 0 9.91-4.45 9.91-9.91C21.96 6.45 17.5 2 12.04 2zm5.8 14.06c-.24.68-1.42 1.31-1.96 1.36-.54.05-1.04.24-3.52-.73-2.99-1.18-4.86-4.29-5.01-4.49-.15-.2-1.2-1.6-1.2-3.05 0-1.45.76-2.16 1.03-2.46.27-.29.59-.37.78-.37s.39 0 .56.01c.18.01.42-.07.66.5.24.59.83 2.03.9 2.18.07.15.12.32.02.51-.1.2-.15.32-.29.5s-.3.4-.43.53c-.15.15-.3.31-.13.6.17.29.76 1.25 1.62 2.02 1.11.99 2.05 1.3 2.34 1.45.29.15.46.12.63-.07.17-.2.73-.85.92-1.14.2-.29.39-.24.66-.15.27.1 1.71.81 2 .96.29.15.49.22.56.34.07.13.07.75-.17 1.43z"/></svg>
        </a>
"""

    content = f"""{hero}

<!-- 2. FIND YOUR CAR CHIPS GRID -->
<section class="tv-section-block" style="background:#ffffff;">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow">&mdash; SELECT YOUR VEHICLE &mdash;</span>
      <h2 class="center tv-section-title">Find your car</h2>
      <p class="center tv-section-subtitle" style="max-width:840px; margin:0 auto 36px auto; font-size:1.06rem; line-height:1.75; color:#475569;">
        Tap your vehicle model below to send a pre-filled WhatsApp enquiry directly to our technical team for confirmed sizes, verified stock, and instant pricing.
      </p>
    </div>

    <div class="svc-grid shop-by-grid" style="margin-top:24px;">
      {chips_html}
    </div>
  </div>
</section>

<!-- 3. TYRE SIZES BY CAR MODEL TABLE -->
<section class="price-section tv-section-block" style="background:#F8FAFC;">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow">&bull; POPULAR UAE VEHICLES &bull;</span>
      <h2>Tyre sizes by car model</h2>
      <p class="lead">Factory dimensions and optimal tyre categories across 25 of the most popular vehicles driven on UAE roads.</p>
    </div>

    {build_guarantees_strip()}

    <div class="price-table-card" style="margin-top:28px;">
      <div class="price-table-scroll">
        <table class="price-table tv-4x4-table" aria-label="Tyre Sizes by Car Model in the UAE">
          <thead>
            <tr>
              <th scope="col">Car Model</th>
              <th scope="col">Common Sizes</th>
              <th scope="col">Tyre Type Usually Best</th>
              <th scope="col" style="text-align:right;">Action</th>
            </tr>
          </thead>
          <tbody>
            {car_rows}
          </tbody>
        </table>
      </div>
    </div>
  </div>
</section>

<!-- 4. SEDANS AND HATCHBACKS -->
<section class="tv-section-block" style="background:#ffffff;">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow">&mdash; PASSENGER COMMUTERS &mdash;</span>
      <h2>Sedans and hatchbacks</h2>
      <p class="lead">Corolla, Civic, Sunny, Elantra, Camry, Accord, Cerato, Jetta.</p>
    </div>

    <div class="card" style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:18px; padding:32px; max-width:880px; margin:0 auto;">
      <p style="font-size:1.02rem; line-height:1.75; color:#334155; margin:0 0 16px 0;">
        For everyday sedans and hatchbacks, drivers should focus on ride comfort, low cabin noise, and fuel economy. The mid-range tyre tier (Hankook, Yokohama, Kumho, Dunlop) is usually the sweet spot &mdash; offering around 85% of premium European tyre durability and wet braking performance for roughly 60% of the price.
      </p>
      <p style="font-size:0.96rem; line-height:1.7; color:#64748B; margin:0;">
        If you commute between Sharjah and Dubai or cover high annual highway mileage, opting for a low-rolling-resistance silica compound pays dividends in lower fuel consumption and reduced tyre wear during summer tarmac conditions.
      </p>
    </div>
  </div>
</section>

<!-- 5. SUVS AND 4X4S (OVERLAP RULE ENFORCED: SHORT SECTION WITH LINK OUT) -->
<section class="tv-section-block" style="background:#F8FAFC;">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow">&mdash; SPORT UTILITY VEHICLES &mdash;</span>
      <h2>SUVs and 4x4s</h2>
    </div>

    <div class="card" style="background:#ffffff; border:1px solid #E2E8F0; border-radius:18px; padding:28px; max-width:840px; margin:0 auto; text-align:center;">
      <p style="font-size:1.05rem; line-height:1.75; color:#334155; margin:0 0 16px 0;">
        Large SUVs like the Land Cruiser, Patrol, Prado, and Tahoe demand reinforced load capacities and specialized tread compounds. If you drive primarily on city highways, choose Highway-Terrain (H/T) tyres for comfort and thermal protection; if you venture into the desert, select All-Terrain (A/T) tyres with sand deflation capability.
      </p>
      <p style="margin:0; font-weight:700;">
        For comprehensive desert driving tips and 4x4 model fitments, explore our dedicated guide to <a href="/off-road-4x4-tyres" style="color:#2563FF; text-decoration:underline;">off-road and 4x4 tyres</a>.
      </p>
    </div>
  </div>
</section>

<!-- 6. ELECTRIC AND HYBRID (SHORT SECTION WITH LINK OUT) -->
<section class="tv-section-block" style="background:#ffffff;">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow">&mdash; ELECTRIFIED MOBILITY &mdash;</span>
      <h2>Electric and hybrid</h2>
    </div>

    <div class="card" style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:18px; padding:28px; max-width:840px; margin:0 auto; text-align:center;">
      <p style="font-size:1.05rem; line-height:1.75; color:#334155; margin:0 0 16px 0;">
        Electric and hybrid vehicles like the Tesla Model 3, Model Y, BYD Seal, and Lexus Hybrids feature immediate electric torque and heavy battery packs. They require High Load (HL/XL) carcasses, low rolling resistance silica compounds, and acoustic foam damping to preserve range and quietness.
      </p>
      <p style="margin:0; font-weight:700;">
        For technical load requirements and model fitments, visit our complete guide to <a href="/ev-tyres" style="color:#2563FF; text-decoration:underline;">EV tyres</a>.
      </p>
    </div>
  </div>
</section>

<!-- 7. WHY THE SAME MODEL CAN TAKE TWO SIZES -->
<section class="tv-section-block" style="background:#F8FAFC;">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow">&mdash; FITMENT NUANCES &mdash;</span>
      <h2>Why the same model can take two sizes</h2>
      <p class="lead" style="max-width:820px; margin:0 auto 28px auto;">Trim levels and wheel sizes differ. Always check the sidewall, not just the model name.</p>
    </div>

    <div class="card" style="background:#ffffff; border:1px solid #E2E8F0; border-radius:18px; padding:32px; max-width:880px; margin:0 auto;">
      <p style="font-size:1.02rem; line-height:1.75; color:#334155; margin:0 0 16px 0;">A base-model Toyota Camry or Corolla typically rolls on 16-inch or 17-inch alloy wheels with taller sidewall profiles for maximum cushion over bumps. Meanwhile, the Sport, SE, or Limited trim of the exact same model year often features 18-inch or 19-inch low-profile wheels for sharper handling.</p>
      <p style="font-size:0.98rem; line-height:1.7; color:#475569; margin:0;">Similarly, a Nissan Patrol SE runs on 18-inch wheels, while a Patrol Platinum or Nismo runs on 20-inch or 22-inch rims. Never buy tyres based on the model name alone &mdash; check our guide on <a href="/tyre-sizes" style="color:#2563FF; font-weight:700; text-decoration:underline;">how to read your tyre size</a>, or send us a quick photo on WhatsApp.</p>
    </div>

    {build_internal_links_card('Need to explore specific brands? Compare 60+ manufacturers on our <a href="/tyre-brands" style="color:#2563FF; font-weight:700; text-decoration:underline;">tyre brands</a> hub, check our dedicated <a href="/off-road-4x4-tyres" style="color:#2563FF; font-weight:700; text-decoration:underline;">off-road and 4x4 tyres</a> guide, or review <a href="/ev-tyres" style="color:#2563FF; font-weight:700; text-decoration:underline;">EV tyres</a>.')}
  </div>
</section>

<!-- 8. CAR MODEL FAQS -->
{build_faq_section("Car model FAQs", faqs, eyebrow="CAR MODEL FITMENT FAQS")}

<!-- 9. BOTTOM CTA -->
{build_bottom_cta(
    heading="Find the Perfect Tyres for Your Car in Minutes",
    lead="Send your car model or tyre size on WhatsApp. We provide exact quotes across certified brands with free fitting.",
    wa_msg="Hi TyresVision, please help me find the best tyres for my car model.",
    wa_btn_text="WhatsApp Your Car Model"
)}
"""
    return content
