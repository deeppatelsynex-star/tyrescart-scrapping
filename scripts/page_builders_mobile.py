"""
scripts/page_builders_mobile.py
Generates Page 1: Mobile Tyre Fitting in Dubai and Abu Dhabi (/mobile-tyre-fitting)
content for MySQL `pages` table storage.
Exact match to specifications in 'TyresVision-13-Page-Build-Plan 1.docx'.
"""

from page_shared_components import (
    build_hero_section,
    build_guarantees_strip,
    build_faq_section,
    build_bottom_cta,
    build_internal_links_card
)

def build_page_mobile():
    hero = build_hero_section(
        title="Mobile Tyre Fitting in Dubai and Abu Dhabi",
        eyebrow="DOORSTEP TYRE SERVICE",
        lead="Mobile tyre fitting at your home, office or car park across Dubai and Abu Dhabi. Send your tyre size and location on WhatsApp for a price in minutes.",
        wa_text="WhatsApp for Mobile Fitting",
        wa_msg="Hi TyresVision, I'd like mobile tyre fitting at my location.",
        breadcrumb_label="Mobile Tyre Fitting",
        default_emirate="Dubai"
    )

    faqs = [
        {
            "q": "How long does mobile tyre fitting take?",
            "a": "Most single-tyre replacements take 20 to 30 minutes once our van arrives. A full set of four tyres, including computerized wheel balancing and new valves, typically takes under an hour."
        },
        {
            "q": "Do I need to be physically present when the van arrives?",
            "a": "Not necessarily. As long as your car is unlocked (or keys left with building security) and our technicians have access to the vehicle, we can complete the fitting and send before/after photos with an online payment link."
        },
        {
            "q": "Can you fit tyres in my building or basement car park?",
            "a": "Yes! Our technicians operate in residential building car parks across Dubai and Abu Dhabi daily. Please check basement ceiling clearance in advance (our vans require 2.4m height clearance) and alert building security."
        },
        {
            "q": "Is dynamic wheel balancing included with mobile fitting?",
            "a": "Yes. Balancing is performed right on site using digital balancers installed inside each mobile workshop van. We never skip balancing."
        },
        {
            "q": "Do you remove and dispose of the old tyres?",
            "a": "Yes. Our mobile fitting vans have dedicated internal racks to take your old tyres away for eco-friendly recycling at certified UAE scrap rubber processing centres."
        },
        {
            "q": "What happens if I have a puncture on a major highway like Sheikh Zayed Road?",
            "a": "For safety reasons, mobile tyre fitting cannot be carried out on live highway shoulders like Sheikh Zayed Road or Mohammed Bin Zayed Road. We will arrange vehicle recovery to the nearest partner fitting centre instead."
        }
    ]

    return f"""{hero}

<!-- HOW MOBILE TYRE FITTING WORKS -->
<section class="tv-section-block" style="background:#ffffff;">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow">&mdash; FOUR SIMPLE STEPS &mdash;</span>
      <h2>How mobile tyre fitting works</h2>
      <p class="lead">From your initial WhatsApp message to fresh tyres mounted on your driveway in four effortless steps.</p>
    </div>

    <div class="grid g4" style="margin-top:28px;">
      <div class="card" style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:14px; padding:22px; text-align:center;">
        <div style="width:42px; height:42px; border-radius:50%; background:#2563FF; color:#fff; display:flex; align-items:center; justify-content:center; font-weight:800; margin:0 auto 12px auto;">1</div>
        <h3 style="font-size:1.05rem; font-weight:800; color:#0F172A; margin:0 0 8px 0;">Send Your Tyre Size</h3>
        <p style="font-size:0.86rem; color:#64748B; margin:0;">Snap a photo of your tyre sidewall or share your car make and model on WhatsApp.</p>
      </div>

      <div class="card" style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:14px; padding:22px; text-align:center;">
        <div style="width:42px; height:42px; border-radius:50%; background:#2563FF; color:#fff; display:flex; align-items:center; justify-content:center; font-weight:800; margin:0 auto 12px auto;">2</div>
        <h3 style="font-size:1.05rem; font-weight:800; color:#0F172A; margin:0 0 8px 0;">Send a Location Pin</h3>
        <p style="font-size:0.86rem; color:#64748B; margin:0;">Drop a WhatsApp pin for your villa driveway, office tower, or apartment car park.</p>
      </div>

      <div class="card" style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:14px; padding:22px; text-align:center;">
        <div style="width:42px; height:42px; border-radius:50%; background:#2563FF; color:#fff; display:flex; align-items:center; justify-content:center; font-weight:800; margin:0 auto 12px auto;">3</div>
        <h3 style="font-size:1.05rem; font-weight:800; color:#0F172A; margin:0 0 8px 0;">Confirmed Time Window</h3>
        <p style="font-size:0.86rem; color:#64748B; margin:0;">Our dispatcher confirms an exact arrival time before the van leaves the depot.</p>
      </div>

      <div class="card" style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:14px; padding:22px; text-align:center;">
        <div style="width:42px; height:42px; border-radius:50%; background:#2563FF; color:#fff; display:flex; align-items:center; justify-content:center; font-weight:800; margin:0 auto 12px auto;">4</div>
        <h3 style="font-size:1.05rem; font-weight:800; color:#0F172A; margin:0 0 8px 0;">Fitted on the Spot</h3>
        <p style="font-size:0.86rem; color:#64748B; margin:0;">Mounted, laser balanced, new valves installed, and old tyres taken away.</p>
      </div>
    </div>
  </div>
</section>

<!-- WHAT OUR VANS CARRY -->
<section class="tv-section-block" style="background:#F8FAFC;">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow">&mdash; THE TRUST SECTION &mdash;</span>
      <h2>What our vans carry</h2>
      <p class="lead">A complete commercial tyre workshop compact enough to fit inside your residential bay.</p>
    </div>

    <div class="grid g4" style="margin-top:28px;">
      <div class="card" style="background:#ffffff; border:1px solid #E2E8F0; border-radius:14px; padding:24px;">
        <h3 style="font-size:1.15rem; font-weight:800; color:#0F172A; margin:0 0 10px 0;">Heavy Pneumatic Tyre Changer</h3>
        <p style="font-size:0.9rem; line-height:1.6; color:#475569; margin:0;">Scratch-free demounting arms capable of handling 14-inch to 24-inch alloy rims and stiff run-flat sidewalls without wheel rim scuffing.</p>
      </div>
      <div class="card" style="background:#ffffff; border:1px solid #E2E8F0; border-radius:14px; padding:24px;">
        <h3 style="font-size:1.15rem; font-weight:800; color:#0F172A; margin:0 0 10px 0;">Computerized Wheel Balancer</h3>
        <p style="font-size:0.9rem; line-height:1.6; color:#475569; margin:0;">Digital balancing machine calibrated daily to eliminate steering vibrations up to 160 km/h. Balancing is always performed on site, never skipped.</p>
      </div>
      <div class="card" style="background:#ffffff; border:1px solid #E2E8F0; border-radius:14px; padding:24px;">
        <h3 style="font-size:1.15rem; font-weight:800; color:#0F172A; margin:0 0 10px 0;">Precision Torque Wrenches</h3>
        <p style="font-size:0.9rem; line-height:1.6; color:#475569; margin:0;">Every wheel nut is torqued by hand to exact manufacturer Newton-metre (Nm) specifications to protect wheel studs from stretching or shearing.</p>
      </div>
      <div class="card" style="background:#ffffff; border:1px solid #E2E8F0; border-radius:14px; padding:24px;">
        <h3 style="font-size:1.15rem; font-weight:800; color:#0F172A; margin:0 0 10px 0;">Valves &amp; Old Tyre Racks</h3>
        <p style="font-size:0.9rem; line-height:1.6; color:#475569; margin:0;">Fresh German valves fitted with every tyre, and dedicated storage compartments to haul your old worn tyres away for licensed eco-recycling.</p>
      </div>
    </div>
  </div>
</section>

<!-- WHAT MOBILE FITTING COSTS -->
<section class="tv-section-block" style="background:#ffffff;">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow">&mdash; HONEST &amp; PLAIN PRICING &mdash;</span>
      <h2>What mobile fitting costs</h2>
      <p class="lead">Say it plainly: fitting at a partner centre is free. Mobile fitting at your own location has a call-out fee, confirmed on WhatsApp before the van is sent. No surprise charges.</p>
    </div>

    <div class="grid g2" style="max-width:880px; margin:0 auto;">
      <div class="card" style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:16px; padding:28px; text-align:center;">
        <span style="font-weight:800; font-size:0.8rem; color:#2563FF; text-transform:uppercase;">Partner Centre Fitting</span>
        <h3 style="font-size:1.5rem; font-weight:800; color:#0F172A; margin:8px 0;">100% Free</h3>
        <p style="font-size:0.95rem; color:#475569; line-height:1.6; margin:0;">You only pay the tyre price. Mounting, 3D laser balancing, and new valves at our vetted workshops carry zero extra fee.</p>
      </div>

      <div class="card" style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:16px; padding:28px; text-align:center;">
        <span style="font-weight:800; font-size:0.8rem; color:#059669; text-transform:uppercase;">Doorstep Mobile Van</span>
        <h3 style="font-size:1.5rem; font-weight:800; color:#0F172A; margin:8px 0;">Tyre Cost + Modest Call-Out</h3>
        <p style="font-size:0.95rem; color:#475569; line-height:1.6; margin:0;">A transparent call-out fee is quoted and agreed upon on WhatsApp before dispatch. Absolutely no hidden fees upon van arrival.</p>
      </div>
    </div>
  </div>
</section>

<!-- WHERE WE CAN AND CAN'T FIT -->
<section class="tv-section-block" style="background:#F8FAFC;">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow">&mdash; THE HONESTY SECTION &mdash;</span>
      <h2>Where we can and can’t fit</h2>
      <p class="lead">We value your time and safety &mdash; here is what works and what does not.</p>
    </div>

    <div class="grid g2" style="max-width:920px; margin:0 auto;">
      <div class="card" style="background:#ffffff; border:1px solid #E2E8F0; border-radius:16px; padding:24px;">
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:12px;">
          <span style="background:#DCFCE7; color:#15803D; font-weight:800; font-size:0.8rem; padding:4px 10px; border-radius:100px;">YES</span>
          <h3 style="margin:0; font-size:1.15rem; font-weight:800; color:#0F172A;">Villa Driveways &amp; Private Parking</h3>
        </div>
        <p style="font-size:0.92rem; line-height:1.6; color:#475569; margin:0;">Our most common jobs across Arabian Ranches, Jumeirah, Khalifa City, and Yas Island. Plenty of level space to safely lift vehicles and work.</p>
      </div>

      <div class="card" style="background:#ffffff; border:1px solid #E2E8F0; border-radius:16px; padding:24px;">
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:12px;">
          <span style="background:#DCFCE7; color:#15803D; font-weight:800; font-size:0.8rem;">YES</span>
          <h3 style="margin:0; font-size:1.15rem; font-weight:800; color:#0F172A;">Apartment Car Parks (With Access)</h3>
        </div>
        <p style="font-size:0.92rem; line-height:1.6; color:#475569; margin:0;">We regularly service apartments in Downtown, Marina, and JLT, provided building security confirms visitor vehicle access in advance.</p>
      </div>

      <div class="card" style="background:#ffffff; border:1px solid #E2E8F0; border-radius:16px; padding:24px;">
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:12px;">
          <span style="background:#FEF3C7; color:#B45309; font-weight:800; font-size:0.8rem;">CHECK FIRST</span>
          <h3 style="margin:0; font-size:1.15rem; font-weight:800; color:#0F172A;">Height-Restricted Basements</h3>
        </div>
        <p style="font-size:0.92rem; line-height:1.6; color:#475569; margin:0;">Some mobile vans require 2.4 metres of vertical clearance. If your basement is low, tell us on WhatsApp and we can arrange alternate bay access.</p>
      </div>

      <div class="card" style="background:#ffffff; border:1px solid #E2E8F0; border-radius:16px; padding:24px;">
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:12px;">
          <span style="background:#FEE2E2; color:#B91C1C; font-weight:800; font-size:0.8rem;">NO</span>
          <h3 style="margin:0; font-size:1.15rem; font-weight:800; color:#0F172A;">Busy Highway Roadside (SZR, MBZ)</h3>
        </div>
        <p style="font-size:0.92rem; line-height:1.6; color:#475569; margin:0;">It is illegal and life-threatening to change tyres on fast 120 km/h highway shoulders. We coordinate vehicle recovery to a partner garage instead.</p>
      </div>
    </div>
  </div>
</section>

<!-- EVS, RUN-FLATS AND 4X4S AT YOUR LOCATION -->
<section class="tv-section-block" style="background:#ffffff;">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow">&mdash; SPECIALIZED VEHICLE FITMENT &mdash;</span>
      <h2>EVs, run-flats and 4x4s at your location</h2>
      <p class="lead">Certified equipment and trained technicians for delicate and heavy vehicles.</p>
    </div>

    <div class="card" style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:18px; padding:32px; max-width:860px; margin:0 auto; text-align:center;">
      <p style="font-size:1.02rem; line-height:1.75; color:#334155; margin:0 0 16px 0;">
        Electric vehicles must strictly be lifted on their marked chassis jacking points using protective rubber pucks &mdash; never on the battery casing or structural undertray. Our vans carry specialized EV lifting adapters and bead-assist arms to handle stiff run-flat tyres without wheel damage.
      </p>
      <p style="font-size:0.98rem; line-height:1.7; color:#475569; margin:0;">
        Learn more about specific fitments on our dedicated <a href="/ev-tyres" style="color:#2563FF; font-weight:700; text-decoration:underline;">EV and run-flat tyres</a> page, or verify your wheel dimensions to <a href="/tyre-sizes" style="color:#2563FF; font-weight:700; text-decoration:underline;">find your tyre size</a>.
      </p>
    </div>
  </div>
</section>

<!-- AREAS OUR VANS COVER -->
<section class="tv-section-block" style="background:#F8FAFC;">
  <div class="wrap">
    <div class="center tv-section-head">
      <span class="eyebrow">&mdash; COVERAGE ZONES &mdash;</span>
      <h2>Areas our vans cover</h2>
      <p class="lead">Serving drivers in need of <a href="/tyre-shop-dubai" style="color:#2563FF; font-weight:700; text-decoration:underline;">tyre fitting in Dubai</a> and <a href="/tyre-shop-abu-dhabi" style="color:#2563FF; font-weight:700; text-decoration:underline;">tyre fitting in Abu Dhabi</a>.</p>
    </div>

    <div class="grid g3" style="margin-top:28px;">
      <div class="card" style="background:#ffffff; border:1px solid #E2E8F0; border-radius:14px; padding:24px;">
        <h3 style="font-size:1.2rem; font-weight:800; color:#0F172A; margin:0 0 12px 0;">Dubai Coverage</h3>
        <p style="font-size:0.9rem; line-height:1.65; color:#475569; margin:0;">Downtown, Business Bay, Dubai Marina, JLT, JBR, Palm Jumeirah, Umm Suqeim, Arabian Ranches, Motor City, Dubai Hills, Mirdif, and Silicon Oasis.</p>
      </div>

      <div class="card" style="background:#ffffff; border:1px solid #E2E8F0; border-radius:14px; padding:24px;">
        <h3 style="font-size:1.2rem; font-weight:800; color:#0F172A; margin:0 0 12px 0;">Abu Dhabi Coverage</h3>
        <p style="font-size:0.9rem; line-height:1.65; color:#475569; margin:0;">Al Reem Island, Al Maryah Island, Khalifa City, Al Raha Beach, Yas Island, Saadiyat Island, Mohamed Bin Zayed City, and central Abu Dhabi Island.</p>
      </div>

      <div class="card" style="background:#ffffff; border:1px solid #E2E8F0; border-radius:14px; padding:24px;">
        <h3 style="font-size:1.2rem; font-weight:800; color:#0F172A; margin:0 0 12px 0;">Northern Emirates</h3>
        <p style="font-size:0.9rem; line-height:1.65; color:#475569; margin:0;">Mobile fitting in Sharjah is available upon request. In Ajman, RAK, Fujairah, and UAQ, we direct drivers to our convenient local partner fitting centres.</p>
      </div>
    </div>
  </div>
</section>

<!-- MOBILE FITTING FAQS -->
{build_faq_section("Mobile fitting FAQs", faqs, eyebrow="DOORSTEP SERVICE FAQS")}

<!-- BOTTOM CTA -->
{build_bottom_cta(
    heading="Book Doorstep Mobile Tyre Fitting Today",
    lead="Send your tyre size and location pin on WhatsApp. Our dispatchers confirm a quick arrival window and clear upfront pricing.",
    wa_msg="Hi TyresVision, I'd like mobile tyre fitting at my location.",
    wa_btn_text="WhatsApp for Mobile Fitting"
)}
"""
