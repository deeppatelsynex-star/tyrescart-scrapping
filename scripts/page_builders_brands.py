"""
scripts/page_builders_brands.py
Generates Page 4: Tyre Brands We Supply Across the UAE (/tyre-brands)
Exact match to specifications in 'TyresVision-13-Page-Build-Plan 1.docx'.
"""

from page_shared_components import (
    build_hero_section,
    build_guarantees_strip,
    build_faq_section,
    build_bottom_cta,
    build_internal_links_card
)

def build_page_brands():
    hero = build_hero_section(
        title="Tyre Brands We Supply Across the UAE",
        eyebrow="60+ GLOBAL TYRE MANUFACTURERS",
        lead="Compare 60+ tyre brands available in the UAE. Premium, mid-range and budget explained, with honest advice on which suits UAE heat and your mileage.",
        wa_text="WhatsApp for Brand Quotes",
        wa_msg="Hi TyresVision, I'd like a price quote across different tyre brands.",
        breadcrumb_label="Tyre Brands",
        default_emirate="Dubai"
    )

    faqs = [
        {
            "q": "Which tyre brand lasts the longest in the UAE?",
            "a": "Michelin, Bridgestone and Continental consistently deliver the highest mileage in the UAE, typically achieving 50,000 to 70,000 km when correctly inflated and rotated every 10,000 km. Their advanced silica-carbon black compounds resist thermal degradation from 55°C summer asphalt."
        },
        {
            "q": "Are budget tyre brands legal and safe in the UAE?",
            "a": "Yes, provided they carry official ESMA (Emirates Authority for Standardization and Metrology) certification and have a fresh DOT production date under 150 days old. A budget tyre with the correct load and speed ratings is completely road-legal and safe for urban commuting."
        },
        {
            "q": "What is the warranty on new tyres purchased from TyresVision?",
            "a": "All tyres supplied by TyresVision carry the official UAE manufacturer/distributor warranty against manufacturing defects (typically 1 to 5 years depending on the brand and model)."
        },
        {
            "q": "How old can a new tyre be when sold in the UAE?",
            "a": "Under UAE consumer protection and ESMA rules, tyres sold by licensed retailers must not exceed 2 years from their DOT manufacture date at the time of sale, and must be replaced after a maximum of 5 years in service."
        },
        {
            "q": "Can I mix different tyre brands on my car?",
            "a": "You should never mix different brands or tread patterns across the same axle. While you can technically run one brand on the front axle and another on the rear, keeping all four tyres of the same brand, model, and wear level ensures balanced braking and stable electronic stability control operation."
        },
        {
            "q": "Which mid-range brand offers the best value for money?",
            "a": "Hankook, Yokohama, and Kumho represent the sweet spot for UAE drivers. They deliver approximately 80% to 85% of premium brand longevity and wet braking performance for about 60% of the price."
        }
    ]

    content = f"""{hero}

<!-- 2. THE THREE TIERS AND WHAT THE MONEY BUYS YOU -->
<section class="tv-section-block" style="background:#ffffff;">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow">&mdash; MARKET BREAKDOWN &mdash;</span>
      <h2 class="center tv-section-title">The three tiers, and what the money buys you</h2>
      <p class="center tv-section-subtitle" style="max-width:840px; margin:0 auto 36px auto; font-size:1.06rem; line-height:1.75; color:#475569;">
        Premium buys shorter braking distances and longer life. Mid-range gives around 80% of that for around 60% of the price. Budget makes sense for low-mileage city cars and not much else.
      </p>
    </div>

    <div class="grid g3" style="margin-top:24px;">
      <div class="card tv-feature-card">
        <div class="icon-well" aria-hidden="true" style="background:#EFF6FF; color:#2563FF;">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>
        </div>
        <h3 style="font-size:1.25rem; font-weight:800; color:#0F172A; margin:14px 0 10px 0;">Premium Tier</h3>
        <p style="font-size:0.92rem; line-height:1.65; color:#475569; margin:0 0 12px 0;"><strong>Michelin, Bridgestone, Continental, Pirelli, Goodyear, Dunlop.</strong></p>
        <p style="font-size:0.88rem; line-height:1.6; color:#64748B; margin:0;">Engineered with proprietary silica compounds and acoustic dampening. Maximum heat resistance, shortest stopping distances, and longevity exceeding 60,000 km.</p>
      </div>

      <div class="card tv-feature-card" style="border-color:#2563FF; box-shadow:0 10px 28px -6px rgba(37,99,255,0.12);">
        <div class="icon-well" aria-hidden="true" style="background:#2563FF; color:#ffffff;">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 14 14"/></svg>
        </div>
        <h3 style="font-size:1.25rem; font-weight:800; color:#0F172A; margin:14px 0 10px 0;">Mid-Range Tier (Sweet Spot)</h3>
        <p style="font-size:0.92rem; line-height:1.65; color:#475569; margin:0 0 12px 0;"><strong>Hankook, Yokohama, Toyo, Falken, Kumho, Nexen, BFGoodrich.</strong></p>
        <p style="font-size:0.88rem; line-height:1.6; color:#64748B; margin:0;">Delivers roughly 80% to 85% of premium performance at 60% of the cost. Ideal for daily commuters, highway family saloons, and practical SUVs.</p>
      </div>

      <div class="card tv-feature-card">
        <div class="icon-well" aria-hidden="true" style="background:#F1F5F9; color:#475569;">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>
        </div>
        <h3 style="font-size:1.25rem; font-weight:800; color:#0F172A; margin:14px 0 10px 0;">Value Tier</h3>
        <p style="font-size:0.92rem; line-height:1.65; color:#475569; margin:0 0 12px 0;"><strong>Laufenn, Giti, Sumitomo, Zeetex, Roadstone.</strong></p>
        <p style="font-size:0.88rem; line-height:1.6; color:#64748B; margin:0;">ESMA-certified and reliable for low-mileage city driving, secondary cars, and budget fleet transport where high-speed desert or highway runs are rare.</p>
      </div>
    </div>
  </div>
</section>

<!-- 3. PREMIUM BRANDS DETAIL -->
<section class="tv-section-block" style="background:#F8FAFC;">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow">&mdash; TIER 1 MANUFACTURERS &mdash;</span>
      <h2>Premium brands</h2>
      <p class="lead">Two or three sentences on what each brand is genuinely known for and which driver it suits.</p>
    </div>

    <div class="grid g3" style="margin-top:28px;">
      <div class="card" style="background:#ffffff; border:1px solid #E2E8F0; border-radius:14px; padding:24px;">
        <h3 style="font-size:1.2rem; font-weight:800; color:#0F172A; margin:0 0 10px 0;">Michelin</h3>
        <p style="font-size:0.92rem; line-height:1.65; color:#475569; margin:0;">Renowned for the Pilot Sport and Primacy lineups, Michelin delivers the longest usable tread life and lowest rolling resistance in the UAE. Best for luxury saloons, high-mileage highway drivers, and EVs requiring acoustic silence.</p>
      </div>

      <div class="card" style="background:#ffffff; border:1px solid #E2E8F0; border-radius:14px; padding:24px;">
        <h3 style="font-size:1.2rem; font-weight:800; color:#0F172A; margin:0 0 10px 0;">Bridgestone</h3>
        <p style="font-size:0.92rem; line-height:1.65; color:#475569; margin:0;">Famous for the Potenza and Dueler lines, Bridgestone features remarkably stiff sidewalls engineered for extreme durability under severe UAE heat. The go-to choice for heavy SUVs and drivers prioritizing structural blowout protection.</p>
      </div>

      <div class="card" style="background:#ffffff; border:1px solid #E2E8F0; border-radius:14px; padding:24px;">
        <h3 style="font-size:1.2rem; font-weight:800; color:#0F172A; margin:0 0 10px 0;">Continental</h3>
        <p style="font-size:0.92rem; line-height:1.65; color:#475569; margin:0;">Continental leads European OEM fitments with the SportContact and UltraContact series, delivering benchmark stopping distances on dry and wet tarmac. Best suited for German performance saloons and premium crossover SUVs.</p>
      </div>

      <div class="card" style="background:#ffffff; border:1px solid #E2E8F0; border-radius:14px; padding:24px;">
        <h3 style="font-size:1.2rem; font-weight:800; color:#0F172A; margin:0 0 10px 0;">Pirelli</h3>
        <p style="font-size:0.92rem; line-height:1.65; color:#475569; margin:0;">Pirelli's P Zero and Scorpion families dominate supercar and high-performance SUV fitments with unmatched lateral cornering grip and sharp steering response. Ideal for spirited drivers and sports performance vehicles.</p>
      </div>

      <div class="card" style="background:#ffffff; border:1px solid #E2E8F0; border-radius:14px; padding:24px;">
        <h3 style="font-size:1.2rem; font-weight:800; color:#0F172A; margin:0 0 10px 0;">Goodyear</h3>
        <p style="font-size:0.92rem; line-height:1.65; color:#475569; margin:0;">Goodyear's Eagle F1 and EfficientGrip series balance ride comfort with strong aquaplaning resistance and durable tread compounds. A dependable pick for executive saloons and American crossovers.</p>
      </div>

      <div class="card" style="background:#ffffff; border:1px solid #E2E8F0; border-radius:14px; padding:24px;">
        <h3 style="font-size:1.2rem; font-weight:800; color:#0F172A; margin:0 0 10px 0;">Dunlop</h3>
        <p style="font-size:0.92rem; line-height:1.65; color:#475569; margin:0;">Long-time factory fitment for Toyota Land Cruiser and Prado with Grandtrek, Dunlop offers robust all-around performance and good sand flotation. Reliable choice for long-standing UAE SUV owners.</p>
      </div>
    </div>
  </div>
</section>

<!-- 4. MID-RANGE BRANDS DETAIL -->
<section class="tv-section-block" style="background:#ffffff;">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow">&mdash; TIER 2 VALUE LEADERS &mdash;</span>
      <h2>Mid-range brands</h2>
      <p class="lead">Delivering proven durability and engineering excellence at realistic price points.</p>
    </div>

    <div class="grid g3" style="margin-top:28px;">
      <div class="card" style="border:1px solid #E2E8F0; border-radius:14px; padding:22px;">
        <h3 style="font-size:1.15rem; font-weight:800; color:#0F172A; margin:0 0 8px 0;">Hankook</h3>
        <p style="font-size:0.9rem; line-height:1.6; color:#475569; margin:0;">Korean tier-1 supplier chosen by BMW and Porsche; the Ventus and Dynapro lines offer exceptional quietness and long life at sharp pricing.</p>
      </div>
      <div class="card" style="border:1px solid #E2E8F0; border-radius:14px; padding:22px;">
        <h3 style="font-size:1.15rem; font-weight:800; color:#0F172A; margin:0 0 8px 0;">Yokohama</h3>
        <p style="font-size:0.9rem; line-height:1.6; color:#475569; margin:0;">Japanese precision engineering; the Geolandar is an iconic UAE desert and highway fitment with outstanding sand flotation.</p>
      </div>
      <div class="card" style="border:1px solid #E2E8F0; border-radius:14px; padding:22px;">
        <h3 style="font-size:1.15rem; font-weight:800; color:#0F172A; margin:0 0 8px 0;">Toyo</h3>
        <p style="font-size:0.9rem; line-height:1.6; color:#475569; margin:0;">Celebrated for the Open Country 4x4 lineup and Proxes sports tyres, delivering aggressive styling and rugged puncture defense.</p>
      </div>
      <div class="card" style="border:1px solid #E2E8F0; border-radius:14px; padding:22px;">
        <h3 style="font-size:1.15rem; font-weight:800; color:#0F172A; margin:0 0 8px 0;">Falken</h3>
        <p style="font-size:0.9rem; line-height:1.6; color:#475569; margin:0;">Sumitomo-backed Japanese brand; the Wildpeak A/T is a top off-road favourite while Ziex provides great passenger car grip.</p>
      </div>
      <div class="card" style="border:1px solid #E2E8F0; border-radius:14px; padding:22px;">
        <h3 style="font-size:1.15rem; font-weight:800; color:#0F172A; margin:0 0 8px 0;">Kumho</h3>
        <p style="font-size:0.9rem; line-height:1.6; color:#475569; margin:0;">Consistent Korean reliability; Ecsta and Crugen lines provide comfortable, quiet highway tracking for saloons and crossovers.</p>
      </div>
      <div class="card" style="border:1px solid #E2E8F0; border-radius:14px; padding:22px;">
        <h3 style="font-size:1.15rem; font-weight:800; color:#0F172A; margin:0 0 8px 0;">Nexen</h3>
        <p style="font-size:0.9rem; line-height:1.6; color:#475569; margin:0;">Factory equipment on many Hyundai and Kia vehicles; N'Fera and Roadian lines represent outstanding durability per dirham.</p>
      </div>
      <div class="card" style="border:1px solid #E2E8F0; border-radius:14px; padding:22px;">
        <h3 style="font-size:1.15rem; font-weight:800; color:#0F172A; margin:0 0 8px 0;">BFGoodrich</h3>
        <p style="font-size:0.9rem; line-height:1.6; color:#475569; margin:0;">The global benchmark in extreme all-terrain and mud-terrain rubber; the All-Terrain T/A KO2 and KO3 are virtually indestructible.</p>
      </div>
      <div class="card" style="border:1px solid #E2E8F0; border-radius:14px; padding:22px;">
        <h3 style="font-size:1.15rem; font-weight:800; color:#0F172A; margin:0 0 8px 0;">Cooper</h3>
        <p style="font-size:0.9rem; line-height:1.6; color:#475569; margin:0;">American heavy-duty SUV tyre maker; Discoverer A/T3 provides heavy carcass plies and great rocky wadi performance.</p>
      </div>
      <div class="card" style="border:1px solid #E2E8F0; border-radius:14px; padding:22px;">
        <h3 style="font-size:1.15rem; font-weight:800; color:#0F172A; margin:0 0 8px 0;">Nitto &amp; Vredestein</h3>
        <p style="font-size:0.9rem; line-height:1.6; color:#475569; margin:0;">Specialty performance and enthusiast 4x4 fitments combining striking tread aesthetic with refined high-speed wet/dry composure.</p>
      </div>
    </div>
  </div>
</section>

<!-- 5. VALUE BRANDS DETAIL -->
<section class="tv-section-block" style="background:#F8FAFC;">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow">&mdash; TIER 3 BUDGET OPTIONS &mdash;</span>
      <h2>Value brands</h2>
      <p class="lead">Laufenn, Giti, Sumitomo, Zeetex, Roadstone. Be straight about the trade-off.</p>
    </div>

    <div class="card" style="background:#ffffff; border:1px solid #E2E8F0; border-radius:18px; padding:32px; max-width:880px; margin:0 auto;">
      <p style="font-size:1.02rem; line-height:1.75; color:#334155; margin:0 0 16px 0;">
        Value brands allow vehicle owners to replace worn rubber legally and affordably. Brands like <strong>Laufenn</strong> (Hankook's sub-brand), <strong>Sumitomo</strong> (Japan), <strong>Giti</strong>, <strong>Zeetex</strong>, and <strong>Roadstone</strong> pass full GCC homologation and provide dependable traction for short urban commutes.
      </p>
      <p style="font-size:1.02rem; line-height:1.75; color:#334155; margin:0;">
        The honest trade-off: Expect slightly higher road noise, softer sidewalls, and a lifespan of 30,000 to 40,000 km compared to the 60,000+ km of a premium Michelin or Bridgestone. If you do 30,000 km of highway commuting a year, a mid-range or premium set is cheaper per kilometre.
      </p>
    </div>
  </div>
</section>

<!-- 6. WHICH BRAND IS BEST FOR UAE HEAT? -->
<section class="tv-section-block" style="background:#ffffff;">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow">&mdash; CRITICAL HEAT ADVICE &mdash;</span>
      <h2>Which brand is best for UAE heat?</h2>
      <p class="lead">The direct answer to the most common question asked by drivers in Dubai and Abu Dhabi.</p>
    </div>

    <div class="tv-4x4-load-block">
      <div class="tv-4x4-load-grid">
        <div>
          <span class="tv-4x4-load-badge-pill">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
            Heat Resistance Benchmark
          </span>
          <h3 style="font-size:1.45rem; font-weight:800; color:#0F172A; margin:0 0 12px 0;">Bridgestone and Michelin handle UAE summer heat better than any other tyre brand.</h3>
          <p style="font-size:1.02rem; line-height:1.7; color:#334155; margin:0 0 16px 0;">Both manufacturers formulate specialized GCC-specification compounds that resist thermal hardening and vulcanisation breakdown when road surfaces reach 55&deg;C to 60&deg;C in July and August.</p>
          <p style="font-size:1.02rem; line-height:1.7; color:#334155; margin:0;">Continental and Hankook follow closely behind with exceptional high-temperature silica polymers. For severe desert or heavy-towing applications, Bridgestone's high-tensile steel belts and reinforced beads provide the highest safety margin against high-speed thermal blowouts.</p>
        </div>
        <div class="tv-4x4-load-card">
          <div style="font-weight:800; color:#0F172A; font-size:1.05rem; margin-bottom:12px;">Temperature Grading &amp; Heat Rules</div>
          <div style="font-size:0.9rem; color:#475569; line-height:1.6; margin-bottom:12px;">
            &bull; Always verify <strong>Temperature Grade A</strong> on the sidewall for sustained UAE highway driving.<br>
            &bull; Never let tyre age exceed 5 years in UAE heat, regardless of remaining tread depth.<br>
            &bull; Check tyre cold pressures monthly to prevent excessive internal heat build-up.
          </div>
          <a class="tv-btn-wa-green" href="https://wa.me/971505069575?text=Hi%20TyresVision%2C%20which%20tyre%20brand%20do%20you%20recommend%20for%20my%20car%27s%20summer%20driving%3F" target="_blank" rel="noopener" style="width:100%; justify-content:center; padding:10px 16px; font-size:0.9rem;">
            <span>Ask Our Specialists on WhatsApp</span>
          </a>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- 7. BRAND BY VEHICLE TYPE -->
<section class="price-section tv-section-block" style="background:#F8FAFC;">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow">&bull; APPLICATION GUIDE &bull;</span>
      <h2>Brand by vehicle type</h2>
      <p class="lead">We recommend a tyre tier tailored to your driving requirements rather than forcing a single brand.</p>
    </div>

    <div class="price-table-card" style="margin-top:28px;">
      <div class="price-table-scroll">
        <table class="price-table tv-4x4-table" aria-label="Brand Recommendation by Vehicle Type">
          <thead>
            <tr>
              <th scope="col">Vehicle Type</th>
              <th scope="col">Recommended Tier</th>
              <th scope="col">Top Brand Choices</th>
              <th scope="col">Primary Benefit</th>
              <th scope="col" style="text-align:right;">Action</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td style="font-weight:700; color:#0F172A;">City Car &amp; Compact</td>
              <td style="color:#2563FF; font-weight:700;">Value to Mid-Range</td>
              <td style="color:#475569;">Kumho, Nexen, Laufenn, Giti</td>
              <td style="color:#64748B;">Low cost per km, easy city handling</td>
              <td style="text-align:right;"><a class="get-quote-link" href="https://wa.me/971505069575?text=Hi%20TyresVision%2C%20I%20need%20tyres%20for%20a%20compact%20car." target="_blank" rel="noopener"><span>Get Quote</span> &rarr;</a></td>
            </tr>
            <tr>
              <td style="font-weight:700; color:#0F172A;">Family Sedan (Camry, Accord)</td>
              <td style="color:#2563FF; font-weight:700;">Mid-Range (Sweet Spot)</td>
              <td style="color:#475569;">Hankook, Yokohama, Toyo, Dunlop</td>
              <td style="color:#64748B;">Quiet cabin, long tread life, balanced braking</td>
              <td style="text-align:right;"><a class="get-quote-link" href="https://wa.me/971505069575?text=Hi%20TyresVision%2C%20I%20need%20tyres%20for%20a%20family%20sedan." target="_blank" rel="noopener"><span>Get Quote</span> &rarr;</a></td>
            </tr>
            <tr>
              <td style="font-weight:700; color:#0F172A;">Highway SUV &amp; Crossover</td>
              <td style="color:#2563FF; font-weight:700;">Mid-Range to Premium</td>
              <td style="color:#475569;">Michelin, Continental, Bridgestone, Hankook</td>
              <td style="color:#64748B;">High load support, 140 km/h thermal stamina</td>
              <td style="text-align:right;"><a class="get-quote-link" href="https://wa.me/971505069575?text=Hi%20TyresVision%2C%20I%20need%20tyres%20for%20a%20highway%20SUV." target="_blank" rel="noopener"><span>Get Quote</span> &rarr;</a></td>
            </tr>
            <tr>
              <td style="font-weight:700; color:#0F172A;">Off-Road 4x4 &amp; Pickup</td>
              <td style="color:#2563FF; font-weight:700;">Mid-Range to Premium A/T</td>
              <td style="color:#475569;">BFGoodrich, Yokohama, Cooper, Dunlop</td>
              <td style="color:#64748B;">Desert deflation flotation, cut-resistant sidewalls</td>
              <td style="text-align:right;"><a class="get-quote-link" href="https://wa.me/971505069575?text=Hi%20TyresVision%2C%20I%20need%20tyres%20for%20an%20off-road%204x4." target="_blank" rel="noopener"><span>Get Quote</span> &rarr;</a></td>
            </tr>
            <tr>
              <td style="font-weight:700; color:#0F172A;">Electric Vehicle (Tesla, BYD)</td>
              <td style="color:#2563FF; font-weight:700;">Premium EV-Rated (HL/XL)</td>
              <td style="color:#475569;">Michelin Acoustic, Pirelli PNCS, Hankook iON</td>
              <td style="color:#64748B;">Acoustic foam, low rolling resistance, torque grip</td>
              <td style="text-align:right;"><a class="get-quote-link" href="https://wa.me/971505069575?text=Hi%20TyresVision%2C%20I%20need%20tyres%20for%20an%20electric%20car." target="_blank" rel="noopener"><span>Get Quote</span> &rarr;</a></td>
            </tr>
            <tr>
              <td style="font-weight:700; color:#0F172A;">Performance Sports Car</td>
              <td style="color:#2563FF; font-weight:700;">Premium High-Performance</td>
              <td style="color:#475569;">Michelin Pilot Sport, Pirelli P Zero, Continental</td>
              <td style="color:#64748B;">Razor-sharp steering, high-speed rating (Y/Z)</td>
              <td style="text-align:right;"><a class="get-quote-link" href="https://wa.me/971505069575?text=Hi%20TyresVision%2C%20I%20need%20tyres%20for%20a%20performance%20car." target="_blank" rel="noopener"><span>Get Quote</span> &rarr;</a></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</section>

<!-- 8. ARE CHEAP TYRES SAFE IN THE UAE? -->
<section class="tv-section-block" style="background:#ffffff;">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow">&mdash; HONEST SAFETY ANALYSIS &mdash;</span>
      <h2>Are cheap tyres safe in the UAE?</h2>
      <p class="lead" style="max-width:820px; margin:0 auto 28px auto;">Yes if correctly load-rated and date-fresh. No if under-rated or three years old before fitting. The danger is the specification, not the badge.</p>
    </div>

    <div class="card" style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:18px; padding:32px; max-width:880px; margin:0 auto;">
      <p style="font-size:1.02rem; line-height:1.75; color:#334155; margin:0 0 16px 0;">Every tyre sold through TyresVision is 100% compliant with ESMA regulatory standards and bears official GCC customs certification. A budget tyre in the correct size, load index, and speed rating is fundamentally safe for normal commuting.</p>
      <p style="font-size:0.98rem; line-height:1.7; color:#475569; margin:0;">Where drivers run into catastrophic risks is fitting an under-rated budget tyre &mdash; for example, installing a 111-load passenger tyre on a heavy Nissan Patrol or Tesla that demands a 116 or HL rating &mdash; or buying old stock that has aged on an un-airconditioned shelf. At TyresVision, we strictly enforce factory-fresh production dates and correct load matching on every single tyre we deliver.</p>
    </div>

    {build_internal_links_card('Looking for specific terrain rubber? View our <a href="/off-road-4x4-tyres" style="color:#2563FF; font-weight:700; text-decoration:underline;">off-road and 4x4 tyres</a>, explore high-efficiency <a href="/ev-tyres" style="color:#2563FF; font-weight:700; text-decoration:underline;">EV tyres</a>, compare popular <a href="/tyre-sizes" style="color:#2563FF; font-weight:700; text-decoration:underline;">tyre sizes</a>, or look up <a href="/tyres-by-car" style="color:#2563FF; font-weight:700; text-decoration:underline;">tyres for your car model</a>.')}
  </div>
</section>

<!-- 9. BRAND FAQS -->
{build_faq_section("Brand FAQs", faqs, eyebrow="TYRE BRAND FAQS")}

<!-- 10. BOTTOM CTA -->
{build_bottom_cta(
    heading="Compare 60+ Tyre Brands with Transparent UAE Pricing",
    lead="Send your tyre size on WhatsApp. Our specialists provide instant quotes across premium, mid-range and value tiers with free fitting.",
    wa_msg="Hi TyresVision, I would like to compare brand prices for my tyre size.",
    wa_btn_text="WhatsApp for Brand Quotes"
)}
"""
    return content
