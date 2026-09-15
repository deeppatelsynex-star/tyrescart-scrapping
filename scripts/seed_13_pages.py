"""
scripts/seed_13_pages.py
Seeds the 12 new CMS pages (Pages 2 through 13) specified in
'TyresVision-13-Page-Build-Plan 1.docx' into the MySQL `pages` table.
All content is formatted with clean semantic HTML suitable for CKEditor
and rendering in templates/Client/Page.html.
"""

import os
import sys
import json

# Add project root and app to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app'))

from db import get_connection

PAGES_DATA = [
    # -------------------------------------------------------------------------
    # PAGE 2: EV Tyres (/ev-tyres)
    # -------------------------------------------------------------------------
    {
        'slug': 'ev-tyres',
        'title': {'en': 'EV and Hybrid Tyres in the UAE'},
        'seo_title': {'en': 'EV Tyres in Dubai & Abu Dhabi | Tesla, BYD | TyresVision'},
        'meta_description': {'en': 'Tyres for Tesla, BYD, hybrid and electric cars in the UAE. Correct load rating and low rolling resistance, fitted free at a centre near you.'},
        'content': {'en': """
<div class="tv-page-lead">
  <p>Electric and hybrid vehicles present unique demands on rubber. With instantaneous electric torque, zero engine noise to mask road rumble, and curb weights typically 20% to 30% greater than equivalent petrol vehicles due to high-capacity battery packs, selecting the correct tyre specification is essential for safety, range efficiency, and tyre longevity in the UAE.</p>
</div>

<div class="tv-cta-box">
  <div class="tv-cta-content">
    <h3>Need an exact tyre quote for your EV?</h3>
    <p>Share your vehicle make, model, or tyre sidewall size on WhatsApp. We confirm compatible EV-rated options and same-day fitting across the UAE.</p>
  </div>
  <div class="tv-cta-actions">
    <a href="https://wa.me/971505069575?text=Hi%20TyresVision%2C%20I%20need%20a%20tyre%20quote%20for%20my%20electric%20car." target="_blank" rel="noopener" class="btn btn-wa">
      WhatsApp for EV Quote
    </a>
    <a href="tel:+971505069575" class="btn btn-call">+971 50 506 9575</a>
  </div>
</div>

<h2>Why an electric car needs different tyres</h2>
<p>An electric vehicle produces maximum torque from zero RPM. When accelerating from a stoplight, standard passenger tyres undergo tremendous shear stress across the contact patch, leading to accelerated center and shoulder tread wear. In UAE summer tarmac temperatures exceeding 55&deg;C, a non-EV rated tyre fitted on a dual-motor Tesla or BYD can degrade up to 40% faster than intended.</p>
<p>Dedicated EV tyres incorporate three distinct engineering differences:</p>
<ul>
  <li><strong>Stiffer sidewall and reinforced carcass:</strong> Handles the continuous 2,000&ndash;2,600 kg curb weight without excessive deflection or shoulder scrubbing.</li>
  <li><strong>Acoustic sound-dampening foam:</strong> Because electric drivetrains operate silently, tyre cavity resonance becomes the dominant in-cabin sound. Leading EV fitments (such as Michelin Acoustic, Continental ContiSilent, and Pirelli Noise Cancelling System) integrate polyurethane foam on the inner liner to absorb high-frequency road rumble.</li>
  <li><strong>Low rolling resistance compounds:</strong> Advanced silica compounds minimize energy dissipation per rotation, protecting battery range by up to 7% to 10% per full charge.</li>
</ul>

<h2>Tyres by electric and hybrid model</h2>
<p>Below are common factory fitments and technical specifications for popular electric and hybrid vehicles driven across Dubai and Abu Dhabi:</p>

<div class="table-responsive">
  <table class="tv-table">
    <thead>
      <tr>
        <th>Vehicle</th>
        <th>Common Sizes</th>
        <th>Recommended Specification</th>
        <th>Action</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Tesla Model 3</strong></td>
        <td>235/45 R18, 235/40 R19, 235/35 R20</td>
        <td>EV-rated, acoustic foam lining, low rolling resistance</td>
        <td><a href="https://wa.me/971505069575?text=Quote%20for%20Tesla%20Model%203%20tyres" class="tv-table-link">Price Quote &rarr;</a></td>
      </tr>
      <tr>
        <td><strong>Tesla Model Y</strong></td>
        <td>255/45 R19, 255/40 R20, 275/35 R21</td>
        <td>High Load (XL/HL), reinforced sidewall, EV compound</td>
        <td><a href="https://wa.me/971505069575?text=Quote%20for%20Tesla%20Model%20Y%20tyres" class="tv-table-link">Price Quote &rarr;</a></td>
      </tr>
      <tr>
        <td><strong>BYD Atto 3</strong></td>
        <td>215/60 R17, 235/50 R18</td>
        <td>EV-rated, comfort-biased silica compound</td>
        <td><a href="https://wa.me/971505069575?text=Quote%20for%20BYD%20Atto%203%20tyres" class="tv-table-link">Price Quote &rarr;</a></td>
      </tr>
      <tr>
        <td><strong>BYD Seal</strong></td>
        <td>235/45 R19, 245/45 R19</td>
        <td>Low rolling resistance, high-speed rating (W/Y)</td>
        <td><a href="https://wa.me/971505069575?text=Quote%20for%20BYD%20Seal%20tyres" class="tv-table-link">Price Quote &rarr;</a></td>
      </tr>
      <tr>
        <td><strong>Hyundai Ioniq 5</strong></td>
        <td>235/55 R19, 255/45 R20</td>
        <td>Heavy load rating, sound-absorbing foam lining</td>
        <td><a href="https://wa.me/971505069575?text=Quote%20for%20Hyundai%20Ioniq%205%20tyres" class="tv-table-link">Price Quote &rarr;</a></td>
      </tr>
      <tr>
        <td><strong>Kia EV6</strong></td>
        <td>235/55 R19, 255/45 R20</td>
        <td>EV-rated, quiet compound, high wear resistance</td>
        <td><a href="https://wa.me/971505069575?text=Quote%20for%20Kia%20EV6%20tyres" class="tv-table-link">Price Quote &rarr;</a></td>
      </tr>
      <tr>
        <td><strong>Polestar 2</strong></td>
        <td>245/45 R19, 245/40 R20</td>
        <td>Performance EV compound, high cornering stiffness</td>
        <td><a href="https://wa.me/971505069575?text=Quote%20for%20Polestar%202%20tyres" class="tv-table-link">Price Quote &rarr;</a></td>
      </tr>
      <tr>
        <td><strong>Mercedes EQE / EQS</strong></td>
        <td>255/45 R19, 265/40 R20, 265/35 R21</td>
        <td>XL/HL load index, MO-E (Mercedes Original Extended EV)</td>
        <td><a href="https://wa.me/971505069575?text=Quote%20for%20Mercedes%20EQ%20tyres" class="tv-table-link">Price Quote &rarr;</a></td>
      </tr>
      <tr>
        <td><strong>Audi e-tron / Q8 e-tron</strong></td>
        <td>255/55 R19, 265/45 R21, 285/40 R22</td>
        <td>High Load index, acoustic foam, AO (Audi Original)</td>
        <td><a href="https://wa.me/971505069575?text=Quote%20for%20Audi%20e-tron%20tyres" class="tv-table-link">Price Quote &rarr;</a></td>
      </tr>
      <tr>
        <td><strong>Toyota &amp; Lexus Hybrids</strong></td>
        <td>215/55 R17, 235/45 R18</td>
        <td>Low rolling resistance fuel saver compounds</td>
        <td><a href="https://wa.me/971505069575?text=Quote%20for%20Toyota%20Hybrid%20tyres" class="tv-table-link">Price Quote &rarr;</a></td>
      </tr>
    </tbody>
  </table>
</div>

<h2>Load index and the &ldquo;HL&rdquo; marking</h2>
<p>Modern battery electric SUVs frequently demand load capacities higher than even traditional Extra Load (XL) tyres can deliver. Tyre manufacturers developed the <strong>HL (High Load)</strong> standard to support up to 25% higher loads at equivalent inflation pressures.</p>
<p>If your vehicle manufacturer door placard specifies an &ldquo;HL&rdquo; prefix (such as <em>HL 255/45 R19</em>), fitting a standard-load tyre to save cost is hazardous. In ambient UAE temperatures exceeding 45&deg;C, an under-rated tyre under heavy dynamic load experiences internal heat build-up that can precipitate structural delamination.</p>

<h2>Do EV tyres cost more?</h2>
<p>EV-specific tyres typically cost 10% to 20% more than generic passenger tyres in the identical size. However, that difference is recovered over the lifespan of the tyre. Standard tyres installed on an electric vehicle wear out significantly faster, requiring replacement prematurely, whereas dedicated EV compounds maintain even tread wear and preserve range.</p>

<h2>Run-flat tyres &mdash; who has them and how they work</h2>
<p>Many premium vehicles (including BMW, Mercedes-Benz, MINI, and select Lexus models) are factory-equipped with run-flat tyres (RFT). Run-flats feature reinforced sidewall inserts that sustain vehicle weight after a total loss of air pressure, allowing you to drive up to 80 km at speeds up to 80 km/h to reach safety.</p>

<h3>Can a run-flat tyre be repaired?</h3>
<p>Almost always, <strong>no</strong>. Once a run-flat tyre has been driven with zero or low pressure, the internal structural rubber in the sidewall undergoes severe heat degradation. Even if the external sidewall appears pristine, the internal cords may be compromised. For safety reasons, tyre manufacturers strongly mandate replacement rather than plugging or patching run-flats that have been driven flat.</p>

<h3>Can I change run-flats to normal tyres?</h3>
<p>Yes, you can swap run-flats for conventional tyres to enjoy a noticeably softer ride and lower replacement cost. However, verify your trunk first: most run-flat equipped vehicles do not contain a spare wheel, jack, or wrench. If you switch to conventional tyres, ensure you carry a 12V inflator kit and emergency sealant.</p>

<h2>Mobile fitting for EVs at your home or office</h2>
<p>Electric vehicles must strictly be lifted at dedicated reinforced jacking points beneath the rocker panels &mdash; never on the battery casing or undertray. Our <a href="/mobile-tyre-fitting">mobile tyre fitting</a> vans carry low-profile jacks, vehicle-specific rubber lifting pucks, and precision torque wrenches to service electric vehicles safely in your driveway or building parking bay.</p>

<p>Compare premium and mid-range <a href="/tyre-brands">tyre brands</a>, verify all standard <a href="/tyre-sizes">tyre sizes</a>, or look up specific <a href="/tyres-by-car">tyres for your car model</a>.</p>

<h2>EV Tyre FAQs</h2>
<div class="tv-faq-container">
  <div class="tv-faq-item">
    <button type="button" class="tv-faq-trigger">
      <span>Do I need special tyres for my Tesla?</span>
      <span class="tv-faq-icon">+</span>
    </button>
    <div class="tv-faq-panel">
      <p>Yes, Tesla models require tyres rated for high vehicle weight and immediate torque, ideally equipped with acoustic noise-dampening foam (like Tesla TO specification) to eliminate cabin booming at highway speeds.</p>
    </div>
  </div>

  <div class="tv-faq-item">
    <button type="button" class="tv-faq-trigger">
      <span>How long do EV tyres last in the UAE?</span>
      <span class="tv-faq-icon">+</span>
    </button>
    <div class="tv-faq-panel">
      <p>With correct inflation and regular rotation every 10,000 km, premium EV tyres typically achieve 35,000 to 50,000 km in the UAE. Standard non-EV tyres on an electric car may wear out in as few as 20,000 km.</p>
    </div>
  </div>

  <div class="tv-faq-item">
    <button type="button" class="tv-faq-trigger">
      <span>Do EV tyres reduce or increase driving range?</span>
      <span class="tv-faq-icon">+</span>
    </button>
    <div class="tv-faq-panel">
      <p>EV-rated tyres feature specialized low rolling resistance compounds designed to maximize range, adding up to 15 to 30 km of driving distance per full battery charge compared to conventional tyres.</p>
    </div>
  </div>

  <div class="tv-faq-item">
    <button type="button" class="tv-faq-trigger">
      <span>Can you fit EV tyres in my apartment car park?</span>
      <span class="tv-faq-icon">+</span>
    </button>
    <div class="tv-faq-panel">
      <p>Yes. Our mobile fitting vans carry specialized equipment and rubber jacking pads to change and balance EV tyres on-site in residential car parks across Dubai and Abu Dhabi.</p>
    </div>
  </div>

  <div class="tv-faq-item">
    <button type="button" class="tv-faq-trigger">
      <span>What happens if I fit standard tyres to my electric vehicle?</span>
      <span class="tv-faq-icon">+</span>
    </button>
    <div class="tv-faq-panel">
      <p>Standard tyres will experience rapid and uneven tread wear, significantly increased road noise inside the cabin, longer braking distances under high vehicle mass, and potential overheating during summer highway driving.</p>
    </div>
  </div>
</div>
"""}
    },

    # -------------------------------------------------------------------------
    # PAGE 3: Off-Road & 4x4 Tyres (/off-road-4x4-tyres)
    # -------------------------------------------------------------------------
    {
        'slug': 'off-road-4x4-tyres',
        'title': {'en': 'Off-Road and 4x4 Tyres in the UAE'},
        'seo_title': {'en': 'Off-Road & 4x4 Tyres in the UAE | TyresVision'},
        'meta_description': {'en': 'Off-road, all-terrain and highway 4x4 tyres for Patrol, Land Cruiser and Prado. Honest advice on desert versus tarmac, fitted free across the UAE.'},
        'content': {'en': """
<div class="tv-page-lead">
  <p>The UAE is one of the world's most demanding proving grounds for 4x4 and SUV tyres. Between sustained 140 km/h highway runs in 50&deg;C heat and weekend dune driving across the Empty Quarter, selecting the correct tyre balance between Highway-Terrain (H/T), All-Terrain (A/T), and Mud-Terrain (M/T) determines your comfort, fuel economy, and safety.</p>
</div>

<div class="tv-cta-box">
  <div class="tv-cta-content">
    <h3>Looking for SUV or 4x4 tyre prices?</h3>
    <p>Message our specialists on WhatsApp with your vehicle model or tyre size. We provide upfront pricing with free fitting across partner centres or mobile van dispatch.</p>
  </div>
  <div class="tv-cta-actions">
    <a href="https://wa.me/971505069575?text=Hi%20TyresVision%2C%20I%20need%204x4%20and%20SUV%20tyre%20prices." target="_blank" rel="noopener" class="btn btn-wa">
      WhatsApp for 4x4 Quote
    </a>
    <a href="tel:+971505069575" class="btn btn-call">+971 50 506 9575</a>
  </div>
</div>

<h2>Highway, all-terrain or mud-terrain &mdash; which do you actually need?</h2>
<p>Most UAE SUV owners drive primarily on paved tarmac but are frequently upsold aggressive All-Terrain tyres that they never utilize. Understanding the trade-offs is vital:</p>

<div class="tv-grid-3">
  <div class="tv-card">
    <h3>Highway Terrain (H/T)</h3>
    <p><strong>Best for:</strong> 90%+ tarmac commuting, family road trips, school runs.</p>
    <p>Features closed shoulder blocks and longitudinal water grooves. Delivers the quietest cabin, shortest dry and wet braking distances, lowest rolling resistance, and superior high-speed heat dissipation in UAE summers.</p>
  </div>
  <div class="tv-card">
    <h3>All-Terrain (A/T)</h3>
    <p><strong>Best for:</strong> 60% tarmac, 40% desert dunes, gravel wadis, camping.</p>
    <p>Interlocking tread blocks with reinforced sidewalls (e.g. BFGoodrich KO2, Cooper Discoverer, Yokohama Geolandar). Excellent sand flotation when deflated, though with a moderate increase in highway road hum and fuel consumption.</p>
  </div>
  <div class="tv-card">
    <h3>Mud-Terrain (M/T)</h3>
    <p><strong>Best for:</strong> Dedicated off-road rigs, rocky mountains, heavy mud.</p>
    <p>Massive tread lugs and extreme sidewall armour. Highly resilient against rock punctures, but noisy on highways with longer braking distances on wet city streets.</p>
  </div>
</div>

<h2>Tyres by 4x4 model</h2>
<p>Popular factory fitments and common sizing for leading SUVs across the Emirates:</p>

<div class="table-responsive">
  <table class="tv-table">
    <thead>
      <tr>
        <th>Vehicle</th>
        <th>Common Sizes</th>
        <th>Recommended Tyre Type</th>
        <th>Action</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Toyota Land Cruiser (LC200 / LC300)</strong></td>
        <td>285/65 R17, 285/60 R18, 275/60 R20</td>
        <td>Highway (H/T) for daily use; A/T for dune touring</td>
        <td><a href="https://wa.me/971505069575?text=Quote%20for%20Land%20Cruiser%20tyres" class="tv-table-link">Price Quote &rarr;</a></td>
      </tr>
      <tr>
        <td><strong>Nissan Patrol (Y61 / Y62)</strong></td>
        <td>275/70 R16, 265/70 R18, 275/60 R20</td>
        <td>Highway (H/T) for daily use; A/T for sand driving</td>
        <td><a href="https://wa.me/971505069575?text=Quote%20for%20Nissan%20Patrol%20tyres" class="tv-table-link">Price Quote &rarr;</a></td>
      </tr>
      <tr>
        <td><strong>Toyota Prado</strong></td>
        <td>265/65 R17, 265/60 R18, 265/55 R19</td>
        <td>H/T or balanced A/T</td>
        <td><a href="https://wa.me/971505069575?text=Quote%20for%20Toyota%20Prado%20tyres" class="tv-table-link">Price Quote &rarr;</a></td>
      </tr>
      <tr>
        <td><strong>Mitsubishi Pajero</strong></td>
        <td>265/70 R16, 265/60 R18</td>
        <td>Highway (H/T) gives best comfort and longevity</td>
        <td><a href="https://wa.me/971505069575?text=Quote%20for%20Pajero%20tyres" class="tv-table-link">Price Quote &rarr;</a></td>
      </tr>
      <tr>
        <td><strong>Toyota Fortuner / Hilux</strong></td>
        <td>265/65 R17, 265/60 R18</td>
        <td>A/T or rugged H/T</td>
        <td><a href="https://wa.me/971505069575?text=Quote%20for%20Fortuner%20Hilux%20tyres" class="tv-table-link">Price Quote &rarr;</a></td>
      </tr>
      <tr>
        <td><strong>Jeep Wrangler (JK / JL)</strong></td>
        <td>255/75 R17, 285/70 R17, 33x12.5 R17</td>
        <td>A/T or M/T with 3-ply sidewall</td>
        <td><a href="https://wa.me/971505069575?text=Quote%20for%20Jeep%20Wrangler%20tyres" class="tv-table-link">Price Quote &rarr;</a></td>
      </tr>
      <tr>
        <td><strong>Ford Explorer / Expedition</strong></td>
        <td>255/50 R20, 275/55 R20</td>
        <td>Highway (H/T) comfort specification</td>
        <td><a href="https://wa.me/971505069575?text=Quote%20for%20Ford%20SUV%20tyres" class="tv-table-link">Price Quote &rarr;</a></td>
      </tr>
      <tr>
        <td><strong>Chevrolet Tahoe / Suburban</strong></td>
        <td>265/65 R18, 275/55 R20, 275/50 R22</td>
        <td>Highway H/T with high load index</td>
        <td><a href="https://wa.me/971505069575?text=Quote%20for%20Tahoe%20tyres" class="tv-table-link">Price Quote &rarr;</a></td>
      </tr>
      <tr>
        <td><strong>Mercedes G-Class (G63 / G500)</strong></td>
        <td>275/50 R20, 295/40 R22</td>
        <td>High-performance H/T or dedicated A/T</td>
        <td><a href="https://wa.me/971505069575?text=Quote%20for%20G-Class%20tyres" class="tv-table-link">Price Quote &rarr;</a></td>
      </tr>
    </tbody>
  </table>
</div>

<h2>Load rating on heavy SUVs &mdash; why it matters</h2>
<p>Heavy SUVs like the Nissan Patrol and Toyota Land Cruiser weigh nearly 2.8 tonnes unloaded. Loaded with family, luggage, and recovery gear, axle weights easily exceed 3.3 tonnes. The <strong>load index</strong> (such as 112, 116, or 121) stamped after the tyre size defines the maximum weight capacity.</p>
<p>Fitting passenger-car rated tyres with a lower load index to save a few dirhams creates severe blowout risk under sustained highway speeds in July heat. At TyresVision, we strictly adhere to manufacturer load ratings.</p>

<h2>Tyres for desert driving</h2>
<p>Sand driving requires deflating tyres to between <strong>14 and 18 PSI</strong> to lengthen the footprint and float over soft sand. When choosing an off-road tyre for UAE dunes:</p>
<ul>
  <li>Look for flexible 2-ply or 3-ply polyester sidewalls that bag out evenly without unseating the bead.</li>
  <li>Avoid low-profile 21&quot; or 22&quot; rims for desert driving; 17&quot; or 18&quot; wheels offer ample sidewall cushion.</li>
  <li><strong>Critical safety rule:</strong> Always re-inflate back to recommended highway pressure (32&ndash;36 PSI) before driving at speed on paved highways. Running deflated tyres on tarmac at 120 km/h causes rapid overheating and sidewall destruction.</li>
</ul>

<p>Explore our full roster of <a href="/tyre-brands">tyre brands</a>, check our guide to <a href="/tyres-by-car">tyres for your car model</a>, or compare common <a href="/tyre-sizes">tyre sizes</a>. Need installation in Dubai? Visit our <a href="/tyre-shop-dubai">tyre fitting in Dubai</a> page.</p>

<h2>Off-Road &amp; 4x4 Tyre FAQs</h2>
<div class="tv-faq-container">
  <div class="tv-faq-item">
    <button type="button" class="tv-faq-trigger">
      <span>How long do All-Terrain tyres last in the UAE?</span>
      <span class="tv-faq-icon">+</span>
    </button>
    <div class="tv-faq-panel">
      <p>Quality All-Terrain tyres (like BFGoodrich KO2 or Yokohama Geolandar) typically last 50,000 to 70,000 km in the UAE if rotated every 8,000 to 10,000 km and kept at correct highway inflation pressures.</p>
    </div>
  </div>

  <div class="tv-faq-item">
    <button type="button" class="tv-faq-trigger">
      <span>Can I use Mud-Terrain (M/T) tyres for daily highway driving?</span>
      <span class="tv-faq-icon">+</span>
    </button>
    <div class="tv-faq-panel">
      <p>You can, but they are significantly louder, generate vibration at highway speeds above 100 km/h, wear out faster in summer heat, and yield longer braking distances on wet city roads.</p>
    </div>
  </div>

  <div class="tv-faq-item">
    <button type="button" class="tv-faq-trigger">
      <span>What is the ideal tyre pressure for UAE desert dunes?</span>
      <span class="tv-faq-icon">+</span>
    </button>
    <div class="tv-faq-panel">
      <p>Between 14 and 18 PSI is ideal for general sand driving. Never drop below 12 PSI unless using beadlock wheels, as the tyre bead can pop off the rim under lateral load.</p>
    </div>
  </div>

  <div class="tv-faq-item">
    <button type="button" class="tv-faq-trigger">
      <span>Do bigger tyres throw off my speedometer?</span>
      <span class="tv-faq-icon">+</span>
    </button>
    <div class="tv-faq-panel">
      <p>Yes. Installing taller tyres increases the overall rolling circumference, causing your speedometer to read slightly slower than your actual road speed. It can also increase fuel consumption slightly due to altered gearing.</p>
    </div>
  </div>
</div>
"""}
    },

    # -------------------------------------------------------------------------
    # PAGE 4: Tyre Brands (/tyre-brands)
    # -------------------------------------------------------------------------
    {
        'slug': 'tyre-brands',
        'title': {'en': 'Tyre Brands We Supply Across the UAE'},
        'seo_title': {'en': 'Tyre Brands in the UAE | 60+ Brands | TyresVision'},
        'meta_description': {'en': 'Compare 60+ tyre brands available in the UAE. Premium, mid-range and budget explained, with honest advice on which suits UAE heat and your mileage.'},
        'content': {'en': """
<div class="tv-page-lead">
  <p>With over 60 global tyre manufacturers in the UAE market, selecting the right brand can be overwhelming. Rather than pushing single-brand incentives, TyresVision categorizes tyre brands into three distinct tiers based on build quality, high-speed heat dissipation, wet braking capabilities, and actual value for UAE drivers.</p>
</div>

<div class="tv-cta-box">
  <div class="tv-cta-content">
    <h3>Compare tyre prices across 60+ brands</h3>
    <p>Tell us your size or car make on WhatsApp. We provide instant side-by-side quotes for premium, mid-range, and value options with official manufacturer warranty.</p>
  </div>
  <div class="tv-cta-actions">
    <a href="https://wa.me/971505069575?text=Hi%20TyresVision%2C%20please%20compare%20tyre%20brand%20prices%20for%20my%20size." target="_blank" rel="noopener" class="btn btn-wa">
      WhatsApp for Brand Comparison
    </a>
    <a href="tel:+971505069575" class="btn btn-call">+971 50 506 9575</a>
  </div>
</div>

<h2>The three tiers, and what your money buys you</h2>
<p>Understanding the fundamental difference between tiers prevents overspending on unnecessary performance or compromising safety:</p>
<ul>
  <li><strong>Premium Brands:</strong> Invest hundreds of millions in R&amp;D. Delivers the shortest braking distances, lowest road noise, and highest resilience against heat delamination on 140 km/h highway runs.</li>
  <li><strong>Mid-Range Brands:</strong> The sweet spot for 70% of UAE motorists. Typically delivers 85% to 90% of premium performance and lifespan at approximately 60% of the price.</li>
  <li><strong>Value &amp; Budget Brands:</strong> Sourced primarily from reputable Asian manufacturers with GCC standardization certification. Ideal for low-mileage city commuting, second cars, and commercial fleets on strict budgets.</li>
</ul>

<h2>Premium Tyre Brands</h2>
<div class="tv-grid-2">
  <div class="tv-card">
    <h3>Michelin</h3>
    <p>Renowned for class-leading tread life, acoustic refinement, and superior compound resilience in extreme heat. The Pilot Sport and Primacy lines are gold standards for luxury sedans and performance EVs.</p>
  </div>
  <div class="tv-card">
    <h3>Bridgestone</h3>
    <p>Dominant OE fitment across Land Cruiser and Patrol. Exceptional high-temperature heat dissipation and puncture-resistant carcasses (Dueler and Potenza series).</p>
  </div>
  <div class="tv-card">
    <h3>Continental</h3>
    <p>World-renowned for wet braking performance and precise steering response. The SportContact and UltraContact series offer exceptional balance for German luxury vehicles.</p>
  </div>
  <div class="tv-card">
    <h3>Pirelli</h3>
    <p>The choice for high-performance sports cars and high-end SUVs (P Zero and Scorpion families), offering uncompromising high-speed stability and grip.</p>
  </div>
  <div class="tv-card">
    <h3>Goodyear</h3>
    <p>Pioneers in high-mileage all-season rubber with the Eagle F1 and EfficientGrip series, offering quiet, durable touring performance.</p>
  </div>
  <div class="tv-card">
    <h3>Dunlop</h3>
    <p>Longstanding UAE legacy brand, particularly with Grandtrek 4x4 fitments that offer rugged sidewall strength across rocky desert and highway routes.</p>
  </div>
</div>

<h2>Mid-Range Tyre Brands &mdash; The Value Sweet Spot</h2>
<p>For drivers wanting dependable performance without premium price tags, our mid-range roster provides outstanding value:</p>
<ul>
  <li><strong>Hankook:</strong> OE supplier to Porsche, BMW, and Audi. Outstanding wet and dry braking with Ventus and Dynapro lines.</li>
  <li><strong>Yokohama:</strong> Japanese engineering powerhouse celebrated for durable Geolandar 4x4 tyres and whisper-quiet Advan luxury lines.</li>
  <li><strong>Toyo:</strong> Renowned for Open Country off-road durability and Proxes high-performance road grip.</li>
  <li><strong>Falken:</strong> Outstanding heat tolerance and long tread life at very competitive pricing (Azenis and Wildpeak series).</li>
  <li><strong>Kumho &amp; Nexen:</strong> Korean manufacturers offering comfortable, fuel-efficient OE fitments for Hyundai, Kia, and Japanese sedans.</li>
  <li><strong>BFGoodrich &amp; Cooper:</strong> American off-road legends built for extreme desert expeditions and heavy payload utility.</li>
</ul>

<h2>Value &amp; Budget Brands</h2>
<p>When budget is the priority, we stock rigorously tested value brands including <strong>Laufenn</strong> (Hankook subsidiary), <strong>Giti</strong>, <strong>Sumitomo</strong>, <strong>Zeetex</strong>, and <strong>Roadstone</strong>. Every budget tyre we supply carries verified GCC standardization (ESMA) certification with fresh production dates &mdash; never expired surplus stock.</p>

<h2>Which tyre brand is best for UAE heat?</h2>
<p><strong>Michelin and Bridgestone</strong> consistently demonstrate the lowest failure rates in sustained 50&deg;C summer highway conditions due to proprietary heat-dissipating bead constructions and high-temperature synthetic compounds. For mid-range budgets, <strong>Hankook and Yokohama</strong> deliver virtually identical heat endurance at a substantially lower price point.</p>

<h2>Brand Recommendations by Vehicle Type</h2>
<div class="table-responsive">
  <table class="tv-table">
    <thead>
      <tr>
        <th>Vehicle Category</th>
        <th>Recommended Brand Tier</th>
        <th>Top Brand Choices</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>City Hatchbacks (Yaris, Sunny, Picanto)</td>
        <td>Value to Mid-Range</td>
        <td>Nexen, Kumho, Zeetex, Falken</td>
      </tr>
      <tr>
        <td>Family Sedans (Camry, Accord, Altima)</td>
        <td>Mid-Range to Premium</td>
        <td>Hankook, Yokohama, Continental, Michelin</td>
      </tr>
      <tr>
        <td>Full-Size 4x4s (Land Cruiser, Patrol, Tahoe)</td>
        <td>Mid-Range to Premium</td>
        <td>Bridgestone, Dunlop, BFGoodrich, Michelin</td>
      </tr>
      <tr>
        <td>Electric Vehicles (Tesla, BYD, Porsche Taycan)</td>
        <td>Premium EV-Rated</td>
        <td>Michelin (Acoustic), Pirelli (Elect), Continental</td>
      </tr>
      <tr>
        <td>Commercial Vans &amp; Pickups</td>
        <td>Value to Mid-Range HD</td>
        <td>Toyo, Bridgestone, Giti, Sumitomo</td>
      </tr>
    </tbody>
  </table>
</div>

<h2>Are cheap tyres safe in the UAE?</h2>
<p><strong>Yes, provided they carry official GCC certification and date-fresh manufacturing.</strong> A budget tyre with a recent DOT date code and the correct speed and load rating is entirely safe for daily commuting. The real danger in the UAE comes from buying used tyres or stale stock stored in uncooled warehouses where rubber compounds have already begun hardening and micro-cracking.</p>

<p>Need specialist advice? See our dedicated guides for <a href="/off-road-4x4-tyres">off-road and 4x4 tyres</a>, dedicated <a href="/ev-tyres">EV tyres</a>, find your exact <a href="/tyre-sizes">tyre sizes</a>, or check recommended <a href="/tyres-by-car">tyres for your car model</a>.</p>

<h2>Tyre Brand FAQs</h2>
<div class="tv-faq-container">
  <div class="tv-faq-item">
    <button type="button" class="tv-faq-trigger">
      <span>What is the difference between Chinese and Japanese tyres?</span>
      <span class="tv-faq-icon">+</span>
    </button>
    <div class="tv-faq-panel">
      <p>Japanese tyres (Bridgestone, Yokohama, Toyo) feature advanced silica compounds, precision balancing, and quieter highway acoustics. Certified Chinese tyres (Giti, Zeetex) offer safe, dependable utility for city commuting at roughly 40% to 50% lower upfront cost.</p>
    </div>
  </div>

  <div class="tv-faq-item">
    <button type="button" class="tv-faq-trigger">
      <span>How do I check if my tyres are genuine GCC spec?</span>
      <span class="tv-faq-icon">+</span>
    </button>
    <div class="tv-faq-panel">
      <p>Genuine GCC tyres carry the GSO (Gulf Standardization Organization) certification mark embossed directly into the sidewall, confirming compound adaptation for high ambient heat.</p>
    </div>
  </div>

  <div class="tv-faq-item">
    <button type="button" class="tv-faq-trigger">
      <span>Is Michelin really worth the extra money over Hankook?</span>
      <span class="tv-faq-icon">+</span>
    </button>
    <div class="tv-faq-panel">
      <p>For high-mileage highway drivers and luxury vehicles doing 35,000+ km annually, Michelin's superior tread wear and acoustic silence justify the premium. For moderate city and highway use, Hankook delivers exceptional value and safety for hundreds of dirhams less.</p>
    </div>
  </div>
</div>
"""}
    },

    # -------------------------------------------------------------------------
    # PAGE 5: Tyre Sizes (/tyre-sizes)
    # -------------------------------------------------------------------------
    {
        'slug': 'tyre-sizes',
        'title': {'en': 'Tyre Sizes and Prices in the UAE'},
        'seo_title': {'en': 'Tyre Sizes in the UAE | Find Your Size | TyresVision'},
        'meta_description': {'en': 'Find your tyre size and see UAE prices. Popular sizes from 195/65 R15 to 305/40 R22, what each number means, and which cars use them.'},
        'content': {'en': """
<div class="tv-page-lead">
  <p>Understanding tyre size markings ensures you get the exact fitment intended by your vehicle's engineers. From compact 15-inch commuter fitments to heavy 22-inch SUV specifications, TyresVision stocks all popular UAE tyre sizes with date-fresh manufacturing and transparent pricing.</p>
</div>

<div class="tv-cta-box">
  <div class="tv-cta-content">
    <h3>Not sure what size your car takes?</h3>
    <p>Snap a quick photo of your tyre sidewall or tell us your car model on WhatsApp. We verify the correct size and send back immediate brand and price options.</p>
  </div>
  <div class="tv-cta-actions">
    <a href="https://wa.me/971505069575?text=Hi%20TyresVision%2C%20here%20is%20my%20tyre%20size%2C%20please%20send%20prices." target="_blank" rel="noopener" class="btn btn-wa">
      WhatsApp Your Tyre Size
    </a>
    <a href="tel:+971505069575" class="btn btn-call">+971 50 506 9575</a>
  </div>
</div>

<h2>How to read your tyre size: 235/55 R19 105W explained</h2>
<p>Every tyre sidewall features a standardised string of numbers and letters. For example, <strong>235/55 R19 105W</strong>:</p>
<div class="tv-grid-3">
  <div class="tv-card">
    <h3>235 &mdash; Width</h3>
    <p>The section width of the tyre in millimetres from sidewall to sidewall when mounted on the wheel.</p>
  </div>
  <div class="tv-card">
    <h3>55 &mdash; Aspect Ratio</h3>
    <p>The sidewall height expressed as a percentage of width (55% of 235 mm = ~129 mm height).</p>
  </div>
  <div class="tv-card">
    <h3>R19 &mdash; Rim Diameter</h3>
    <p><strong>R</strong> indicates radial ply construction; <strong>19</strong> is the wheel rim diameter in inches.</p>
  </div>
</div>
<div class="tv-grid-2" style="margin-top: 16px;">
  <div class="tv-card">
    <h3>105 &mdash; Load Index</h3>
    <p>A numerical code corresponding to the maximum weight the tyre can support (105 = 925 kg per tyre).</p>
  </div>
  <div class="tv-card">
    <h3>W &mdash; Speed Rating</h3>
    <p>The maximum safe speed the tyre can sustain under maximum load (W = up to 270 km/h).</p>
  </div>
</div>

<h2>Where to find your tyre size</h2>
<p>You can locate your vehicle's factory tyre specifications in two primary places:</p>
<ul>
  <li><strong>Tyre Sidewall:</strong> Molded directly into the outer rubber face of your current tyres.</li>
  <li><strong>Driver Door Pillar:</strong> The factory tyre placard sticker located inside the driver's door frame or fuel filler flap shows original sizes and recommended cold tyre inflation pressures.</li>
</ul>

<h2>Popular tyre sizes in the UAE and starting prices</h2>
<div class="table-responsive">
  <table class="tv-table">
    <thead>
      <tr>
        <th>Tyre Size</th>
        <th>Common Vehicles</th>
        <th>Starting Price (AED)</th>
        <th>Action</th>
      </tr>
    </thead>
    <tbody>
      <tr><td><strong>195/65 R15</strong></td><td>Toyota Corolla, Honda Civic, Hyundai Elantra</td><td>From 175 AED</td><td><a href="https://wa.me/971505069575?text=Price%20for%20195/65R15%20tyres" class="tv-table-link">Check Stock &rarr;</a></td></tr>
      <tr><td><strong>205/55 R16</strong></td><td>Golf, Corolla, Civic, Mazda 3</td><td>From 195 AED</td><td><a href="https://wa.me/971505069575?text=Price%20for%20205/55R16%20tyres" class="tv-table-link">Check Stock &rarr;</a></td></tr>
      <tr><td><strong>215/60 R16</strong></td><td>Toyota Camry, Nissan Altima</td><td>From 225 AED</td><td><a href="https://wa.me/971505069575?text=Price%20for%20215/60R16%20tyres" class="tv-table-link">Check Stock &rarr;</a></td></tr>
      <tr><td><strong>225/65 R17</strong></td><td>Toyota RAV4, Nissan X-Trail, Honda CR-V</td><td>From 260 AED</td><td><a href="https://wa.me/971505069575?text=Price%20for%20225/65R17%20tyres" class="tv-table-link">Check Stock &rarr;</a></td></tr>
      <tr><td><strong>265/65 R17</strong></td><td>Toyota Prado, Fortuner, Hilux, Pajero</td><td>From 340 AED</td><td><a href="https://wa.me/971505069575?text=Price%20for%20265/65R17%20tyres" class="tv-table-link">Check Stock &rarr;</a></td></tr>
      <tr><td><strong>235/45 R18</strong></td><td>Tesla Model 3, Camry Grande, Accord</td><td>From 290 AED</td><td><a href="https://wa.me/971505069575?text=Price%20for%20235/45R18%20tyres" class="tv-table-link">Check Stock &rarr;</a></td></tr>
      <tr><td><strong>265/60 R18</strong></td><td>Land Cruiser, Patrol, Pajero, Prado</td><td>From 375 AED</td><td><a href="https://wa.me/971505069575?text=Price%20for%20265/60R18%20tyres" class="tv-table-link">Check Stock &rarr;</a></td></tr>
      <tr><td><strong>285/60 R18</strong></td><td>Toyota Land Cruiser V8 / V6</td><td>From 420 AED</td><td><a href="https://wa.me/971505069575?text=Price%20for%20285/60R18%20tyres" class="tv-table-link">Check Stock &rarr;</a></td></tr>
      <tr><td><strong>235/55 R19</strong></td><td>Hyundai Santa Fe, Kia Sorento, Lexus RX</td><td>From 330 AED</td><td><a href="https://wa.me/971505069575?text=Price%20for%20235/55R19%20tyres" class="tv-table-link">Check Stock &rarr;</a></td></tr>
      <tr><td><strong>255/45 R19</strong></td><td>Tesla Model Y, Audi A6, BMW 5-Series</td><td>From 390 AED</td><td><a href="https://wa.me/971505069575?text=Price%20for%20255/45R19%20tyres" class="tv-table-link">Check Stock &rarr;</a></td></tr>
      <tr><td><strong>275/60 R20</strong></td><td>Nissan Patrol Platinum, Land Cruiser LC300</td><td>From 480 AED</td><td><a href="https://wa.me/971505069575?text=Price%20for%20275/60R20%20tyres" class="tv-table-link">Check Stock &rarr;</a></td></tr>
      <tr><td><strong>285/50 R20</strong></td><td>Land Cruiser LC200, Patrol, Lexus LX570</td><td>From 490 AED</td><td><a href="https://wa.me/971505069575?text=Price%20for%20285/50R20%20tyres" class="tv-table-link">Check Stock &rarr;</a></td></tr>
      <tr><td><strong>275/40 R21</strong></td><td>Range Rover Sport, BMW X5 / X6, Porsche Cayenne</td><td>From 580 AED</td><td><a href="https://wa.me/971505069575?text=Price%20for%20275/40R21%20tyres" class="tv-table-link">Check Stock &rarr;</a></td></tr>
      <tr><td><strong>285/45 R22</strong></td><td>Cadillac Escalade, GMC Yukon Denali, Tahoe</td><td>From 590 AED</td><td><a href="https://wa.me/971505069575?text=Price%20for%20285/45R22%20tyres" class="tv-table-link">Check Stock &rarr;</a></td></tr>
    </tbody>
  </table>
</div>

<h2>Load Index &amp; Speed Rating Reference Table</h2>
<div class="table-responsive">
  <table class="tv-table">
    <thead>
      <tr>
        <th>Load Index (kg per tyre)</th>
        <th>Speed Rating Symbol</th>
        <th>Maximum Speed (km/h)</th>
      </tr>
    </thead>
    <tbody>
      <tr><td><strong>91</strong> (615 kg) &mdash; Compact Sedans</td><td><strong>H</strong></td><td>210 km/h</td></tr>
      <tr><td><strong>95</strong> (690 kg) &mdash; Mid-Size Sedans</td><td><strong>V</strong></td><td>240 km/h</td></tr>
      <tr><td><strong>100</strong> (800 kg) &mdash; Crossovers</td><td><strong>W</strong></td><td>270 km/h</td></tr>
      <tr><td><strong>105</strong> (925 kg) &mdash; Premium EVs / Mid SUVs</td><td><strong>Y</strong></td><td>300 km/h</td></tr>
      <tr><td><strong>112&ndash;116</strong> (1,120&ndash;1,250 kg) &mdash; Full 4x4s</td><td><strong>(Y)</strong></td><td>Above 300 km/h</td></tr>
    </tbody>
  </table>
</div>

<h2>Can I fit a different size tyre on my car?</h2>
<p>We recommend sticking to manufacturer-approved sizes. Fitting an arbitrary size alters your rolling circumference, which introduces speedometer error, can trigger ABS/traction control faults, and may cause tyre rubbing against suspension struts at full steering lock. If you wish to upsize or downsize wheels, our technicians verify fitment clearance before installation.</p>

<p>Find fitment by looking up <a href="/tyres-by-car">tyres for your car model</a>, compare leading <a href="/tyre-brands">tyre brands</a>, explore dedicated <a href="/off-road-4x4-tyres">4x4 and SUV tyres</a>, or book our convenient doorstep <a href="/mobile-tyre-fitting">mobile tyre fitting</a> service.</p>

<h2>Tyre Size FAQs</h2>
<div class="tv-faq-container">
  <div class="tv-faq-item">
    <button type="button" class="tv-faq-trigger">
      <span>What is the four-digit DOT number on the sidewall?</span>
      <span class="tv-faq-icon">+</span>
    </button>
    <div class="tv-faq-panel">
      <p>The DOT code indicates the exact manufacturing date. For instance, &ldquo;2425&rdquo; means the tyre was built during the 24th week of 2025. In the UAE, tyres should be replaced after 5 years regardless of remaining tread.</p>
    </div>
  </div>

  <div class="tv-faq-item">
    <button type="button" class="tv-faq-trigger">
      <span>Can I have different tyre sizes on the front and rear?</span>
      <span class="tv-faq-icon">+</span>
    </button>
    <div class="tv-faq-panel">
      <p>Only if your vehicle came from the factory with a staggered fitment (common on sports cars like Porsche 911, BMW M models, and Mercedes-AMG). Front and rear sizes must always be identical on non-staggered vehicles.</p>
    </div>
  </div>
</div>
"""}
    },

    # -------------------------------------------------------------------------
    # PAGE 6: Tyres by Car Model (/tyres-by-car)
    # -------------------------------------------------------------------------
    {
        'slug': 'tyres-by-car',
        'title': {'en': 'Find Tyres for Your Car Model'},
        'seo_title': {'en': 'Tyres by Car Model in the UAE | TyresVision'},
        'meta_description': {'en': 'Find the right tyre size for your car. Land Cruiser, Patrol, Corolla, Camry, Civic, Tesla and more, with UAE prices and free fitting near you.'},
        'content': {'en': """
<div class="tv-page-lead">
  <p>Finding the right tyre size for your specific vehicle trim eliminates guesswork. TyresVision stocks verified factory tyre fitments for Japanese, Korean, American, German, and electric vehicles across the UAE, with free fitting at 350+ partner garages or convenient mobile fitting to your doorstep.</p>
</div>

<div class="tv-cta-box">
  <div class="tv-cta-content">
    <h3>Need tyres for your specific car model?</h3>
    <p>Tell us your vehicle make, year, and model on WhatsApp. We instantly match your factory size options across leading brands with free installation.</p>
  </div>
  <div class="tv-cta-actions">
    <a href="https://wa.me/971505069575?text=Hi%20TyresVision%2C%20what%20tyres%20fit%20my%20car%20model%3F" target="_blank" rel="noopener" class="btn btn-wa">
      WhatsApp Your Car Model
    </a>
    <a href="tel:+971505069575" class="btn btn-call">+971 50 506 9575</a>
  </div>
</div>

<h2>Tyre sizes by popular car models in the UAE</h2>
<div class="table-responsive">
  <table class="tv-table">
    <thead>
      <tr>
        <th>Make &amp; Model</th>
        <th>Common Factory Sizes</th>
        <th>Recommended Focus</th>
        <th>Action</th>
      </tr>
    </thead>
    <tbody>
      <tr><td>Toyota Corolla</td><td>195/65 R15, 205/55 R16</td><td>Fuel economy &amp; comfort</td><td><a href="https://wa.me/971505069575?text=Tyres%20for%20Toyota%20Corolla" class="tv-table-link">Get Quote &rarr;</a></td></tr>
      <tr><td>Toyota Camry</td><td>215/60 R16, 215/55 R17, 235/45 R18</td><td>Touring comfort &amp; low noise</td><td><a href="https://wa.me/971505069575?text=Tyres%20for%20Toyota%20Camry" class="tv-table-link">Get Quote &rarr;</a></td></tr>
      <tr><td>Nissan Sunny</td><td>185/65 R15, 195/55 R16</td><td>Value durability</td><td><a href="https://wa.me/971505069575?text=Tyres%20for%20Nissan%20Sunny" class="tv-table-link">Get Quote &rarr;</a></td></tr>
      <tr><td>Nissan Altima</td><td>215/60 R16, 215/55 R17, 235/40 R19</td><td>Highway touring comfort</td><td><a href="https://wa.me/971505069575?text=Tyres%20for%20Nissan%20Altima" class="tv-table-link">Get Quote &rarr;</a></td></tr>
      <tr><td>Honda Civic</td><td>215/55 R16, 215/50 R17</td><td>Responsive handling &amp; braking</td><td><a href="https://wa.me/971505069575?text=Tyres%20for%20Honda%20Civic" class="tv-table-link">Get Quote &rarr;</a></td></tr>
      <tr><td>Honda Accord</td><td>225/50 R17, 235/45 R18, 235/40 R19</td><td>Acoustic refinement</td><td><a href="https://wa.me/971505069575?text=Tyres%20for%20Honda%20Accord" class="tv-table-link">Get Quote &rarr;</a></td></tr>
      <tr><td>Hyundai Elantra</td><td>195/65 R15, 205/55 R16, 225/45 R17</td><td>Balanced ride &amp; long wear</td><td><a href="https://wa.me/971505069575?text=Tyres%20for%20Hyundai%20Elantra" class="tv-table-link">Get Quote &rarr;</a></td></tr>
      <tr><td>Kia Cerato / Forte</td><td>195/65 R15, 205/55 R16, 225/45 R17</td><td>Value &amp; comfort</td><td><a href="https://wa.me/971505069575?text=Tyres%20for%20Kia%20Cerato" class="tv-table-link">Get Quote &rarr;</a></td></tr>
      <tr><td>Toyota RAV4</td><td>225/65 R17, 225/60 R18, 235/55 R19</td><td>All-round highway crossover</td><td><a href="https://wa.me/971505069575?text=Tyres%20for%20Toyota%20RAV4" class="tv-table-link">Get Quote &rarr;</a></td></tr>
      <tr><td>Nissan X-Trail</td><td>225/65 R17, 225/60 R18, 235/55 R19</td><td>Family touring H/T</td><td><a href="https://wa.me/971505069575?text=Tyres%20for%20Nissan%20X-Trail" class="tv-table-link">Get Quote &rarr;</a></td></tr>
      <tr><td>Toyota Land Cruiser</td><td>285/65 R17, 285/60 R18, 275/60 R20</td><td>High load rating (H/T or A/T)</td><td><a href="https://wa.me/971505069575?text=Tyres%20for%20Land%20Cruiser" class="tv-table-link">Get Quote &rarr;</a></td></tr>
      <tr><td>Nissan Patrol</td><td>265/70 R18, 275/60 R20</td><td>Heavy SUV reinforced carcass</td><td><a href="https://wa.me/971505069575?text=Tyres%20for%20Nissan%20Patrol" class="tv-table-link">Get Quote &rarr;</a></td></tr>
      <tr><td>Toyota Prado</td><td>265/65 R17, 265/60 R18</td><td>Durable H/T or versatile A/T</td><td><a href="https://wa.me/971505069575?text=Tyres%20for%20Toyota%20Prado" class="tv-table-link">Get Quote &rarr;</a></td></tr>
      <tr><td>Mitsubishi Pajero</td><td>265/70 R16, 265/60 R18</td><td>Rugged highway touring</td><td><a href="https://wa.me/971505069575?text=Tyres%20for%20Mitsubishi%20Pajero" class="tv-table-link">Get Quote &rarr;</a></td></tr>
      <tr><td>Tesla Model 3</td><td>235/45 R18, 235/40 R19</td><td>Acoustic foam, EV rating</td><td><a href="https://wa.me/971505069575?text=Tyres%20for%20Tesla%20Model%203" class="tv-table-link">Get Quote &rarr;</a></td></tr>
      <tr><td>Tesla Model Y</td><td>255/45 R19, 255/40 R20</td><td>High load (XL/HL), EV compound</td><td><a href="https://wa.me/971505069575?text=Tyres%20for%20Tesla%20Model%20Y" class="tv-table-link">Get Quote &rarr;</a></td></tr>
      <tr><td>Ford Explorer</td><td>255/50 R20, 265/45 R21</td><td>Highway SUV quiet ride</td><td><a href="https://wa.me/971505069575?text=Tyres%20for%20Ford%20Explorer" class="tv-table-link">Get Quote &rarr;</a></td></tr>
      <tr><td>Chevrolet Tahoe</td><td>265/65 R18, 275/55 R20, 275/50 R22</td><td>High load touring stability</td><td><a href="https://wa.me/971505069575?text=Tyres%20for%20Chevrolet%20Tahoe" class="tv-table-link">Get Quote &rarr;</a></td></tr>
      <tr><td>BMW 5-Series / 7-Series</td><td>245/45 R18, 245/40 R19 (F), 275/35 R19 (R)</td><td>Run-flat (RFT) or high-perf touring</td><td><a href="https://wa.me/971505069575?text=Tyres%20for%20BMW" class="tv-table-link">Get Quote &rarr;</a></td></tr>
      <tr><td>Mercedes E-Class / S-Class</td><td>245/45 R18, 245/40 R19, 275/35 R19</td><td>MO / MOE acoustic luxury touring</td><td><a href="https://wa.me/971505069575?text=Tyres%20for%20Mercedes" class="tv-table-link">Get Quote &rarr;</a></td></tr>
    </tbody>
  </table>
</div>

<h2>Sedans and hatchbacks</h2>
<p>For high-volume commuter models like the Corolla, Civic, Sunny, and Camry, drivers should prioritize low rolling resistance, comfort, and consistent wet and dry braking. In this segment, mid-range brands such as Hankook, Yokohama, and Falken deliver the optimal sweet spot between purchase cost and longevity.</p>

<h2>SUVs and 4x4 vehicles</h2>
<p>Vehicles like the Land Cruiser, Patrol, and Prado require heavy-duty carcasses with load indexes of 112 or higher to withstand high-speed highway heat under full passenger load. For specialized sand and desert fitments, view our dedicated <a href="/off-road-4x4-tyres">off-road and 4x4 tyres</a> guide.</p>

<h2>Electric and hybrid models</h2>
<p>Electric cars demand reinforced XL or HL load ratings and low road-noise cavity foam to offset battery weight and protect cabin serenity. See our full guide on <a href="/ev-tyres">EV tyres</a>.</p>

<h2>Why the same car model can take two or three sizes</h2>
<p>Car manufacturers frequently specify different wheel and tyre packages depending on trim level (e.g. Base, Mid, or Full-Option / Sport). A Toyota Camry may run 16-inch wheels on base fleet trims, 17-inch on mid trims, and 18-inch on the Grande trim. Always check your physical tyre sidewall or learn <a href="/tyre-sizes">how to read your tyre size</a> before ordering.</p>

<p>Compare leading <a href="/tyre-brands">tyre brands</a> or order with free fitting at a centre near you.</p>

<h2>Car Model Tyre FAQs</h2>
<div class="tv-faq-container">
  <div class="tv-faq-item">
    <button type="button" class="tv-faq-trigger">
      <span>My car model isn't listed in the table. Can you still supply tyres?</span>
      <span class="tv-faq-icon">+</span>
    </button>
    <div class="tv-faq-panel">
      <p>Yes. We stock over 7,000 tyre sizes covering virtually every car, SUV, van, and light commercial vehicle sold in the UAE. Message your tyre size or registration on WhatsApp for immediate options.</p>
    </div>
  </div>

  <div class="tv-faq-item">
    <button type="button" class="tv-faq-trigger">
      <span>Do I have to use the exact size the vehicle came with from the factory?</span>
      <span class="tv-faq-icon">+</span>
    </button>
    <div class="tv-faq-panel">
      <p>We strongly recommend adhering to the original manufacturer tyre size to maintain accurate speedometer readings, correct gearbox shifting, and proper electronic stability control calibration.</p>
    </div>
  </div>
</div>
"""}
    },

    # -------------------------------------------------------------------------
    # PAGE 7: Tyre Shop Dubai (/tyre-shop-dubai)
    # -------------------------------------------------------------------------
    {
        'slug': 'tyre-shop-dubai',
        'title': {'en': 'Tyre Shop in Dubai — Tyres Fitted Near You'},
        'seo_title': {'en': 'Tyre Shop in Dubai | Free Fitting Near You | TyresVision'},
        'meta_description': {'en': 'Looking for a tyre shop in Dubai? 60+ brands delivered and fitted free at a centre near you, from Al Quoz to Deira. Send your size on WhatsApp.'},
        'content': {'en': """
<div class="tv-page-lead">
  <p>Looking for a dependable tyre shop in Dubai without driving around industrial areas or haggling over inconsistent quotes? TyresVision delivers 60+ authentic, date-fresh tyre brands with free installation across certified partner fitting garages throughout Dubai, or direct to your doorstep via our mobile service vans.</p>
</div>

<div class="tv-cta-box">
  <div class="tv-cta-content">
    <h3>Get instant Dubai tyre quotes on WhatsApp</h3>
    <p>Message your tyre size and preferred Dubai area. We confirm stock, transparent all-inclusive prices, and book your fitting slot within minutes.</p>
  </div>
  <div class="tv-cta-actions">
    <a href="https://wa.me/971505069575?text=Hi%20TyresVision%2C%20I%20need%20a%20tyre%20quote%20in%20Dubai." target="_blank" rel="noopener" class="btn btn-wa">
      WhatsApp Dubai Team
    </a>
    <a href="tel:+971505069575" class="btn btn-call">+971 50 506 9575</a>
  </div>
</div>

<h2>Tyre fitting centres across Dubai</h2>
<p>We partner with top-rated automotive service centres across key Dubai hubs, ensuring you never have to travel far for professional fitting, laser balancing, and alignment:</p>
<div class="tv-grid-3">
  <div class="tv-card">
    <h3>Central &amp; South Dubai</h3>
    <ul>
      <li>Al Quoz Industrial 1, 3 &amp; 4</li>
      <li>Al Barsha 1 &amp; Al Barsha South</li>
      <li>Jebel Ali Industrial Area</li>
      <li>Dubai Investment Park (DIP 1 &amp; 2)</li>
    </ul>
  </div>
  <div class="tv-card">
    <h3>New Dubai &amp; Marina</h3>
    <ul>
      <li>Dubai Marina &amp; JLT</li>
      <li>Umm Suqeim &amp; Al Sufouh</li>
      <li>Motor City &amp; Dubai Studio City</li>
      <li>Arabian Ranches &amp; Mudon</li>
    </ul>
  </div>
  <div class="tv-card">
    <h3>North &amp; East Dubai</h3>
    <ul>
      <li>Deira &amp; Port Saeed</li>
      <li>Al Qusais Industrial 1&ndash;5</li>
      <li>Rashidiya &amp; Umm Ramool</li>
      <li>Mirdif &amp; Silicon Oasis</li>
    </ul>
  </div>
</div>

<h2>Tyres delivered free to your nearest Dubai centre</h2>
<p>There is no delivery surcharge when fitting at any of our Dubai partner locations. We dispatch date-fresh tyres directly from temperature-controlled warehouses to the centre of your choice before your arrival, so your replacement takes under 45 minutes from start to finish.</p>

<h2>Or we come to you: Mobile tyre fitting in Dubai</h2>
<p>Short on time? Our specialized <a href="/mobile-tyre-fitting">mobile tyre fitting</a> vans bring the workshop directly to your villa driveway, office basement, or apartment parking bay across Dubai. Every van carries pneumatic bead breakers, dynamic balancing machines, and precision torque wrenches.</p>

<h2>What driving in Dubai does to your tyres</h2>
<p>Dubai driving is characterized by extreme dualities: prolonged stop-start traffic along Sheikh Zayed Road and Downtown, contrasted with sustained 120&ndash;140 km/h cruising across Emirates Road and Al Khail. During peak summer months, asphalt surface temperatures frequently reach 60&deg;C. Heat accelerates compound hardening and tyre pressure expansion. Checking pressures monthly and selecting tyres with high temperature ratings (Temperature A) is critical for preventing highway blowouts.</p>

<p>Compare leading <a href="/tyre-brands">tyre brands</a>, explore dedicated <a href="/ev-tyres">EV tyres</a>, or find your exact dimensions with our guide to <a href="/tyre-sizes">find your tyre size</a>.</p>

<h2>Dubai Tyre FAQs</h2>
<div class="tv-faq-container">
  <div class="tv-faq-item">
    <button type="button" class="tv-faq-trigger">
      <span>How quickly can I get tyres fitted in Dubai?</span>
      <span class="tv-faq-icon">+</span>
    </button>
    <div class="tv-faq-panel">
      <p>Most common sizes are in stock for same-day fitting across our Al Quoz, Al Barsha, and Al Qusais partner centres if booked before 2:00 PM. Mobile van fitting can often be arranged on the same day.</p>
    </div>
  </div>

  <div class="tv-faq-item">
    <button type="button" class="tv-faq-trigger">
      <span>Are fitting, balancing, and disposal included in Dubai prices?</span>
      <span class="tv-faq-icon">+</span>
    </button>
    <div class="tv-faq-panel">
      <p>Yes. Our quotes are all-inclusive with zero hidden costs &mdash; standard fitting, computerised wheel balancing, new standard valves, and environmental disposal of old tyres are all included.</p>
    </div>
  </div>

  <div class="tv-faq-item">
    <button type="button" class="tv-faq-trigger">
      <span>Can you fit tyres in my Dubai office or tower car park?</span>
      <span class="tv-faq-icon">+</span>
    </button>
    <div class="tv-faq-panel">
      <p>Yes, provided building security allows contractor access and the basement ceiling clears our van height (minimum 2.4 metres clearance). Open surface bays are always suitable.</p>
    </div>
  </div>
</div>
"""}
    },

    # -------------------------------------------------------------------------
    # PAGE 8: Tyre Shop Abu Dhabi (/tyre-shop-abu-dhabi)
    # -------------------------------------------------------------------------
    {
        'slug': 'tyre-shop-abu-dhabi',
        'title': {'en': 'Tyre Shop in Abu Dhabi — Tyres Fitted Near You'},
        'seo_title': {'en': 'Tyre Shop in Abu Dhabi | Free Fitting | TyresVision'},
        'meta_description': {'en': 'Looking for a tyre shop in Abu Dhabi? 60+ brands delivered and fitted free at a centre near you, from Musaffah to Khalifa City. WhatsApp your size.'},
        'content': {'en': """
<div class="tv-page-lead">
  <p>TyresVision provides motorists across Abu Dhabi with access to over 60 global tyre manufacturers at transparent, competitive prices. Choose between free installation at certified partner fitting centres from Musaffah to Al Bateen, or convenient doorstep mobile fitting throughout the capital.</p>
</div>

<div class="tv-cta-box">
  <div class="tv-cta-content">
    <h3>Get instant Abu Dhabi tyre quotes</h3>
    <p>Message your tyre size and location in Abu Dhabi on WhatsApp. We provide upfront pricing across leading brands with same-day fitting options.</p>
  </div>
  <div class="tv-cta-actions">
    <a href="https://wa.me/971505069575?text=Hi%20TyresVision%2C%20I%20need%20a%20tyre%20quote%20in%20Abu%20Dhabi." target="_blank" rel="noopener" class="btn btn-wa">
      WhatsApp Abu Dhabi Team
    </a>
    <a href="tel:+971505069575" class="btn btn-call">+971 50 506 9575</a>
  </div>
</div>

<h2>Tyre fitting centres across Abu Dhabi</h2>
<p>Our partner network spans the key automotive districts of the capital:</p>
<div class="tv-grid-2">
  <div class="tv-card">
    <h3>Musaffah Industrial Hubs</h3>
    <p>Certified partner garages located throughout Musaffah Industrial (M-9, M-14, M-37, M-40) equipped with heavy-duty mounting, 3D laser alignment, and commercial balancing machines.</p>
  </div>
  <div class="tv-card">
    <h3>Abu Dhabi City &amp; Islands</h3>
    <p>Convenient partner centres serving Al Bateen, Tourist Club Area, Al Reem Island, Yas Island, Khalifa City, and Al Raha Beach.</p>
  </div>
</div>

<h2>What driving in Abu Dhabi does to your tyres</h2>
<p>Abu Dhabi drivers frequently cover extended highway distances &mdash; such as the 140 km/h sustained cruise along the E11 towards Dubai, the Sheikh Khalifa highway to Yas Island, and long desert corridors out to Al Ain and the Western Region. Sustained high-speed driving under heavy vehicle loads (such as Nissan Patrol and Land Cruiser V8s) generates immense continuous thermal stress inside the tyre carcass. Maintaining correct cold tyre pressure and inspecting sidewalls for micro-cracks is vital for safety on Abu Dhabi roads.</p>

<h2>Or we come to you: Mobile tyre fitting in Abu Dhabi</h2>
<p>Avoid the drive down to Musaffah. Our <a href="/mobile-tyre-fitting">mobile tyre fitting</a> vans service residences and corporate parking bays across Khalifa City, Al Raha, Yas Island, and central Abu Dhabi, mounting and balancing new tyres while you remain in your home or office.</p>

<p>Need specialist fitment? View our dedicated guide to <a href="/off-road-4x4-tyres">4x4 and SUV tyres</a>, compare leading <a href="/tyre-brands">tyre brands</a>, or <a href="/tyre-sizes">find your tyre size</a>.</p>

<h2>Abu Dhabi Tyre FAQs</h2>
<div class="tv-faq-container">
  <div class="tv-faq-item">
    <button type="button" class="tv-faq-trigger">
      <span>Do you deliver tyres to Musaffah fitting centres?</span>
      <span class="tv-faq-icon">+</span>
    </button>
    <div class="tv-faq-panel">
      <p>Yes. We deliver directly to trusted partner fitting workshops throughout Musaffah with zero delivery charges.</p>
    </div>
  </div>

  <div class="tv-faq-item">
    <button type="button" class="tv-faq-trigger">
      <span>How does mobile tyre fitting work in Abu Dhabi?</span>
      <span class="tv-faq-icon">+</span>
    </button>
    <div class="tv-faq-panel">
      <p>Our van arrives at your villa or office location with your chosen tyres. We lift the vehicle on safety pads, demount the old tyres, fit and digitally balance the new ones, torque wheel nuts to factory spec, and take away your old tyres.</p>
    </div>
  </div>
</div>
"""}
    },

    # -------------------------------------------------------------------------
    # PAGE 9: Tyre Shop Sharjah (/tyre-shop-sharjah)
    # -------------------------------------------------------------------------
    {
        'slug': 'tyre-shop-sharjah',
        'title': {'en': 'Tyre Shop in Sharjah — Tyres Delivered and Fitted'},
        'seo_title': {'en': 'Tyre Shop in Sharjah | Free Fitting | TyresVision'},
        'meta_description': {'en': 'Tyre shop serving Sharjah. 60+ brands delivered free to a fitting centre near you in Al Nahda, Al Majaz or Muwaileh. WhatsApp your tyre size.'},
        'content': {'en': """
<div class="tv-page-lead">
  <p>TyresVision delivers brand-new, date-fresh tyres from over 60 global manufacturers across Sharjah. Skip the crowded industrial area queues &mdash; choose free fitting at certified partner garages near Al Majaz, Al Nahda, and Muwaileh, or arrange mobile fitting right at your door.</p>
</div>

<div class="tv-cta-box">
  <div class="tv-cta-content">
    <h3>Get instant Sharjah tyre quotes on WhatsApp</h3>
    <p>Share your tyre dimensions or car model. We confirm pricing, stock, and immediate fitting booking across Sharjah.</p>
  </div>
  <div class="tv-cta-actions">
    <a href="https://wa.me/971505069575?text=Hi%20TyresVision%2C%20I%20need%20a%20tyre%20quote%20in%20Sharjah." target="_blank" rel="noopener" class="btn btn-wa">
      WhatsApp Sharjah Team
    </a>
    <a href="tel:+971505069575" class="btn btn-call">+971 50 506 9575</a>
  </div>
</div>

<h2>Tyre fitting centres across Sharjah</h2>
<p>Our network covers primary residential and commercial districts throughout the emirate:</p>
<ul>
  <li><strong>Industrial Areas:</strong> Industrial Area 1, 2, 4, 10, 12, and 17.</li>
  <li><strong>Commuter &amp; Residential Belts:</strong> Al Nahda, Al Majaz (1, 2 &amp; 3), Al Khan, and Al Taawun.</li>
  <li><strong>University &amp; Airport Corridor:</strong> Muwaileh Commercial and University City vicinity.</li>
</ul>

<h2>What driving in Sharjah does to your tyres</h2>
<p>Many Sharjah motorists commute daily into Dubai via Al Ittihad Road or Mohammed Bin Zayed Road (E311). This involves prolonged bumper-to-bumper idling, frequent stop-start acceleration, and navigating countless speed humps and roundabouts. This driving profile creates distinctive outer shoulder scrubbing on front tyres. Quality mid-range brands (such as Hankook, Yokohama, and Kumho) offer reinforced shoulder blocks that resist uneven wear while remaining budget-friendly.</p>

<p>Need doorstep installation? Check our <a href="/mobile-tyre-fitting">mobile tyre fitting</a> service, compare <a href="/tyre-brands">budget and mid-range tyre brands</a>, or <a href="/tyre-sizes">find your tyre size</a>.</p>

<h2>Sharjah Tyre FAQs</h2>
<div class="tv-faq-container">
  <div class="tv-faq-item">
    <button type="button" class="tv-faq-trigger">
      <span>Are tyres fitted in Sharjah covered by warranty?</span>
      <span class="tv-faq-icon">+</span>
    </button>
    <div class="tv-faq-panel">
      <p>Yes. Every tyre supplied by TyresVision in Sharjah carries an official manufacturer warranty against manufacturing defects.</p>
    </div>
  </div>

  <div class="tv-faq-item">
    <button type="button" class="tv-faq-trigger">
      <span>Can you fit tyres in Sharjah on the same day?</span>
      <span class="tv-faq-icon">+</span>
    </button>
    <div class="tv-faq-panel">
      <p>Yes, orders placed on WhatsApp before 1:00 PM are typically delivered and fitted on the same day at our Sharjah partner centres.</p>
    </div>
  </div>
</div>
"""}
    },

    # -------------------------------------------------------------------------
    # PAGE 10: Tyre Shop Ajman (/tyre-shop-ajman)
    # -------------------------------------------------------------------------
    {
        'slug': 'tyre-shop-ajman',
        'title': {'en': 'Tyre Shop in Ajman — Tyres Delivered and Fitted'},
        'seo_title': {'en': 'Tyre Shop in Ajman | Tyres Delivered & Fitted | TyresVision'},
        'meta_description': {'en': 'Tyre shop serving Ajman. 60+ brands delivered free to a fitting centre near you in Al Nuaimiya, Al Jurf or Ajman city. WhatsApp your tyre size.'},
        'content': {'en': """
<div class="tv-page-lead">
  <p>TyresVision provides Ajman motorists with honest tyre recommendations, upfront pricing, and fast local fitting. We deliver 60+ brands free of charge to certified fitting centres in Al Jurf and Al Nuaimiya, or dispatch our mobile van to your home.</p>
</div>

<div class="tv-cta-box">
  <div class="tv-cta-content">
    <h3>Instant tyre quotes for Ajman drivers</h3>
    <p>Message your tyre size on WhatsApp for verified stock, competitive prices, and fast same-day fitting.</p>
  </div>
  <div class="tv-cta-actions">
    <a href="https://wa.me/971505069575?text=Hi%20TyresVision%2C%20I%20need%20a%20tyre%20quote%20in%20Ajman." target="_blank" rel="noopener" class="btn btn-wa">
      WhatsApp Ajman Team
    </a>
    <a href="tel:+971505069575" class="btn btn-call">+971 50 506 9575</a>
  </div>
</div>

<h2>Fast tyre delivery across Ajman</h2>
<p>Due to Ajman's compact layout, our logistics network delivers tyres from regional distribution hubs to partner fitting centres across Al Jurf Industrial, Al Nuaimiya, Al Rashidiya, and Al Rawda in under two hours.</p>

<h2>What driving in Ajman does to your tyres: Why age matters more than tread</h2>
<p>Many Ajman vehicles are used for local family errands, clocking relatively modest mileage (often 7,000 to 9,000 km per year). Under these conditions, tyre tread depth may appear deep and healthy after four years, but ambient heat and ozone exposure cause the rubber compound to oxidize and harden internally. In the UAE, tyres must be replaced when they reach <strong>5 years from their DOT manufacture date</strong>, regardless of remaining tread depth.</p>

<p>Book convenient <a href="/mobile-tyre-fitting">mobile tyre fitting</a> in Ajman, compare our roster of <a href="/tyre-brands">tyre brands</a>, or <a href="/tyre-sizes">find your tyre size</a>.</p>

<h2>Ajman Tyre FAQs</h2>
<div class="tv-faq-container">
  <div class="tv-faq-item">
    <button type="button" class="tv-faq-trigger">
      <span>Where are the tyre fitting centres in Ajman?</span>
      <span class="tv-faq-icon">+</span>
    </button>
    <div class="tv-faq-panel">
      <p>Our partner centres are conveniently located in Al Jurf Industrial Area and Al Nuaimiya, offering modern tyre mounting, balancing, and alignment bays.</p>
    </div>
  </div>

  <div class="tv-faq-item">
    <button type="button" class="tv-faq-trigger">
      <span>How do I check the manufacturing year of my tyres in Ajman?</span>
      <span class="tv-faq-icon">+</span>
    </button>
    <div class="tv-faq-panel">
      <p>Look for the 4-digit oval DOT stamp on the sidewall. The first two digits are the week, and the last two digits are the year (e.g. 1825 = 18th week of 2025).</p>
    </div>
  </div>
</div>
"""}
    },

    # -------------------------------------------------------------------------
    # PAGE 11: Tyre Shop Ras Al Khaimah (/tyre-shop-ras-al-khaimah)
    # -------------------------------------------------------------------------
    {
        'slug': 'tyre-shop-ras-al-khaimah',
        'title': {'en': 'Tyre Shop in Ras Al Khaimah'},
        'seo_title': {'en': 'Tyre Shop in Ras Al Khaimah | Tyres Fitted | TyresVision'},
        'meta_description': {'en': 'Tyre shop serving Ras Al Khaimah. 60+ brands delivered free to a fitting centre near you, from Al Nakheel to Al Hamra. WhatsApp your tyre size.'},
        'content': {'en': """
<div class="tv-page-lead">
  <p>From the urban coastal roads of Al Nakheel and Al Hamra to the steep mountain ascents of Jebel Jais, Ras Al Khaimah places unique physical demands on tyres. TyresVision supplies 60+ authentic tyre brands delivered free to certified fitting garages across RAK.</p>
</div>

<div class="tv-cta-box">
  <div class="tv-cta-content">
    <h3>Get RAK tyre pricing &amp; fitment options</h3>
    <p>Message your vehicle model or tyre size on WhatsApp for transparent quotes, reinforced sidewall options, and fast fitting in RAK.</p>
  </div>
  <div class="tv-cta-actions">
    <a href="https://wa.me/971505069575?text=Hi%20TyresVision%2C%20I%20need%20a%20tyre%20quote%20in%20Ras%20Al%20Khaimah." target="_blank" rel="noopener" class="btn btn-wa">
      WhatsApp RAK Team
    </a>
    <a href="tel:+971505069575" class="btn btn-call">+971 50 506 9575</a>
  </div>
</div>

<h2>Tyre fitting locations across Ras Al Khaimah</h2>
<p>Partner fitting centres serve key districts throughout RAK:</p>
<ul>
  <li>Al Nakheel &amp; Old RAK City</li>
  <li>Al Dhait &amp; Khuzam</li>
  <li>Al Hamra Village &amp; Mina Al Arab</li>
  <li>RAK Industrial &amp; Quarry zones</li>
  <li>Digdaga &amp; Airport Road</li>
</ul>

<h2>What driving in RAK does to your tyres: Mountain grades &amp; quarry roads</h2>
<p>Ras Al Khaimah is the UAE's mountain and quarry hub. Driving the Jebel Jais mountain corridor involves ascending over 1,900 metres, followed by sustained, brake-heavy descents where kinetic energy transfers into the wheel rims and tyre beads. Furthermore, heavy industrial transport traffic from quarries leads to gravel debris and sharp aggregates on secondary roads. Pickups, 4x4s, and utility vehicles in RAK require tyres with high load ratings and reinforced 3-ply sidewalls to guard against cuts and punctures.</p>

<p>Equip your rig with rugged <a href="/off-road-4x4-tyres">off-road and 4x4 tyres</a>, schedule convenient <a href="/mobile-tyre-fitting">mobile tyre fitting</a>, or <a href="/tyre-sizes">find your tyre size</a>.</p>

<h2>Ras Al Khaimah Tyre FAQs</h2>
<div class="tv-faq-container">
  <div class="tv-faq-item">
    <button type="button" class="tv-faq-trigger">
      <span>What tyres are best for Jebel Jais mountain driving?</span>
      <span class="tv-faq-icon">+</span>
    </button>
    <div class="tv-faq-panel">
      <p>Tyres with high thermal resistance ratings (Temperature A), stiff sidewalls, and reinforced carcass construction withstand the repeated braking heat and lateral cornering forces of mountain driving.</p>
    </div>
  </div>

  <div class="tv-faq-item">
    <button type="button" class="tv-faq-trigger">
      <span>Do you deliver commercial and pickup tyres to RAK?</span>
      <span class="tv-faq-icon">+</span>
    </button>
    <div class="tv-faq-panel">
      <p>Yes. We carry heavy-duty fitments for Toyota Hilux, Land Cruiser pickups, and commercial light trucks with free delivery to RAK fitting centres.</p>
    </div>
  </div>
</div>
"""}
    },

    # -------------------------------------------------------------------------
    # PAGE 12: Tyre Shop Fujairah (/tyre-shop-fujairah)
    # -------------------------------------------------------------------------
    {
        'slug': 'tyre-shop-fujairah',
        'title': {'en': 'Tyre Shop in Fujairah and the East Coast'},
        'seo_title': {'en': 'Tyre Shop in Fujairah | Tyres Fitted | TyresVision'},
        'meta_description': {'en': 'Tyre shop serving Fujairah and the east coast. 60+ brands delivered free to a fitting centre near you. Send your tyre size on WhatsApp.'},
        'content': {'en': """
<div class="tv-page-lead">
  <p>Serving Fujairah city, Dibba, Kalba, and Khor Fakkan, TyresVision provides east coast motorists with date-fresh tyres from 60+ manufacturers. Enjoy transparent pricing and free delivery to certified partner fitting garages across the east coast.</p>
</div>

<div class="tv-cta-box">
  <div class="tv-cta-content">
    <h3>Instant Fujairah &amp; East Coast tyre quotes</h3>
    <p>Message your tyre size and east coast location on WhatsApp. We provide instant brand recommendations and arrange fitting near you.</p>
  </div>
  <div class="tv-cta-actions">
    <a href="https://wa.me/971505069575?text=Hi%20TyresVision%2C%20I%20need%20a%20tyre%20quote%20in%20Fujairah." target="_blank" rel="noopener" class="btn btn-wa">
      WhatsApp Fujairah Team
    </a>
    <a href="tel:+971505069575" class="btn btn-call">+971 50 506 9575</a>
  </div>
</div>

<h2>East Coast fitting centre coverage</h2>
<p>Our partner network supports drivers throughout the eastern seaboard:</p>
<ul>
  <li>Fujairah City &amp; Port Marine Zone</li>
  <li>Dibba Al Fujairah</li>
  <li>Khor Fakkan &amp; Kalba</li>
  <li>Masafi mountain highway corridor</li>
</ul>

<h2>What driving on the East Coast does to your tyres</h2>
<p>East Coast driving combines steep mountain switchbacks through Masafi with elevated coastal humidity. The continuous cornering and elevation shifts cause tyres to wear more heavily on the outer shoulders than along the center tread. Routine tyre rotation and wheel alignment every 10,000 km are vital to maintain uniform grip and prolong tyre lifespan.</p>

<p>Explore durable <a href="/off-road-4x4-tyres">off-road and 4x4 tyres</a>, arrange <a href="/mobile-tyre-fitting">mobile tyre fitting</a>, or compare leading <a href="/tyre-brands">tyre brands</a>.</p>

<h2>Fujairah Tyre FAQs</h2>
<div class="tv-faq-container">
  <div class="tv-faq-item">
    <button type="button" class="tv-faq-trigger">
      <span>How long does delivery take to Fujairah?</span>
      <span class="tv-faq-icon">+</span>
    </button>
    <div class="tv-faq-panel">
      <p>Tyres are dispatched directly from central stock to Fujairah partner centres daily, usually arriving same-day or next-morning depending on order time.</p>
    </div>
  </div>

  <div class="tv-faq-item">
    <button type="button" class="tv-faq-trigger">
      <span>Do you service Khor Fakkan and Dibba?</span>
      <span class="tv-faq-icon">+</span>
    </button>
    <div class="tv-faq-panel">
      <p>Yes, we have certified partner workshops located across Khor Fakkan, Kalba, and Dibba Al Fujairah.</p>
    </div>
  </div>
</div>
"""}
    },

    # -------------------------------------------------------------------------
    # PAGE 13: Tyre Shop Umm Al Quwain (/tyre-shop-umm-al-quwain)
    # -------------------------------------------------------------------------
    {
        'slug': 'tyre-shop-umm-al-quwain',
        'title': {'en': 'Tyre Shop in Umm Al Quwain'},
        'seo_title': {'en': 'Tyre Shop in Umm Al Quwain | Tyres Fitted | TyresVision'},
        'meta_description': {'en': 'Tyre shop serving Umm Al Quwain. 60+ brands delivered free to a fitting centre near you, with mobile fitting on request. WhatsApp your size.'},
        'content': {'en': """
<div class="tv-page-lead">
  <p>TyresVision brings premium and mid-range tyres to Umm Al Quwain with complete transparency and zero hidden fees. Enjoy free delivery to our partner fitting garages in UAQ, or request mobile fitting delivered directly to your home.</p>
</div>

<div class="tv-cta-box">
  <div class="tv-cta-content">
    <h3>Get instant UAQ tyre quotes on WhatsApp</h3>
    <p>Message your tyre size on WhatsApp. We confirm exact pricing, GCC warranty, and arrange fast fitting in Umm Al Quwain.</p>
  </div>
  <div class="tv-cta-actions">
    <a href="https://wa.me/971505069575?text=Hi%20TyresVision%2C%20I%20need%20a%20tyre%20quote%20in%20UAQ." target="_blank" rel="noopener" class="btn btn-wa">
      WhatsApp UAQ Team
    </a>
    <a href="tel:+971505069575" class="btn btn-call">+971 50 506 9575</a>
  </div>
</div>

<h2>Areas served in Umm Al Quwain</h2>
<p>We serve motorists throughout the emirate:</p>
<ul>
  <li>UAQ Old Town &amp; City Centre</li>
  <li>Al Salamah &amp; Al Raas</li>
  <li>Al Humrah Industrial Area</li>
  <li>Falaj Al Mualla &amp; Al Rafaah</li>
</ul>

<h2>What driving in UAQ does to your tyres</h2>
<p>UAQ driving blends short neighborhood trips where tyres never fully warm up with high-speed 120 km/h highway runs down the E11 towards Sharjah and Dubai. Additionally, in desert and farm areas around Falaj Al Mualla, airborne sand and grit can work into tyre valve stems and bead seats, causing insidious slow pressure loss. We recommend checking cold tyre pressures every month and using metal or sealed valve caps.</p>

<p>Book convenient doorstep <a href="/mobile-tyre-fitting">mobile tyre fitting</a>, <a href="/tyre-sizes">find your tyre size</a>, or browse all <a href="/tyre-brands">tyre brands</a>.</p>

<h2>Umm Al Quwain Tyre FAQs</h2>
<div class="tv-faq-container">
  <div class="tv-faq-item">
    <button type="button" class="tv-faq-trigger">
      <span>Where can I get my tyres fitted in Umm Al Quwain?</span>
      <span class="tv-faq-icon">+</span>
    </button>
    <div class="tv-faq-panel">
      <p>We partner with leading workshops in Al Humrah Industrial Area and central UAQ, offering precision fitting and computer balancing.</p>
    </div>
  </div>

  <div class="tv-faq-item">
    <button type="button" class="tv-faq-trigger">
      <span>Is mobile fitting available in UAQ?</span>
      <span class="tv-faq-icon">+</span>
    </button>
    <div class="tv-faq-panel">
      <p>Yes, our mobile fitting vans service Umm Al Quwain residential and commercial areas upon request.</p>
    </div>
  </div>
</div>
"""}
    }
]


def seed_pages():
    conn = get_connection()
    cursor = conn.cursor()

    print(f"Starting seeding of {len(PAGES_DATA)} CMS pages...")

    for page_data in PAGES_DATA:
        slug = page_data['slug']
        title_json = json.dumps(page_data['title'])
        seo_title_json = json.dumps(page_data['seo_title'])
        meta_desc_json = json.dumps(page_data['meta_description'])
        content_json = json.dumps(page_data['content'])

        # Check if page already exists
        cursor.execute("SELECT id FROM pages WHERE slug = %s", (slug,))
        row = cursor.fetchone()

        if row:
            page_id = row['id'] if isinstance(row, dict) else row[0]
            cursor.execute("""
                UPDATE pages
                SET title = %s,
                    seo_title = %s,
                    meta_description = %s,
                    content = %s,
                    is_active = 1,
                    deleted_at = NULL,
                    updated_at = NOW()
                WHERE id = %s
            """, (title_json, seo_title_json, meta_desc_json, content_json, page_id))
            print(f"  [UPDATED] Page '{slug}' (ID {page_id})")
        else:
            cursor.execute("""
                INSERT INTO pages (slug, title, seo_title, meta_description, content, is_active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, 1, NOW(), NOW())
            """, (slug, title_json, seo_title_json, meta_desc_json, content_json))
            print(f"  [INSERTED] Page '{slug}'")

    conn.commit()
    conn.close()
    print("Seeding completed successfully!")


if __name__ == '__main__':
    seed_pages()
