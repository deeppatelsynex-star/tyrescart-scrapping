"""Central mapping of URL type -> scraper script, and the sole place that
decides which scraper handles a given URL. app/app.py imports both of these
rather than keeping its own copy, so the script names/detection rules never
drift out of sync between the two.
"""

SCRIPT_MAP = {
    "brand": "pitstoparabia-brand 1.py",
    "sitemap": "pitstoparabia-instock 3.py",
    "listing": "pitstoparabiabycsv.py",
    "product": "pitstoparabiabycsv.py",
}


def detect_scraper_type(url):
    """Classifies a URL by substring match, checked in this exact priority order:

    1. sitemap  -- contains /en/sitemap/
    2. brand    -- contains /en/tyres/brands/
    3. listing  -- under /en/tyres/ but not brand/sitemap (pitstoparabiabycsv.py
                   itself tells listing vs. product apart once it fetches the page)
    4. unknown  -- never guessed; caller must refuse to scrape these

    Order matters: a brand URL also contains "/en/tyres/", so sitemap/brand must
    be checked before the generic listing fallback.
    """
    if not url:
        return "unknown"

    lowered = url.lower()
    if "/en/sitemap/" in lowered:
        return "sitemap"
    if "/en/tyres/brands/" in lowered:
        return "brand"
    if "/en/tyres/" in lowered:
        return "listing"
    return "unknown"
