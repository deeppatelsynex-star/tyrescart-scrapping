"""
scripts/seed_page_sections.py
Seeds comprehensive, modular, high-converting page sections for all 12 CMS pages
(Pages 2 to 13 from TyresVision-13-Page-Build-Plan 1.docx) into the MySQL `page_sections` table.
Each page gets modular sections (Hero, Features, Pricing/Fitment Table, Advice/Coverage, FAQ, CTA).
Safe to re-run (clears existing sections for these 12 slugs before inserting).
"""

import os
import sys
import json

# Setup paths
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app'))

from db import get_connection

SECTIONS_DATA = [
    # =========================================================================
    # PAGE 2: EV Tyres (/ev-tyres)
    # =========================================================================
    {
        'page_slug': 'ev-tyres',
        'sections': [
            {
                'section_type': 'hero',
                'sort_order': 1,
                'section_title': {'en': 'EV & Hybrid Tyres in Dubai, Abu Dhabi & UAE'},
                'section_subtitle': {'en': 'ELECTRIC MOBILITY SPECIALISTS'},
                'content': {'en': 'High-load rated (HL/XL), low rolling resistance tyres engineered for instantaneous electric torque and quiet cabin acoustics. Fitted free at a partner centre or doorstep mobile van across the UAE.'},
                'button_text': {'en': 'WhatsApp for EV Tyre Quote'},
                'button_url': 'https://wa.me/971505069575?text=Hi%20TyresVision%2C%20I%20need%20a%20tyre%20quote%20for%20my%20electric%20car.',
                'section_data': {
                    'badges': [
                        {'title': 'HL & XL High Load Rated'},
                        {'title': 'Acoustic Foam Sound-Dampening'},
                        {'title': 'Low Rolling Resistance (Longer Range)'},
                        {'title': 'Safe Doorstep Mobile Jacking'}
                    ],
                    'phone': '+971505069575',
                    'phone_display': '+971 50 506 9575'
                }
            },
            {
                'section_type': 'features',
                'sort_order': 2,
                'section_title': {'en': 'Why Electric Cars Need Dedicated EV Tyres'},
                'section_subtitle': {'en': 'ENGINEERING SPECIFICATIONS'},
                'content': {'en': 'Instantaneous torque and 20% to 30% heavier curb weights subject rubber to severe shear stress. In UAE tarmac heat exceeding 55°C, standard passenger tyres wear out up to 40% faster.'},
                'section_data': {
                    'cards': [
                        {
                            'icon': 'shield',
                            'title': 'Stiffer Sidewall & HL Casing',
                            'description': 'Engineered to handle 2,000–2,600 kg battery curb weight without tread squirm, excessive deflection, or dangerous shoulder scrubbing.'
                        },
                        {
                            'icon': 'zap',
                            'title': 'Acoustic Cavity Dampening Foam',
                            'description': 'With no combustion engine sound, tyre cavity resonance dominates the cabin. Polyurethane inner foam absorbs road rumble for silent driving.'
                        },
                        {
                            'icon': 'truck',
                            'title': 'Range-Preserving Silica Compounds',
                            'description': 'Advanced low rolling resistance compounds reduce kinetic energy loss per rotation, safeguarding battery range by up to 7% to 10%.'
                        },
                        {
                            'icon': 'clock',
                            'title': 'Certified Mobile Jacking Pucks',
                            'description': 'Our mobile vans carry dedicated vehicle-specific rubber lifting pucks to protect underbody high-voltage battery trays during fitting.'
                        }
                    ]
                }
            },
            {
                'section_type': 'price_table',
                'sort_order': 3,
                'section_title': {'en': 'Tyres by Electric & Hybrid Model'},
                'section_subtitle': {'en': 'POPULAR UAE FITMENTS & PRICING'},
                'content': {'en': 'Factory dimensions, recommended load indexes, and starting tyre prices for top electric and hybrid vehicles in Dubai and Abu Dhabi.'},
                'section_data': {
                    'col1_header': 'Vehicle Model',
                    'col2_header': 'Common Tyre Sizes',
                    'col3_header': 'Budget From',
                    'col4_header': 'Mid-Range',
                    'col5_header': 'Premium EV',
                    'value_cards': [
                        {'title': '100% GCC Specification', 'subtitle': 'Certified for extreme 55°C tarmac heat'},
                        {'title': 'Free Fitting & Balancing', 'subtitle': 'Valves and old-tyre disposal included'},
                        {'title': 'Official Manufacturer Warranty', 'subtitle': 'Direct sourced from authorized distributors'},
                        {'title': 'Same-Day Mobile Van Dispatch', 'subtitle': 'Doorstep fitting at villa, office, or apartment'}
                    ],
                    'rows': [
                        {'size': 'Tesla Model 3', 'common_on': {'en': '235/45 R18, 235/40 R19, 235/35 R20'}, 'budget': 'AED 295', 'mid_range': 'AED 490', 'premium': 'AED 780'},
                        {'size': 'Tesla Model Y', 'common_on': {'en': '255/45 R19, 255/40 R20, 275/35 R21'}, 'budget': 'AED 340', 'mid_range': 'AED 560', 'premium': 'AED 890'},
                        {'size': 'BYD Atto 3 / Seal', 'common_on': {'en': '215/60 R17, 235/50 R18, 235/45 R19'}, 'budget': 'AED 260', 'mid_range': 'AED 420', 'premium': 'AED 640'},
                        {'size': 'Hyundai Ioniq 5 / Kia EV6', 'common_on': {'en': '235/55 R19, 255/45 R20'}, 'budget': 'AED 320', 'mid_range': 'AED 510', 'premium': 'AED 790'},
                        {'size': 'Mercedes EQE / EQS', 'common_on': {'en': '255/45 R19, 265/40 R20, 265/35 R21'}, 'budget': 'AED 480', 'mid_range': 'AED 740', 'premium': 'AED 1,180'},
                        {'size': 'Audi e-tron / Q8 e-tron', 'common_on': {'en': '255/55 R19, 265/45 R21, 285/40 R22'}, 'budget': 'AED 490', 'mid_range': 'AED 760', 'premium': 'AED 1,220'},
                        {'size': 'Toyota / Lexus Hybrids', 'common_on': {'en': '215/55 R17, 235/45 R18'}, 'budget': 'AED 210', 'mid_range': 'AED 340', 'premium': 'AED 520'},
                        {'size': 'Polestar 2', 'common_on': {'en': '245/45 R19, 245/40 R20'}, 'budget': 'AED 380', 'mid_range': 'AED 590', 'premium': 'AED 890'}
                    ]
                }
            },
            {
                'section_type': 'advice',
                'sort_order': 4,
                'section_title': {'en': 'Crucial Advice for UAE Electric Car Drivers'},
                'section_subtitle': {'en': 'SAFETY & MAINTENANCE'},
                'content': {'en': 'Key technical guidelines to maximize tyre lifespan and protect your battery range across Dubai and Abu Dhabi.'},
                'section_data': {
                    'cards': [
                        {
                            'icon': 'shield',
                            'title': {'en': 'Check the "HL" (High Load) Rating'},
                            'description': {'en': 'If your door placard specifies an HL rating, never fit standard SL/XL tyres. Under-rated tyres under high summer temperatures build internal heat that causes structural delamination.'}
                        },
                        {
                            'icon': 'clock',
                            'title': {'en': 'Rotate Tyres Every 8,000 to 10,000 KM'},
                            'description': {'en': 'Instantaneous electric motor torque wears drive-axle tyres twice as fast as trailing tyres. Routine rotation equalizes wear across all four corners.'}
                        },
                        {
                            'icon': 'dollar',
                            'title': {'en': 'Run-Flat vs Normal Tyre Swaps'},
                            'description': {'en': 'You can switch run-flats to conventional tyres for a softer ride, but always carry a 12V portable air compressor and emergency sealant kit since most EVs omit spare wheels.'}
                        }
                    ]
                }
            },
            {
                'section_type': 'faq',
                'sort_order': 5,
                'section_title': {'en': 'Frequently Asked Questions About EV Tyres in the UAE'},
                'section_subtitle': {'en': 'COMMON QUERIES'},
                'content': {'en': 'Answers to frequently asked questions about electric vehicle tyres, range impact, and mobile van replacement.'},
                'section_data': {
                    'faqs': [
                        {
                            'question': {'en': 'Do EV tyres really make a difference to battery range?'},
                            'answer': {'en': 'Yes. Independent tests demonstrate that low rolling resistance EV tyres improve driving range by 7% to 10% compared to standard generic tyres, equating to an extra 35–50 km per full charge on a 500 km battery.'}
                        },
                        {
                            'question': {'en': 'Can I put normal tyres on my Tesla or BYD?'},
                            'answer': {'en': 'Technically yes, provided the load and speed ratings match. However, normal tyres will wear up to 40% faster under electric torque, generate noticeable cabin road noise, and slightly decrease battery range.'}
                        },
                        {
                            'question': {'en': 'Why do EV tyres wear out faster than petrol car tyres?'},
                            'answer': {'en': 'Two main reasons: electric vehicles weigh 20% to 30% more because of heavy battery packs, and electric motors deliver 100% torque instantly from 0 RPM, putting intense friction on the tyre contact patch.'}
                        },
                        {
                            'question': {'en': 'Can run-flat tyres on EVs and luxury cars be repaired?'},
                            'answer': {'en': 'Generally no. Once driven with zero or low pressure, the internal sidewall structure suffers severe heat degradation that compromises safety. Manufacturers mandate replacement.'}
                        },
                        {
                            'question': {'en': 'Can your mobile fitting van change EV tyres at my villa or office?'},
                            'answer': {'en': 'Yes. Our mobile vans are fully equipped with low-clearance jacks, vehicle-specific rubber lifting pucks, and precision digital balancing machines to fit tyres at your home or workplace safely.'}
                        }
                    ]
                }
            },
            {
                'section_type': 'cta',
                'sort_order': 6,
                'section_title': {'en': 'Ready to Fit the Right Tyres on Your EV?'},
                'content': {'en': 'Send your tyre size or car model on WhatsApp. Our specialists confirm EV-rated options and book free mobile van fitting today.'},
                'button_text': {'en': 'WhatsApp for EV Tyre Quote'},
                'button_url': 'https://wa.me/971505069575?text=Hi%20TyresVision%2C%20I%20need%20a%20tyre%20quote%20for%20my%20electric%20car.',
                'section_data': {
                    'call_button_text': {'en': 'Call +971 50 506 9575'},
                    'call_button_url': 'tel:+971505069575',
                    'footer_note': {'en': 'Mobile fitting vans and partner workshops active daily across Dubai, Abu Dhabi, and all Emirates.'}
                }
            }
        ]
    },

    # =========================================================================
    # PAGE 3: 4x4 & Off-Road Tyres (/off-road-4x4-tyres)
    # =========================================================================
    {
        'page_slug': 'off-road-4x4-tyres',
        'sections': [
            {
                'section_type': 'hero',
                'sort_order': 1,
                'section_title': {'en': '4x4 & Off-Road Tyres in Dubai, Abu Dhabi & UAE'},
                'section_subtitle': {'en': 'DESERT DUNES & HIGHWAY PERFORMANCE'},
                'content': {'en': 'All-Terrain (A/T), Mud-Terrain (M/T), and Highway-Terrain (H/T) tyres engineered for desert dune bashing, wadi rock trails, and smooth high-speed highway cruising. 100% GCC spec with free local fitting.'},
                'button_text': {'en': 'WhatsApp for 4x4 Tyre Quote'},
                'button_url': 'https://wa.me/971505069575?text=Hi%20TyresVision%2C%20I%20need%20a%20tyre%20quote%20for%20my%204x4.',
                'section_data': {
                    'badges': [
                        {'title': 'Dune Bashing Sand Grip'},
                        {'title': 'Reinforced 3-Ply Sidewalls'},
                        {'title': 'BFGoodrich, Cooper, Michelin & Falken'},
                        {'title': 'Mobile Van or Workshop Fitting'}
                    ],
                    'phone': '+971505069575',
                    'phone_display': '+971 50 506 9575'
                }
            },
            {
                'section_type': 'features',
                'sort_order': 2,
                'section_title': {'en': 'AT vs MT vs HT: Which Tyre Fits Your UAE Driving?'},
                'section_subtitle': {'en': 'TERRAIN COMPARISON'},
                'content': {'en': 'Choosing the right tyre pattern ensures high desert capability without sacrificing highway refinement or fuel economy.'},
                'section_data': {
                    'cards': [
                        {
                            'icon': 'truck',
                            'title': 'All-Terrain (A/T) — The Best All-Rounder',
                            'description': '70% road / 30% off-road balance. Interlocking tread blocks float seamlessly over soft sand dunes while remaining quiet on Sheikh Zayed Road.'
                        },
                        {
                            'icon': 'shield',
                            'title': 'Mud-Terrain (M/T) — Maximum Trail Grip',
                            'description': 'Deep aggressive tread voids and armored sidewalls designed for rocky wadi climbs and extreme off-camber trails. Louder on pavement.'
                        },
                        {
                            'icon': 'zap',
                            'title': 'Highway-Terrain (H/T) — Luxury Comfort',
                            'description': 'Optimized for high-speed highway stability, wet grip, and lowest rolling noise. Ideal for daily commuter SUVs and luxury cruisers.'
                        }
                    ]
                }
            },
            {
                'section_type': 'price_table',
                'sort_order': 3,
                'section_title': {'en': 'Tyres by 4x4 & SUV Model'},
                'section_subtitle': {'en': 'POPULAR UAE 4WD VEHICLES'},
                'content': {'en': 'Factory dimensions and starting prices for the most trusted 4x4s and off-roaders driven across the Emirates.'},
                'section_data': {
                    'col1_header': '4x4 Model',
                    'col2_header': 'Common Tyre Sizes',
                    'col3_header': 'Budget From',
                    'col4_header': 'Mid-Range A/T',
                    'col5_header': 'Premium Off-Road',
                    'value_cards': [
                        {'title': 'Fresh Production Dates', 'subtitle': 'Guaranteed date-fresh DOT codes direct from importers'},
                        {'title': 'Free 3D Balancing & Fitting', 'subtitle': 'Laser balanced to eliminate steering wobble'},
                        {'title': 'Desert Deflation Capable', 'subtitle': 'Tested down to 12 PSI on soft desert sand'},
                        {'title': 'Nationwide Mobile Fitting', 'subtitle': 'We fit at your home, garage, or desert staging area'}
                    ],
                    'rows': [
                        {'size': 'Toyota Land Cruiser (LC300 / LC200)', 'common_on': {'en': '265/65 R18, 265/55 R20, 285/60 R18'}, 'budget': 'AED 380', 'mid_range': 'AED 590', 'premium': 'AED 860'},
                        {'size': 'Nissan Patrol (Y62 / Super Safari)', 'common_on': {'en': '265/70 R18, 275/60 R20, 285/70 R17'}, 'budget': 'AED 390', 'mid_range': 'AED 610', 'premium': 'AED 890'},
                        {'size': 'Toyota Prado & Fortuner', 'common_on': {'en': '265/65 R17, 265/60 R18'}, 'budget': 'AED 310', 'mid_range': 'AED 470', 'premium': 'AED 680'},
                        {'size': 'Jeep Wrangler (Rubicon / Sahara)', 'common_on': {'en': '255/75 R17, 285/70 R17, 33x12.5 R17'}, 'budget': 'AED 420', 'mid_range': 'AED 680', 'premium': 'AED 990'},
                        {'size': 'Land Rover Defender (90 / 110)', 'common_on': {'en': '255/65 R19, 255/60 R20, 275/45 R22'}, 'budget': 'AED 540', 'mid_range': 'AED 820', 'premium': 'AED 1,290'},
                        {'size': 'Ford F-150 Raptor & Ranger', 'common_on': {'en': '315/70 R17, 285/70 R17'}, 'budget': 'AED 580', 'mid_range': 'AED 860', 'premium': 'AED 1,320'},
                        {'size': 'Suzuki Jimny', 'common_on': {'en': '195/80 R15, 215/75 R15'}, 'budget': 'AED 220', 'mid_range': 'AED 350', 'premium': 'AED 540'},
                        {'size': 'Mitsubishi Pajero', 'common_on': {'en': '265/65 R17, 265/60 R18'}, 'budget': 'AED 290', 'mid_range': 'AED 450', 'premium': 'AED 660'}
                    ]
                }
            },
            {
                'section_type': 'advice',
                'sort_order': 4,
                'section_title': {'en': 'Dune Bashing, Deflating & Desert Driving Tips'},
                'section_subtitle': {'en': 'EXPERT OFF-ROAD KNOWLEDGE'},
                'content': {'en': 'Crucial tyre pressure and safety rules for tackling UAE dunes without de-beading or overheating your rubber.'},
                'section_data': {
                    'cards': [
                        {
                            'icon': 'clock',
                            'title': {'en': 'Deflate to 12–15 PSI on Sand'},
                            'description': {'en': 'Dropping tyre pressure from 35 PSI to 14 PSI expands the contact patch by over 200%, allowing your 4x4 to "float" across soft red sand without sinking.'}
                        },
                        {
                            'icon': 'zap',
                            'title': {'en': 'Inflate Before Hitting the Tarmac'},
                            'description': {'en': 'Never drive faster than 40 km/h on deflated tyres. High highway speeds on low pressure causes rapid sidewall heat build-up and blowout danger.'}
                        },
                        {
                            'icon': 'shield',
                            'title': {'en': 'Beadlocks vs Standard Rims'},
                            'description': {'en': 'Beadlock rims clamp the tyre bead mechanically, enabling extreme deflation down to 6–8 PSI without risk of the tyre popping off the rim in sharp dune bowls.'}
                        }
                    ]
                }
            },
            {
                'section_type': 'faq',
                'sort_order': 5,
                'section_title': {'en': 'Frequently Asked Questions: 4x4 & Off-Road Tyres'},
                'section_subtitle': {'en': 'OFF-ROAD FAQ'},
                'content': {'en': 'Essential questions answered on sand deflation, tyre sizes, and balancing.'},
                'section_data': {
                    'faqs': [
                        {
                            'question': {'en': 'What is the best tyre pressure for dune bashing in Dubai?'},
                            'answer': {'en': 'For standard 4x4 tyres on soft sand, 12 to 15 PSI is ideal. For heavier SUVs like a Nissan Patrol Y62, aim for 14–15 PSI. Always re-inflate to manufacturer pressure (32–35 PSI) before returning to high-speed tarmac.'}
                        },
                        {
                            'question': {'en': 'Will All-Terrain tyres make my 4x4 noisy on the highway?'},
                            'answer': {'en': 'Modern All-Terrain tyres (like the BFGoodrich KO2 or Falken Wildpeak A/T3W) feature computer-optimized pitch sequencing that produces minimal road hum — vastly quieter than Mud-Terrain tyres.'}
                        },
                        {
                            'question': {'en': 'Can I fit a larger tyre size on my 4x4 without a lift kit?'},
                            'answer': {'en': 'On most vehicles (like a Land Cruiser or Patrol), you can safely increase one tyre size up without rubbing. Any larger increase requires a 2-inch suspension lift to clear wheel arches.'}
                        },
                        {
                            'question': {'en': 'Why do 4x4 tyres need special dynamic balancing?'},
                            'answer': {'en': 'Large 4x4 wheels have heavy mass. Minor imbalances cause severe steering wheel vibration at 100–120 km/h. We utilize precision laser balancing equipment calibrated for heavy all-terrain tyres.'}
                        },
                        {
                            'question': {'en': 'How long do off-road tyres last in UAE desert heat?'},
                            'answer': {'en': 'With regular rotation and proper inflation, premium 4x4 tyres typically last 45,000 to 65,000 km, or 3 to 4 years. Replace sooner if sidewalls exhibit rock cuts or sun cracking.'}
                        }
                    ]
                }
            },
            {
                'section_type': 'cta',
                'sort_order': 6,
                'section_title': {'en': 'Ready to Equip Your 4x4 for the Desert?'},
                'content': {'en': 'WhatsApp our off-road specialists. We recommend the optimal All-Terrain or Mud-Terrain fitment and schedule free workshop or mobile fitting.'},
                'button_text': {'en': 'WhatsApp for 4x4 Tyre Quote'},
                'button_url': 'https://wa.me/971505069575?text=Hi%20TyresVision%2C%20I%20need%20a%20tyre%20quote%20for%20my%204x4.',
                'section_data': {
                    'call_button_text': {'en': 'Call +971 50 506 9575'},
                    'call_button_url': 'tel:+971505069575',
                    'footer_note': {'en': 'Free delivery & fitting across Dubai, Abu Dhabi, Sharjah, and all Emirates.'}
                }
            }
        ]
    },

    # =========================================================================
    # PAGE 4: Tyre Brands (/tyre-brands)
    # =========================================================================
    {
        'page_slug': 'tyre-brands',
        'sections': [
            {
                'section_type': 'hero',
                'sort_order': 1,
                'section_title': {'en': 'Tyre Brands in the UAE — 60+ Certified Global Brands'},
                'section_subtitle': {'en': 'OFFICIAL DISTRIBUTOR SOURCED'},
                'content': {'en': 'From world-renowned premium manufacturers to dependable value tiers. Every tyre is 100% genuine, date-fresh, and backed by official GCC warranty with free fitting across the UAE.'},
                'button_text': {'en': 'Compare Brand Prices on WhatsApp'},
                'button_url': 'https://wa.me/971505069575?text=Hi%20TyresVision%2C%20I%27d%20like%20to%20compare%20tyre%20brands.',
                'section_data': {
                    'badges': [
                        {'title': '60+ International Brands'},
                        {'title': '100% Genuine ESMA Certified'},
                        {'title': 'Direct Manufacturer Warranty'},
                        {'title': 'Fresh Production Dates'}
                    ],
                    'phone': '+971505069575',
                    'phone_display': '+971 50 506 9575'
                }
            },
            {
                'section_type': 'features',
                'sort_order': 2,
                'section_title': {'en': 'Tyre Brand Tiers in the UAE'},
                'section_subtitle': {'en': 'FIND YOUR BALANCE OF PERFORMANCE & BUDGET'},
                'content': {'en': 'Understand the differences in compounds, treadwear ratings, and wet braking across brand tiers.'},
                'section_data': {
                    'cards': [
                        {
                            'icon': 'award',
                            'title': 'Premium Tier — Michelin, Bridgestone, Continental, Pirelli',
                            'description': 'Industry-leading braking distances, acoustic dampening, and OEM approvals on Porsche, Mercedes, BMW, and Ferrari. Maximum summer heat resistance.'
                        },
                        {
                            'icon': 'shield',
                            'title': 'Mid-Range Tier — Hankook, Dunlop, Yokohama, Kumho, Falken',
                            'description': 'Exceptional reliability, fresh compounds, and balanced wet/dry grip at 20% to 30% lower cost than top tier brands. Excellent value for daily drivers.'
                        },
                        {
                            'icon': 'dollar',
                            'title': 'Budget Tier — Sailun, Triangle, Nexen, Zeetex, Roadstone',
                            'description': 'Cost-effective, ESMA-certified options for fleet vehicles, rideshare drivers, and budget-conscious motorists who want verified safety without high cost.'
                        }
                    ]
                }
            },
            {
                'section_type': 'price_table',
                'sort_order': 3,
                'section_title': {'en': 'Comprehensive Brand Comparison Matrix'},
                'section_subtitle': {'en': 'ORIGIN, WARRANTY & STARTING PRICES'},
                'content': {'en': 'Quick reference overview of the 16 most popular tyre manufacturers supplied and fitted across Dubai and Abu Dhabi.'},
                'section_data': {
                    'col1_header': 'Brand',
                    'col2_header': 'Country of Origin / Specialty',
                    'col3_header': 'Category',
                    'col4_header': 'Warranty',
                    'col5_header': 'Price Guide',
                    'value_cards': [
                        {'title': '100% Authentic Products', 'subtitle': 'Sourced strictly through authorized UAE distribution agencies'},
                        {'title': 'Fresh Production Guarantee', 'subtitle': 'Compliant with ESMA regulations on tyre age'},
                        {'title': 'Full GCC Specification', 'subtitle': 'High-temperature compounding for 50°C+ tarmac'},
                        {'title': 'Price Match Assurance', 'subtitle': 'Transparent upfront quotes with zero hidden workshop extras'}
                    ],
                    'rows': [
                        {'size': 'Michelin', 'common_on': {'en': 'France — Pilot Sport, Primacy, Latitude'}, 'budget': 'Premium', 'mid_range': '5-Year Official', 'premium': 'From AED 380'},
                        {'size': 'Bridgestone', 'common_on': {'en': 'Japan — Potenza, Turanza, Dueler'}, 'budget': 'Premium', 'mid_range': '5-Year Official', 'premium': 'From AED 350'},
                        {'size': 'Continental', 'common_on': {'en': 'Germany — SportContact, PremiumContact'}, 'budget': 'Premium', 'mid_range': '5-Year Official', 'premium': 'From AED 360'},
                        {'size': 'Pirelli', 'common_on': {'en': 'Italy — P Zero, Scorpion, Cinturato'}, 'budget': 'Premium', 'mid_range': '5-Year Official', 'premium': 'From AED 390'},
                        {'size': 'Goodyear', 'common_on': {'en': 'USA — Eagle F1, EfficientGrip, Wrangler'}, 'budget': 'Premium', 'mid_range': '5-Year Official', 'premium': 'From AED 340'},
                        {'size': 'Dunlop', 'common_on': {'en': 'Japan / UK — Grandtrek, SP Sport'}, 'budget': 'Mid-Range', 'mid_range': '5-Year Official', 'premium': 'From AED 260'},
                        {'size': 'Hankook', 'common_on': {'en': 'South Korea — Ventus, Dynapro, iON'}, 'budget': 'Mid-Range', 'mid_range': '5-Year Official', 'premium': 'From AED 240'},
                        {'size': 'Yokohama', 'common_on': {'en': 'Japan — Advan, Geolandar, BluEarth'}, 'budget': 'Mid-Range', 'mid_range': '5-Year Official', 'premium': 'From AED 270'},
                        {'size': 'Kumho', 'common_on': {'en': 'South Korea — Ecsta, Crugen, Solus'}, 'budget': 'Mid-Range', 'mid_range': '5-Year Official', 'premium': 'From AED 220'},
                        {'size': 'Falken', 'common_on': {'en': 'Japan — Azenis, Wildpeak, Ziex'}, 'budget': 'Mid-Range', 'mid_range': '5-Year Official', 'premium': 'From AED 250'},
                        {'size': 'Nexen', 'common_on': {'en': 'South Korea — N Fera, N Blue, Roadian'}, 'budget': 'Mid-Range', 'mid_range': '5-Year Official', 'premium': 'From AED 195'},
                        {'size': 'Toyo', 'common_on': {'en': 'Japan — Proxes, Open Country'}, 'budget': 'Mid-Range', 'mid_range': '5-Year Official', 'premium': 'From AED 260'},
                        {'size': 'Sailun', 'common_on': {'en': 'China — Atrezzo, Terramax'}, 'budget': 'Budget', 'mid_range': '3-Year Official', 'premium': 'From AED 165'},
                        {'size': 'Triangle', 'common_on': {'en': 'China — AdvanteX, SporteX'}, 'budget': 'Budget', 'mid_range': '3-Year Official', 'premium': 'From AED 155'},
                        {'size': 'Zeetex', 'common_on': {'en': 'UAE / Global — HP, SU, ZT'}, 'budget': 'Budget', 'mid_range': '3-Year Official', 'premium': 'From AED 150'}
                    ]
                }
            },
            {
                'section_type': 'advice',
                'sort_order': 4,
                'section_title': {'en': 'GCC-Spec vs Grey Market Tyres'},
                'section_subtitle': {'en': 'BUYER PROTECTION'},
                'content': {'en': 'Why buying officially imported tyres with ESMA certification protects your vehicle and warranty.'},
                'section_data': {
                    'cards': [
                        {
                            'icon': 'shield',
                            'title': {'en': 'Look for the ESMA RFID Tag'},
                            'description': {'en': 'Official UAE tyres carry an RFID sticker issued by the Emirates Authority for Standardization and Metrology, verifying they meet GCC heat and speed criteria.'}
                        },
                        {
                            'icon': 'clock',
                            'title': {'en': 'Check the DOT Date Code'},
                            'description': {'en': 'The 4-digit code (e.g. 2424 for 24th week of 2024) confirms fresh production. Beware grey market tyres that sat in uncooled sea containers for months.'}
                        },
                        {
                            'icon': 'dollar',
                            'title': {'en': 'Warranty Validity'},
                            'description': {'en': 'Grey market tyres are not honored by local UAE brand distributors. TyresVision sources exclusively from official authorized dealer networks with valid warranty.'}
                        }
                    ]
                }
            },
            {
                'section_type': 'faq',
                'sort_order': 5,
                'section_title': {'en': 'Frequently Asked Questions: Tyre Brands'},
                'section_subtitle': {'en': 'BRAND FAQ'},
                'content': {'en': 'Clear advice on brand selection, heat performance, and budget tiers.'},
                'section_data': {
                    'faqs': [
                        {
                            'question': {'en': 'Which tyre brand is best for Dubai summer heat?'},
                            'answer': {'en': 'Michelin and Bridgestone consistently rank highest in heat endurance and high-speed stability on UAE tarmac. Both use specialized silica compounds that resist softening and blistering above 50°C.'}
                        },
                        {
                            'question': {'en': 'Are budget Chinese tyres safe for highway driving in the UAE?'},
                            'answer': {'en': 'Yes, provided they are officially imported and bear the UAE ESMA certification. Brands like Sailun and Triangle pass stringent GCC braking and heat dissipation tests.'}
                        },
                        {
                            'question': {'en': 'How do I know if a tyre is officially GCC spec?'},
                            'answer': {'en': 'Look for the GCC conformity certification mark and the ESMA RFID label affixed to the tyre tread. TyresVision guarantees 100% GCC specification across all 60+ brands.'}
                        },
                        {
                            'question': {'en': 'Can I mix different tyre brands on my car?'},
                            'answer': {'en': 'You should never mix different brands or tread patterns across the same axle. While matching the front axle to one brand and the rear to another is permissible, keeping all four tyres identical is best for balanced handling.'}
                        },
                        {
                            'question': {'en': 'What does the manufacturer warranty actually cover?'},
                            'answer': {'en': 'The official distributor warranty protects against manufacturing defects, tread separation, and casing delamination. It does not cover road hazard punctures, curb damage, or improper alignment wear.'}
                        }
                    ]
                }
            },
            {
                'section_type': 'cta',
                'sort_order': 6,
                'section_title': {'en': 'Need Help Choosing the Best Brand for Your Car?'},
                'content': {'en': 'WhatsApp our specialists with your tyre size and budget. We quote verified options across premium, mid-range, and value brands.'},
                'button_text': {'en': 'WhatsApp for Brand Recommendations'},
                'button_url': 'https://wa.me/971505069575?text=Hi%20TyresVision%2C%20I%27d%20like%20to%20compare%20tyre%20brands.',
                'section_data': {
                    'call_button_text': {'en': 'Call +971 50 506 9575'},
                    'call_button_url': 'tel:+971505069575',
                    'footer_note': {'en': 'All 60+ brands delivered and fitted free across Dubai, Abu Dhabi, Sharjah, and all Emirates.'}
                }
            }
        ]
    },

    # =========================================================================
    # PAGE 5: Tyre Sizes (/tyre-sizes)
    # =========================================================================
    {
        'page_slug': 'tyre-sizes',
        'sections': [
            {
                'section_type': 'hero',
                'sort_order': 1,
                'section_title': {'en': 'Tyre Sizes in the UAE — Comprehensive Guide & Inventory'},
                'section_subtitle': {'en': 'FIND YOUR EXACT FITMENT'},
                'content': {'en': 'In-stock inventory for every rim size from 14-inch to 24-inch. Learn how to decode your sidewall markings, check vehicle compatibility, and get instant pricing across 60+ brands.'},
                'button_text': {'en': 'WhatsApp Your Tyre Size'},
                'button_url': 'https://wa.me/971505069575?text=Hi%20TyresVision%2C%20I%20need%20a%20quote%20for%20my%20tyre%20size.',
                'section_data': {
                    'badges': [
                        {'title': 'R14 to R24 Rim Sizes'},
                        {'title': 'Sedan, SUV, 4x4 & EV Fitments'},
                        {'title': 'Accurate Load & Speed Indexes'},
                        {'title': 'Free Local Installation'}
                    ],
                    'phone': '+971505069575',
                    'phone_display': '+971 50 506 9575'
                }
            },
            {
                'section_type': 'features',
                'sort_order': 2,
                'section_title': {'en': 'How to Read Your Tyre Sidewall Numbers'},
                'section_subtitle': {'en': 'EXAMPLE: 235 / 55 R 19 105 W'},
                'content': {'en': 'Every character on your tyre sidewall reveals vital structural, dimensional, and performance criteria.'},
                'section_data': {
                    'cards': [
                        {
                            'icon': 'tyre',
                            'title': '235 — Section Width (mm)',
                            'description': 'The width of the tyre in millimeters from sidewall to sidewall when mounted on the recommended rim.'
                        },
                        {
                            'icon': 'zap',
                            'title': '55 — Aspect Ratio (%)',
                            'description': 'The height of the sidewall expressed as a percentage of the width. A 55 profile means height is 55% of 235mm (129.25mm).'
                        },
                        {
                            'icon': 'award',
                            'title': 'R 19 — Radial Construction & Rim Diameter',
                            'description': '"R" signifies radial ply construction; "19" indicates the wheel rim diameter in inches.'
                        },
                        {
                            'icon': 'shield',
                            'title': '105 W — Load Index & Speed Rating',
                            'description': '"105" means maximum load capacity of 925 kg per tyre; "W" certifies safe continuous operation up to 270 km/h.'
                        }
                    ]
                }
            },
            {
                'section_type': 'price_table',
                'sort_order': 3,
                'section_title': {'en': 'Top 15 Tyre Sizes in the UAE'},
                'section_subtitle': {'en': 'VEHICLE PAIRINGS & STARTING PRICES'},
                'content': {'en': 'Starting prices and common vehicle applications for the most frequently purchased tyre dimensions across the Emirates.'},
                'section_data': {
                    'col1_header': 'Tyre Size',
                    'col2_header': 'Common On Vehicles',
                    'col3_header': 'Budget From',
                    'col4_header': 'Mid-Range',
                    'col5_header': 'Premium',
                    'value_cards': [
                        {'title': 'All-Inclusive Pricing', 'subtitle': 'Fitting, balancing, new valves and disposal included'},
                        {'title': 'No Hidden Workshop Surcharges', 'subtitle': 'The price quoted is the price paid'},
                        {'title': 'Same-Day Availability', 'subtitle': 'Over 10,000 tyres in stock at our UAE hub'},
                        {'title': 'Doorstep Mobile Fitting', 'subtitle': 'Option to have our van fit at your location'}
                    ],
                    'rows': [
                        {'size': '195/65 R15', 'common_on': {'en': 'Toyota Corolla, Nissan Sunny, Honda Civic'}, 'budget': 'AED 165', 'mid_range': 'AED 240', 'premium': 'AED 360'},
                        {'size': '205/55 R16', 'common_on': {'en': 'VW Golf, Toyota Corolla, Hyundai Elantra'}, 'budget': 'AED 180', 'mid_range': 'AED 260', 'premium': 'AED 385'},
                        {'size': '215/60 R16', 'common_on': {'en': 'Toyota Camry, Honda Accord, Nissan Altima'}, 'budget': 'AED 195', 'mid_range': 'AED 280', 'premium': 'AED 410'},
                        {'size': '215/55 R17', 'common_on': {'en': 'Toyota Camry, Lexus ES, Nissan Altima'}, 'budget': 'AED 220', 'mid_range': 'AED 310', 'premium': 'AED 460'},
                        {'size': '225/65 R17', 'common_on': {'en': 'Toyota RAV4, Nissan X-Trail, Honda CR-V'}, 'budget': 'AED 240', 'mid_range': 'AED 350', 'premium': 'AED 510'},
                        {'size': '225/45 R18', 'common_on': {'en': 'BMW 3 Series, Mercedes C-Class, Audi A4'}, 'budget': 'AED 260', 'mid_range': 'AED 390', 'premium': 'AED 590'},
                        {'size': '235/55 R19', 'common_on': {'en': 'Lexus RX, Audi Q5, Hyundai Santa Fe'}, 'budget': 'AED 295', 'mid_range': 'AED 440', 'premium': 'AED 670'},
                        {'size': '265/65 R17', 'common_on': {'en': 'Toyota Prado, Pajero, Fortuner'}, 'budget': 'AED 310', 'mid_range': 'AED 460', 'premium': 'AED 650'},
                        {'size': '275/40 R20', 'common_on': {'en': 'BMW X5, Range Rover Sport, Porsche Cayenne'}, 'budget': 'AED 390', 'mid_range': 'AED 580', 'premium': 'AED 880'},
                        {'size': '285/60 R18', 'common_on': {'en': 'Toyota Land Cruiser LC200, Nissan Patrol'}, 'budget': 'AED 390', 'mid_range': 'AED 610', 'premium': 'AED 890'},
                        {'size': '275/60 R20', 'common_on': {'en': 'Nissan Patrol Y62, Chevy Tahoe, GMC Yukon'}, 'budget': 'AED 410', 'mid_range': 'AED 640', 'premium': 'AED 920'},
                        {'size': '265/55 R20', 'common_on': {'en': 'Toyota Land Cruiser LC300, Lexus LX'}, 'budget': 'AED 420', 'mid_range': 'AED 660', 'premium': 'AED 940'}
                    ]
                }
            },
            {
                'section_type': 'faq',
                'sort_order': 4,
                'section_title': {'en': 'Frequently Asked Questions: Tyre Sizes'},
                'section_subtitle': {'en': 'SIZING FAQ'},
                'content': {'en': 'Guidance on finding, verifying, and changing tyre sizes in the UAE.'},
                'section_data': {
                    'faqs': [
                        {
                            'question': {'en': 'Where can I find the correct tyre size for my car?'},
                            'answer': {'en': 'The most reliable location is the sticker on the driver’s door pillar (jamb), inside the glove compartment, or in your vehicle owner’s manual. You can also read the numbers directly on your existing tyre sidewall.'}
                        },
                        {
                            'question': {'en': 'Can I change my tyre size or rim size?'},
                            'answer': {'en': 'You can change rim and tyre dimensions as long as the overall rolling diameter remains within ±3% of factory specification. This prevents speedometer errors and rubbing against suspension struts or wheel arches.'}
                        },
                        {
                            'question': {'en': 'What happens if I fit a lower speed rating in UAE summer?'},
                            'answer': {'en': 'Fitting a speed rating lower than manufacturer specification is dangerous. In 50°C summer heat, an under-rated tyre accumulates excessive heat that can cause tread delamination or sudden blowouts at highway speeds.'}
                        },
                        {
                            'question': {'en': 'Are front and rear tyres always the same size?'},
                            'answer': {'en': 'Not always. Many rear-wheel-drive sports cars and performance SUVs (such as BMW M models, Mercedes-AMG, and Porsche) feature "staggered" fitments, where the rear tyres are wider than the front tyres.'}
                        },
                        {
                            'question': {'en': 'If I send a photo of my tyre on WhatsApp, can you confirm the size?'},
                            'answer': {'en': 'Absolutely! Just snap a photo of the raised lettering on your tyre sidewall and message it to our WhatsApp team at +971 50 506 9575. We will reply in minutes with exact prices.'}
                        }
                    ]
                }
            },
            {
                'section_type': 'cta',
                'sort_order': 5,
                'section_title': {'en': 'Not Sure About Your Exact Tyre Size?'},
                'content': {'en': 'Send us your car model or a quick photo of your tyre sidewall on WhatsApp. We find your exact fitment instantly.'},
                'button_text': {'en': 'WhatsApp for Tyre Size Check'},
                'button_url': 'https://wa.me/971505069575?text=Hi%20TyresVision%2C%20I%20need%20a%20quote%20for%20my%20tyre%20size.',
                'section_data': {
                    'call_button_text': {'en': 'Call +971 50 506 9575'},
                    'call_button_url': 'tel:+971505069575',
                    'footer_note': {'en': 'Free fitting, computerized wheel balancing, and new valves included with all sizes.'}
                }
            }
        ]
    },

    # =========================================================================
    # PAGE 6: Tyres by Car Make & Model (/tyres-by-car)
    # =========================================================================
    {
        'page_slug': 'tyres-by-car',
        'sections': [
            {
                'section_type': 'hero',
                'sort_order': 1,
                'section_title': {'en': 'Tyres by Car Make & Model in the UAE'},
                'section_subtitle': {'en': 'VEHICLE FITMENT DIRECTORY'},
                'content': {'en': 'Exact manufacturer-matched tyre fitments for Toyota, Nissan, Mercedes, BMW, Ford, Tesla, Lexus, and Porsche. Guaranteed load and speed ratings with free local fitting across the Emirates.'},
                'button_text': {'en': 'WhatsApp for Car Model Quote'},
                'button_url': 'https://wa.me/971505069575?text=Hi%20TyresVision%2C%20I%27d%20like%20a%20tyre%20quote%20for%20my%20car.',
                'section_data': {
                    'badges': [
                        {'title': 'Original Equipment (OE) Approvals'},
                        {'title': 'Mercedes MO, BMW Star, Audi AO'},
                        {'title': 'Exact Factory Fitments'},
                        {'title': 'Doorstep Mobile Van Installation'}
                    ],
                    'phone': '+971505069575',
                    'phone_display': '+971 50 506 9575'
                }
            },
            {
                'section_type': 'shop_by',
                'sort_order': 2,
                'section_title': {'en': 'Browse Tyres by Vehicle Manufacturer'},
                'section_subtitle': {'en': 'SELECT YOUR CAR BRAND'},
                'content': {'en': 'Click on any manufacturer below to start an instant WhatsApp price check for your vehicle model.'},
                'section_data': {
                    'groups': [
                        {
                            'heading': 'Popular Vehicle Brands in the UAE',
                            'type': 'vehicle',
                            'chips': [
                                'Toyota Land Cruiser', 'Nissan Patrol', 'Toyota Prado', 'Toyota Camry',
                                'Nissan Altima', 'Toyota Corolla', 'Ford F-150', 'Tesla Model Y',
                                'Mercedes-Benz G-Class', 'BMW X5', 'Lexus LX600', 'Porsche Cayenne',
                                'Range Rover', 'Mitsubishi Pajero', 'Hyundai Tucson', 'Kia Sportage'
                            ]
                        }
                    ]
                }
            },
            {
                'section_type': 'price_table',
                'sort_order': 3,
                'section_title': {'en': 'Vehicle Tyre Size Reference Table'},
                'section_subtitle': {'en': 'TOP 20 UAE VEHICLES & FACTORY TYRE SIZES'},
                'content': {'en': 'Factory tyre specifications and starting prices for the most driven passenger cars and SUVs in the UAE.'},
                'section_data': {
                    'col1_header': 'Car Make & Model',
                    'col2_header': 'Factory Tyre Sizes',
                    'col3_header': 'Budget From',
                    'col4_header': 'Mid-Range',
                    'col5_header': 'Premium OE',
                    'value_cards': [
                        {'title': 'OE Factory Specification', 'subtitle': 'Matches your vehicle door placard standards exactly'},
                        {'title': 'Free 3D Alignment & Balancing', 'subtitle': 'Prevents steering pull and uneven edge wear'},
                        {'title': '100% Genuine Certified', 'subtitle': 'Supplied through authorized UAE automotive importers'},
                        {'title': 'Free Doorstep Mobile Fitting', 'subtitle': 'Vans dispatched to your villa or parking bay'}
                    ],
                    'rows': [
                        {'size': 'Toyota Land Cruiser LC300', 'common_on': {'en': '265/65 R18, 265/55 R20'}, 'budget': 'AED 390', 'mid_range': 'AED 620', 'premium': 'AED 940'},
                        {'size': 'Nissan Patrol Y62', 'common_on': {'en': '265/70 R18, 275/60 R20'}, 'budget': 'AED 395', 'mid_range': 'AED 630', 'premium': 'AED 920'},
                        {'size': 'Toyota Prado', 'common_on': {'en': '265/65 R17, 265/60 R18'}, 'budget': 'AED 310', 'mid_range': 'AED 470', 'premium': 'AED 680'},
                        {'size': 'Toyota Camry & Avalon', 'common_on': {'en': '215/60 R16, 215/55 R17, 235/45 R18'}, 'budget': 'AED 195', 'mid_range': 'AED 290', 'premium': 'AED 440'},
                        {'size': 'Nissan Altima & Maxima', 'common_on': {'en': '215/60 R16, 215/55 R17, 235/40 R19'}, 'budget': 'AED 195', 'mid_range': 'AED 295', 'premium': 'AED 460'},
                        {'size': 'Toyota Corolla & Yaris', 'common_on': {'en': '195/65 R15, 205/55 R16'}, 'budget': 'AED 165', 'mid_range': 'AED 240', 'premium': 'AED 360'},
                        {'size': 'Tesla Model 3 & Model Y', 'common_on': {'en': '235/45 R18, 255/45 R19, 255/40 R20'}, 'budget': 'AED 295', 'mid_range': 'AED 540', 'premium': 'AED 860'},
                        {'size': 'Mercedes-Benz C-Class / E-Class', 'common_on': {'en': '225/45 R18, 245/45 R18, 245/40 R19'}, 'budget': 'AED 280', 'mid_range': 'AED 440', 'premium': 'AED 680'},
                        {'size': 'BMW 3 Series & 5 Series', 'common_on': {'en': '225/45 R18, 245/45 R18, 245/40 R19'}, 'budget': 'AED 280', 'mid_range': 'AED 440', 'premium': 'AED 690'},
                        {'size': 'Lexus RX350 & ES350', 'common_on': {'en': '235/55 R19, 235/60 R18, 215/55 R17'}, 'budget': 'AED 240', 'mid_range': 'AED 380', 'premium': 'AED 580'},
                        {'size': 'Porsche Cayenne & Macan', 'common_on': {'en': '275/45 R20, 295/35 R21, 265/45 R20'}, 'budget': 'AED 450', 'mid_range': 'AED 690', 'premium': 'AED 1,080'},
                        {'size': 'Ford F-150 & Ranger', 'common_on': {'en': '275/65 R18, 275/55 R20, 315/70 R17'}, 'budget': 'AED 390', 'mid_range': 'AED 590', 'premium': 'AED 890'}
                    ]
                }
            },
            {
                'section_type': 'faq',
                'sort_order': 4,
                'section_title': {'en': 'Frequently Asked Questions: Tyres by Car Make'},
                'section_subtitle': {'en': 'FITMENT FAQ'},
                'content': {'en': 'Answers regarding manufacturer tyre marks, warranties, and vehicle specifics.'},
                'section_data': {
                    'faqs': [
                        {
                            'question': {'en': 'What do manufacturer markings like "MO" or "Star" mean?'},
                            'answer': {'en': 'These indicate Original Equipment (OE) homologation. "MO" denotes Mercedes-Original, "★" is engineered specifically for BMW, "AO" is Audi-approved, and "N" is Porsche-certified. These tyres are custom-tuned to the vehicle chassis dynamics.'}
                        },
                        {
                            'question': {'en': 'Do I have to buy OE homologated tyres for my German car?'},
                            'answer': {'en': 'No, standard tyres with matching size, load, and speed ratings are completely legal and safe. However, OE marked tyres preserve the original steering feel and ride comfort tuned by factory engineers.'}
                        },
                        {
                            'question': {'en': 'Can I share my vehicle registration (Mulkiya) to get the right tyre size?'},
                            'answer': {'en': 'Yes! Simply take a photo of your Mulkiya card or tyre placard on WhatsApp. Our specialists cross-reference factory databases to suggest exact fitments and prices.'}
                        },
                        {
                            'question': {'en': 'Do you offer mobile van fitting for luxury and sports cars?'},
                            'answer': {'en': 'Yes. Our mobile fitting vans utilize touchless lever-free mounting machines and low-profile jacks that eliminate rim scratches on high-end forged alloys up to 24 inches.'}
                        }
                    ]
                }
            },
            {
                'section_type': 'cta',
                'sort_order': 5,
                'section_title': {'en': 'Need the Exact Tyres for Your Car Make?'},
                'content': {'en': 'Share your vehicle make, model, and year on WhatsApp. We reply with verified fitment options and schedule free local installation.'},
                'button_text': {'en': 'WhatsApp Your Car Details'},
                'button_url': 'https://wa.me/971505069575?text=Hi%20TyresVision%2C%20I%27d%20like%20a%20tyre%20quote%20for%20my%20car.',
                'section_data': {
                    'call_button_text': {'en': 'Call +971 50 506 9575'},
                    'call_button_url': 'tel:+971505069575',
                    'footer_note': {'en': 'Free fitting across Dubai, Abu Dhabi, Sharjah, and all Emirates.'}
                }
            }
        ]
    }
]

# We will dynamically generate the 7 Emirate pages to ensure maximum detail and consistency!
EMIRATES_CONFIG = [
    {
        'slug': 'tyre-shop-dubai',
        'name': 'Dubai',
        'hero_title': 'Tyre Shop Dubai — Buy Tyres Online with Free Fitting',
        'hero_sub': 'DUBAI TYRE SUPPLY & MOBILE VAN SERVICE',
        'hero_lead': 'Skip the Al Quoz industrial area hassle. 60+ certified tyre brands with upfront transparent pricing, delivered free to a partner garage near you or fitted at your villa, apartment, or office by our mobile vans.',
        'areas_heading': 'Dubai Neighborhood Delivery & Mobile Fitting Coverage',
        'chips': ['Dubai Marina', 'JLT', 'JBR', 'Palm Jumeirah', 'Downtown Dubai', 'Business Bay', 'Al Quoz', 'Deira', 'Mirdif', 'Arabian Ranches', 'JVC', 'Dubai Hills', 'Silicon Oasis', 'Al Barsha'],
        'local_advice': 'Dubai Highway Commuting & Basement Parking: High-speed runs on Sheikh Zayed Road (E11) and Al Khail Road elevate tyre temperatures rapidly. Meanwhile, steep basement parking ramps in Marina and Downtown cause front tyre scrub. Ensure you maintain correct tyre pressure and check tread depth regularly.'
    },
    {
        'slug': 'tyre-shop-abu-dhabi',
        'name': 'Abu Dhabi',
        'hero_title': 'Tyre Shop Abu Dhabi — Doorstep Mobile Van & Workshop Fitting',
        'hero_sub': 'ABU DHABI CAPITAL TYRE NETWORK',
        'hero_lead': 'Fast, professional tyre supply and fitting across Abu Dhabi city, Musaffah, and the islands. Upfront pricing across 60+ global brands with certified mobile vans and approved partner centres.',
        'areas_heading': 'Abu Dhabi Coverage Areas',
        'chips': ['Al Reem Island', 'Yas Island', 'Saadiyat Island', 'Khalifa City', 'Al Raha Beach', 'Musaffah', 'MBZ City', 'Corniche', 'Al Bateen', 'Al Shamkha', 'Al Reef'],
        'local_advice': 'Long Highway Stretches & Desert Heat: Commuting between Abu Dhabi and Dubai or Al Ain on the E11 involves sustained 120–140 km/h speeds under 48°C summer sunshine. Check tyre pressure weekly when cold and ensure tyres carry a "Temperature A" rating.'
    },
    {
        'slug': 'tyre-shop-sharjah',
        'name': 'Sharjah',
        'hero_title': 'Tyre Shop Sharjah — Honest Upfront Pricing & Free Fitting',
        'hero_sub': 'SHARJAH COMMUTER & FLEET SPECIALISTS',
        'hero_lead': 'Avoid congested industrial areas and questionable grey-market imports. Get date-fresh, GCC-certified tyres from 60+ brands delivered and fitted at reputable partner workshops across Sharjah or at your doorstep.',
        'areas_heading': 'Sharjah Neighborhood Coverage',
        'chips': ['Industrial Area 1-17', 'Al Majaz', 'Al Nahda', 'Muwaileh', 'Al Taawun', 'Al Khan', 'University City', 'Al Qasimia', 'Al Yarmook', 'Al Mirgab'],
        'local_advice': 'Stop-and-Go Commuter Tyre Wear: Sharjah-Dubai daily commuters experience intense stop-and-go friction on Al Ittihad Road and Sheikh Mohammed Bin Zayed Road. Frequent low-speed crawling with heavy braking accelerates shoulder tread wear; rotating tyres every 10,000 km is critical.'
    },
    {
        'slug': 'tyre-shop-ajman',
        'name': 'Ajman',
        'hero_title': 'Tyre Shop Ajman — Quality Tyres with Free Local Installation',
        'hero_sub': 'AJMAN TYRE SUPPLY & MOBILE SERVICE',
        'hero_lead': 'Buy tyres online in Ajman with complete peace of mind. Genuine brands, fresh manufacturing dates, and verified warranties fitted free at partner garages or right outside your home.',
        'areas_heading': 'Ajman Coverage Areas',
        'chips': ['Al Nuaimiya', 'Al Rashidiya', 'Al Jurf', 'Al Rawda', 'Ajman Downtown', 'Ajman Corniche', 'Al Mowaihat', 'Al Helio', 'Al Bustan'],
        'local_advice': 'Coastal Air & Sand Protection: Proximity to the coast and windblown sand in developing sectors demands regular inspection of valve stems. Replace rubber valve stems with every new tyre set to prevent slow air leaks caused by fine sand intrusion.'
    },
    {
        'slug': 'tyre-shop-ras-al-khaimah',
        'name': 'Ras Al Khaimah',
        'hero_title': 'Tyre Shop Ras Al Khaimah — Built for Coast & Mountains',
        'hero_sub': 'RAK COASTAL & JEBEL JAIS FITMENTS',
        'hero_lead': 'Whether driving coastal highways in Al Hamra or climbing Jebel Jais mountain roads, equip your car with high-traction tyres from 60+ global manufacturers delivered and fitted across RAK.',
        'areas_heading': 'Ras Al Khaimah Coverage Areas',
        'chips': ['Al Nakheel', 'Al Hamra Village', 'Mina Al Arab', 'Khuzam', 'Dafan Al Khor', 'Al Dhait', 'Marjan Island', 'Al Jazirah Al Hamra', 'Jebel Jais Access'],
        'local_advice': 'Mountain Driving on Jebel Jais: Twisty climbs and steep descents place immense thermal and lateral load on your front tyres. Opt for tyres with stiff outer shoulder blocks and high wet/dry traction ratings (AA or A).'
    },
    {
        'slug': 'tyre-shop-fujairah',
        'name': 'Fujairah',
        'hero_title': 'Tyre Shop Fujairah — Mountain Inclines & Coastal Humidity',
        'hero_sub': 'EAST COAST TYRE SERVICE',
        'hero_lead': 'Premium, mid-range, and budget tyres for East Coast drivers. Engineered for mountain passes on the Sheikh Khalifa Highway and coastal road stability with free local fitting in Fujairah.',
        'areas_heading': 'Fujairah Coverage Areas',
        'chips': ['Fujairah City', 'Dibba Al Fujairah', 'Al Faseel', 'Mirbah', 'Qidfa', 'Khor Fakkan Border', 'Al Hayl', 'Sakamkam'],
        'local_advice': 'Highway Mountain Incline Traction: Driving the Sheikh Khalifa Highway through the Hajar Mountains requires robust brake grip and heat dissipation. Never drive on tyres with less than 3mm of tread remaining when navigating steep descents.'
    },
    {
        'slug': 'tyre-shop-umm-al-quwain',
        'name': 'Umm Al Quwain',
        'hero_title': 'Tyre Shop Umm Al Quwain — Reliable Tyres Delivered & Fitted',
        'hero_sub': 'UAQ FAST TYRE SERVICE',
        'hero_lead': 'Convenient tyre replacement for Umm Al Quwain residents. Upfront prices, date-fresh stock from 60+ brands, and free fitting at vetted partner garages or doorstep mobile van dispatch.',
        'areas_heading': 'Umm Al Quwain Coverage Areas',
        'chips': ['Al Salamah', 'Al Raas', 'Al Riqqah', 'Falaj Al Mualla', 'UAQ Marina', 'Old Town', 'Al Madar', 'Al Ramlah'],
        'local_advice': 'Desert Perimeter Driving: Roads in UAQ frequently encounter sand drift from desert winds. Tyres with longitudinal water/sand ejection grooves prevent slip and ensure confident directional stability.'
    }
]

for cfg in EMIRATES_CONFIG:
    slug = cfg['slug']
    name = cfg['name']
    SECTIONS_DATA.append({
        'page_slug': slug,
        'sections': [
            {
                'section_type': 'hero',
                'sort_order': 1,
                'section_title': {'en': cfg['hero_title']},
                'section_subtitle': {'en': cfg['hero_sub']},
                'content': {'en': cfg['hero_lead']},
                'button_text': {'en': f'WhatsApp for {name} Tyre Quote'},
                'button_url': f'https://wa.me/971505069575?text=Hi%20TyresVision%2C%20I%20need%20a%20tyre%20quote%20in%20{name}.',
                'section_data': {
                    'badges': [
                        {'title': f'Free Fitting in {name}'},
                        {'title': '60+ Genuine Brands'},
                        {'title': 'Fresh Production Dates'},
                        {'title': 'Doorstep Mobile Van Service'}
                    ],
                    'phone': '+971505069575',
                    'phone_display': '+971 50 506 9575'
                }
            },
            {
                'section_type': 'coverage',
                'sort_order': 2,
                'section_title': {'en': f'Delivery & Fitting Coverage Across {name}'},
                'section_subtitle': {'en': f'{name.upper()} SERVICE OPTIONS'},
                'content': {'en': f'Choose free installation at any of our partner fitting centres across {name}, or have our certified mobile van replace your tyres at your doorstep.'},
                'section_data': {
                    'options': [
                        {
                            'tag': '100% FREE FITTING',
                            'heading': f'Free fitting at a partner centre in {name}',
                            'description': f'We deliver your fresh tyres directly to a vetted workshop near your home in {name}. Mounting, computerized wheel balancing, new valves, and eco-disposal are all included at no extra charge.',
                            'button_text': 'Book at Partner Workshop',
                            'wa_msg': f'Hi TyresVision, I would like to book free tyre fitting at a partner centre in {name}.'
                        },
                        {
                            'tag': 'MOBILE VAN SERVICE',
                            'heading': f'Mobile van fitting at your location in {name}',
                            'description': f'Our fully equipped mobile vans fit and balance your tyres right on your villa driveway, building parking bay, or office premises in {name}. Call-out fee confirmed upfront before dispatch.',
                            'button_text': 'Book Mobile Van',
                            'wa_msg': f'Hi TyresVision, I would like to book mobile van tyre fitting in {name}.'
                        }
                    ],
                    'areas': [
                        {
                            'heading': cfg['areas_heading'],
                            'emirate': name,
                            'chips': cfg['chips']
                        }
                    ]
                }
            },
            {
                'section_type': 'price_table',
                'sort_order': 3,
                'section_title': {'en': f'Popular Tyre Sizes & Starting Prices in {name}'},
                'section_subtitle': {'en': 'UPFRONT TRANSPARENT PRICING'},
                'content': {'en': f'All prices include delivery to {name}, professional mounting, 3D wheel balancing, new standard valves, and old tyre eco-disposal.'},
                'section_data': {
                    'col1_header': 'Tyre Size',
                    'col2_header': 'Common Vehicle Fitment',
                    'col3_header': 'Budget Tier',
                    'col4_header': 'Mid-Range',
                    'col5_header': 'Premium Tier',
                    'value_cards': [
                        {'title': 'No Hidden Extras', 'subtitle': 'Valves, balancing and fitting included'},
                        {'title': '100% Official Warranty', 'subtitle': 'Sourced directly from authorized distributors'},
                        {'title': 'Fast Local Dispatch', 'subtitle': f'Same-day service available across {name}'},
                        {'title': 'Eco-Friendly Disposal', 'subtitle': 'Old tyres recycled responsibly'}
                    ],
                    'rows': [
                        {'size': '195/65 R15', 'common_on': {'en': 'Corolla, Sunny, Civic'}, 'budget': 'AED 165', 'mid_range': 'AED 240', 'premium': 'AED 360'},
                        {'size': '205/55 R16', 'common_on': {'en': 'Golf, Elantra, Corolla'}, 'budget': 'AED 180', 'mid_range': 'AED 260', 'premium': 'AED 385'},
                        {'size': '215/60 R16', 'common_on': {'en': 'Camry, Altima, Accord'}, 'budget': 'AED 195', 'mid_range': 'AED 280', 'premium': 'AED 410'},
                        {'size': '265/65 R17', 'common_on': {'en': 'Prado, Pajero, Fortuner'}, 'budget': 'AED 310', 'mid_range': 'AED 460', 'premium': 'AED 650'},
                        {'size': '285/60 R18', 'common_on': {'en': 'Land Cruiser LC200, Patrol'}, 'budget': 'AED 390', 'mid_range': 'AED 610', 'premium': 'AED 890'},
                        {'size': '275/60 R20', 'common_on': {'en': 'Patrol Y62, Tahoe, Yukon'}, 'budget': 'AED 410', 'mid_range': 'AED 640', 'premium': 'AED 920'}
                    ]
                }
            },
            {
                'section_type': 'advice',
                'sort_order': 4,
                'section_title': {'en': f'Driving & Tyre Maintenance in {name}'},
                'section_subtitle': {'en': 'LOCAL ROAD CONDITIONS'},
                'content': {'en': cfg['local_advice']},
                'section_data': {
                    'cards': [
                        {
                            'icon': 'clock',
                            'title': {'en': 'Inspect Tyre Pressure Weekly'},
                            'description': {'en': f'High ambient heat in {name} increases tyre pressure by 3–5 PSI while driving. Always measure pressure in the morning when tyres are cold.'}
                        },
                        {
                            'icon': 'shield',
                            'title': {'en': 'Rotate Every 10,000 KM'},
                            'description': {'en': 'Even out tread wear across all four wheels and prolong your tyre lifespan by scheduling routine tyre rotation with our mobile vans.'}
                        },
                        {
                            'icon': 'award',
                            'title': {'en': 'Verify the ESMA RFID Tag'},
                            'description': {'en': f'Avoid roadside shops selling grey imports. Every tyre supplied in {name} by TyresVision has official UAE ESMA certification and warranty.'}
                        }
                    ]
                }
            },
            {
                'section_type': 'faq',
                'sort_order': 5,
                'section_title': {'en': f'Frequently Asked Questions: Tyre Fitting in {name}'},
                'section_subtitle': {'en': f'{name.upper()} FAQ'},
                'content': {'en': f'Common questions about tyre ordering, delivery times, and mobile van fitting in {name}.'},
                'section_data': {
                    'faqs': [
                        {
                            'question': {'en': f'How does free tyre fitting work in {name}?'},
                            'answer': {'en': f'You select your tyres and choose your preferred partner workshop in {name}. We deliver the fresh tyres there free of charge. You drive in at your appointed time, and they fit, balance, and install new valves with zero additional fees.'}
                        },
                        {
                            'question': {'en': f'Can your mobile van come to my home or office in {name}?'},
                            'answer': {'en': f'Yes! Our mobile vans are fully self-sufficient with power generators, touchless tyre changers, and computer balancers. We can fit tyres in your villa driveway or office car park anywhere in {name}.'}
                        },
                        {
                            'question': {'en': f'How fast can tyres be fitted in {name}?'},
                            'answer': {'en': f'Most popular sizes are delivered same-day or within 24 hours across {name}. Send us your size on WhatsApp and we will confirm the fastest fitting slot.'}
                        },
                        {
                            'question': {'en': 'What is included in the tyre price?'},
                            'answer': {'en': 'Every quoted price includes the tyre itself, free delivery, professional mounting, computerized dynamic wheel balancing, new standard valves, and eco-friendly disposal of your old tyres.'}
                        },
                        {
                            'question': {'en': 'How do I pay for my tyres?'},
                            'answer': {'en': 'We offer flexible payment options including credit/debit card online, payment link via WhatsApp, or cash/card upon fitting completion at the workshop.'}
                        }
                    ]
                }
            },
            {
                'section_type': 'cta',
                'sort_order': 6,
                'section_title': {'en': f'Ready to Get New Tyres in {name}?'},
                'content': {'en': f'Message our tyre specialists on WhatsApp with your tyre size. We reply in minutes with verified quotes and book your fitting in {name}.'},
                'button_text': {'en': f'WhatsApp Us for {name} Tyres'},
                'button_url': f'https://wa.me/971505069575?text=Hi%20TyresVision%2C%20I%20need%20a%20tyre%20quote%20in%20{name}.',
                'section_data': {
                    'call_button_text': {'en': 'Call +971 50 506 9575'},
                    'call_button_url': 'tel:+971505069575',
                    'footer_note': {'en': f'Open daily — fast doorstep mobile vans and partner centres active across {name}.'}
                }
            }
        ]
    })


def seed_sections():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            target_slugs = [p['page_slug'] for p in SECTIONS_DATA]
            print(f"Targeting {len(target_slugs)} pages for Section Builder seeding...")

            # Clean out existing active sections for these 12 slugs to avoid duplicates
            slug_placeholders = ', '.join(['%s'] * len(target_slugs))
            delete_sql = f"DELETE FROM page_sections WHERE page_slug IN ({slug_placeholders})"
            cursor.execute(delete_sql, tuple(target_slugs))
            print(f"Cleared existing sections for target slugs.")

            insert_sql = """
                INSERT INTO page_sections (
                    page_slug, section_type, section_title, section_subtitle,
                    content, button_text, button_url, section_data,
                    sort_order, is_active
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            total_inserted = 0
            for page_entry in SECTIONS_DATA:
                page_slug = page_entry['page_slug']
                for sec in page_entry['sections']:
                    cursor.execute(insert_sql, (
                        page_slug,
                        sec.get('section_type', 'hero'),
                        json.dumps(sec.get('section_title', {}), ensure_ascii=False),
                        json.dumps(sec.get('section_subtitle', {}), ensure_ascii=False),
                        json.dumps(sec.get('content', {}), ensure_ascii=False),
                        json.dumps(sec.get('button_text', {}), ensure_ascii=False),
                        sec.get('button_url'),
                        json.dumps(sec.get('section_data', {}), ensure_ascii=False),
                        sec.get('sort_order', 1),
                        1
                    ))
                    total_inserted += 1

            conn.commit()
            print(f"Successfully seeded {total_inserted} page sections across {len(target_slugs)} pages!")

    finally:
        conn.close()


if __name__ == '__main__':
    seed_sections()
