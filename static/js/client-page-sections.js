/**
 * static/js/client-page-sections.js
 * TyresVision Dynamic Client Page & Section Renderer
 * 
 * Fetches page sections directly from the JSON database API (/api/sections/<slug>)
 * and dynamically renders them into the DOM without any server-side Jinja looping.
 */

(function () {
  'use strict';

  function escapeHtml(str) {
    if (!str && str !== 0) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  function renderSvgIcon(iconName, strokeWidth = '2.2', size = 24) {
    const sw = strokeWidth;
    const s = size;
    switch (iconName) {
      case 'dollar-sign':
      case 'price':
        return `<svg width="${s}" height="${s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="${sw}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>`;
      case 'truck':
      case 'delivery':
        return `<svg width="${s}" height="${s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="${sw}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="1" y="3" width="15" height="13"></rect><polygon points="16 8 20 8 23 11 23 16 8"></polygon><circle cx="5.5" cy="18.5" r="2.5"></circle><circle cx="18.5" cy="18.5" r="2.5"></circle></svg>`;
      case 'award':
      case 'badge':
      case 'quality':
        return `<svg width="${s}" height="${s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="${sw}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="8" r="6"></circle><path d="M15.477 12.89 17 22l-5-3-5 3 1.523-9.11"></path></svg>`;
      case 'heart':
      case 'users':
      case 'team':
        return `<svg width="${s}" height="${s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="${sw}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>`;
      case 'zap':
      case 'innovation':
      case 'fast':
        return `<svg width="${s}" height="${s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="${sw}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 18h6"></path><path d="M10 22h4"></path><path d="M15.09 14c.18-.98.65-1.74 1.41-2.5A4.65 4.65 0 0 0 18 8 6 6 0 0 0 6 8c0 1 .23 2.23 1.5 3.5A4.61 4.61 0 0 1 8.91 14"></path></svg>`;
      case 'globe':
      case 'network':
        return `<svg width="${s}" height="${s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="${sw}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>`;
      case 'disc':
      case 'tyre':
      case 'wheel':
        return `<svg width="${s}" height="${s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="${sw}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"></circle><circle cx="12" cy="12" r="3"></circle><path d="M12 3v6"></path><path d="M12 15v6"></path><path d="M3 12h6"></path><path d="M15 12h6"></path></svg>`;
      case 'headset':
      case 'support':
      case 'service':
        return `<svg width="${s}" height="${s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="${sw}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 18v-6a9 9 0 0 1 18 0v6"></path><path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3zM3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z"></path></svg>`;
      default:
        return `<svg width="${s}" height="${s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="${sw}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path><polyline points="9 12 11 14 15 10"></polyline></svg>`;
    }
  }

  function renderHeroSection(sec, page, locale) {
    const isAr = locale === 'ar';
    const homeUrl = isAr ? '/ar' : '/';
    const homeLabel = isAr ? 'الرئيسية' : 'Home';
    const defaultTitle = isAr ? 'من نحن' : 'About Us';
    const pageTitle = page?.title || defaultTitle;
    const titleHtml = (sec.section_title || '').replace(/\n/g, '<br>');
    const heroImage = sec.image || '';

    let featuresHtml = '';
    const featuresList = (sec.section_data && (sec.section_data.features || sec.section_data.items)) || [];
    if (Array.isArray(featuresList) && featuresList.length > 0) {
      featuresHtml = `
        <div class="about-hero-features-grid">
          ${featuresList.map(feat => `
            <div class="about-hero-feat-item">
              <div class="about-hero-feat-icon">
                ${renderSvgIcon(feat.icon || 'star', '2.2', 20)}
              </div>
              <div>
                <div class="about-hero-feat-title">${escapeHtml(feat.title || '')}</div>
                <div class="about-hero-feat-sub">${escapeHtml(feat.sub || feat.desc || '')}</div>
              </div>
            </div>
          `).join('')}
        </div>
      `;
    }

    const bgStyle = heroImage
      ? `background: linear-gradient(90deg, rgba(12, 16, 8, 0.95) 0%, rgba(12, 16, 8, 0.88) 55%, rgba(12, 16, 8, 0.72) 100%), url('${heroImage}') center center / cover no-repeat;`
      : `background: #0c1008;`;

    return `
      <section class="about-hero-dark" id="hero-${sec.id}" style="${bgStyle}">
        <div class="wrap">
          
          <!-- Top Breadcrumb -->
          <nav class="about-breadcrumb" aria-label="Breadcrumb">
            <a href="${homeUrl}">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                <polyline points="9 22 9 12 15 12 15 22"></polyline>
              </svg>
              <span>${homeLabel}</span>
            </a>
            <span class="sep" aria-hidden="true">/</span>
            <span class="current">${escapeHtml(pageTitle)}</span>
          </nav>

          <!-- Hero Content from Database -->
          <div class="hero-db-content" style="max-width: 860px;">
            ${sec.section_subtitle ? `
              <span class="eyebrow">&mdash; ${escapeHtml(sec.section_subtitle)}</span>
            ` : ''}
            
            ${titleHtml ? `<h1>${titleHtml}</h1>` : ''}
            
            ${sec.content ? `
              <div class="lead">${sec.content}</div>
            ` : ''}

            ${sec.button_text ? `
              <div style="margin-top: 24px;">
                <a href="${sec.button_url || '#'}" class="about-hero-cta">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                  </svg>
                  <span>${escapeHtml(sec.button_text)}</span>
                </a>
              </div>
            ` : ''}
          </div>

          <!-- Key Hero Pillars -->
          ${featuresHtml}

        </div>
      </section>
    `;
  }

  function renderContentImageSection(sec, page, locale) {
    const hasImage = Boolean(sec.image && sec.image.trim());
    const isLeft = sec.image_position === 'left';
    const gridStyle = hasImage
      ? (isLeft ? 'grid-template-columns: 1fr 1.15fr;' : 'grid-template-columns: 1.15fr 1fr;')
      : 'grid-template-columns: 1fr;';

    const mediaHtml = hasImage ? `
      <div class="about-story-media">
        <img src="${sec.image}" alt="${escapeHtml(sec.section_title || '')}" loading="lazy" />
        ${sec.section_data && sec.section_data.badge_title ? `
          <div class="about-story-floating-badge">
            <div class="about-badge-icon">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                <circle cx="9" cy="7" r="4"></circle>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
              </svg>
            </div>
            <div>
              <div class="about-badge-title">${escapeHtml(sec.section_data.badge_title)}</div>
              <div class="about-badge-sub">${escapeHtml(sec.section_data.badge_sub || '')}</div>
            </div>
          </div>
        ` : ''}
      </div>
    ` : '';

    const contentHtml = `
      <div class="about-story-content" ${!hasImage ? 'style="max-width: 900px;"' : ''}>
        ${sec.section_subtitle ? `<span class="eyebrow">&mdash; ${escapeHtml(sec.section_subtitle)}</span>` : ''}
        ${sec.section_title ? `<h2>${escapeHtml(sec.section_title)}</h2>` : ''}
        
        ${sec.content ? `<div class="about-story-rich">${sec.content}</div>` : ''}

        ${sec.button_text ? `
          <div>
            <a href="${sec.button_url || '#'}" class="about-btn-primary">
              <span>${escapeHtml(sec.button_text)}</span>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <line x1="5" y1="12" x2="19" y2="12"></line>
                <polyline points="12 5 19 12 12 19"></polyline>
              </svg>
            </a>
          </div>
        ` : ''}
      </div>
    `;

    return `
      <section class="about-story-section" id="story-${sec.id}">
        <div class="wrap">
          <div class="about-story-grid" style="${gridStyle}">
            ${hasImage ? (isLeft ? mediaHtml + contentHtml : contentHtml + mediaHtml) : contentHtml}
          </div>
        </div>
      </section>
    `;
  }

  function renderFeaturesSection(sec, page, locale) {
    let cardsHtml = '';
    const cardsList = (sec.section_data && (sec.section_data.cards || sec.section_data.items || sec.section_data.features)) || [];
    
    if (Array.isArray(cardsList) && cardsList.length > 0) {
      cardsHtml = `
        <div class="about-why-grid">
          ${cardsList.map(card => `
            <div class="about-why-card">
              <div class="about-why-icon-wrap">
                ${renderSvgIcon(card.icon || 'shield', '2.2', 26)}
              </div>
              <h3 class="about-why-card-title">${escapeHtml(card.title || '')}</h3>
              <p class="about-why-card-desc">${escapeHtml(card.desc || card.description || '')}</p>
            </div>
          `).join('')}
        </div>
      `;
    }

    return `
      <section class="about-why-section" id="why-${sec.id}">
        <div class="wrap">
          ${(sec.section_title || sec.section_subtitle) ? `
            <div class="about-section-head">
              ${sec.section_subtitle ? `<span class="eyebrow">&mdash; ${escapeHtml(sec.section_subtitle)}</span>` : ''}
              ${sec.section_title ? `<h2>${escapeHtml(sec.section_title)}</h2>` : ''}
              ${sec.content ? `<div class="sublead">${sec.content}</div>` : ''}
            </div>
          ` : ''}
          ${cardsHtml}
        </div>
      </section>
    `;
  }

  function renderStatsSection(sec, page, locale) {
    const metricsList = (sec.section_data && (sec.section_data.metrics || sec.section_data.items)) || [];
    let metricsHtml = '';
    if (Array.isArray(metricsList) && metricsList.length > 0) {
      metricsHtml = `
        <div class="about-stats-grid">
          ${metricsList.map(stat => `
            <div class="about-stat-item">
              <div class="about-stat-icon">
                ${renderSvgIcon(stat.icon || 'disc', '2', 32)}
              </div>
              <div class="about-stat-num">${escapeHtml(stat.number || '')}</div>
              <div class="about-stat-label">${escapeHtml(stat.heading || stat.label || '')}</div>
              <div class="about-stat-sub">${escapeHtml(stat.subtext || stat.sub || '')}</div>
            </div>
          `).join('')}
        </div>
      `;
    }

    return `
      <section class="about-stats-band" id="stats-${sec.id}">
        <div class="wrap">
          ${metricsHtml}
        </div>
      </section>
    `;
  }

  function renderMissionSection(sec, page, locale) {
    const hasImage = Boolean(sec.image && sec.image.trim());
    const isLeft = sec.image_position === 'left';
    const gridStyle = hasImage
      ? (isLeft ? 'grid-template-columns: 1.2fr 1fr;' : 'grid-template-columns: 1fr 1.2fr;')
      : 'grid-template-columns: 1fr;';

    const mediaHtml = hasImage ? `
      <div class="about-team-media">
        <img src="${sec.image}" alt="${escapeHtml(sec.section_title || '')}" loading="lazy" />
      </div>
    ` : '';

    const contentHtml = `
      <div ${!hasImage ? 'style="max-width: 900px;"' : ''}>
        ${sec.section_subtitle ? `<span class="eyebrow">&mdash; ${escapeHtml(sec.section_subtitle)}</span>` : ''}
        ${sec.section_title ? `<h2>${escapeHtml(sec.section_title)}</h2>` : ''}
        ${sec.content ? `<div class="about-team-rich">${sec.content}</div>` : ''}
        ${sec.button_text ? `
          <div>
            <a href="${sec.button_url || '#'}" class="about-btn-outline">
              <span>${escapeHtml(sec.button_text)}</span>
            </a>
          </div>
        ` : ''}
      </div>
    `;

    return `
      <section class="about-team-section" id="team-${sec.id}">
        <div class="wrap">
          <div class="about-team-grid" style="${gridStyle}">
            ${hasImage ? (isLeft ? mediaHtml + contentHtml : contentHtml + mediaHtml) : contentHtml}
          </div>
        </div>
      </section>
    `;
  }

  function renderCtaSection(sec, page, locale) {
    return `
      <section class="about-action-wrap" id="cta-${sec.id}">
        <div class="wrap">
          <div class="about-action-box">
            <div class="about-action-left">
              ${sec.image ? `
                <div class="about-action-wheel" style="max-width:110px; width:110px; height:110px; flex-shrink:0;">
                  <img src="${sec.image}" alt="${escapeHtml(sec.section_title || '')}" style="width:100%; height:100%; object-fit:contain;" loading="lazy" />
                </div>
              ` : ''}
              <div class="about-action-icon-circle">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                  <circle cx="9" cy="7" r="4"></circle>
                  <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                  <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
                </svg>
              </div>
              <div>
                <h3 class="about-action-title">${escapeHtml(sec.section_title || '')}</h3>
                ${sec.content ? `<div class="about-action-desc">${sec.content}</div>` : ''}
              </div>
            </div>

            ${sec.button_text ? `
              <div>
                <a href="${sec.button_url || '#'}" class="about-action-btn">
                  <span>${escapeHtml(sec.button_text)}</span>
                </a>
              </div>
            ` : ''}
          </div>
        </div>
      </section>
    `;
  }

  function renderBreadcrumbBar(page, locale) {
    const isAr = locale === 'ar';
    const homeUrl = isAr ? '/ar' : '/';
    const homeLabel = isAr ? 'الرئيسية' : 'Home';
    const pageTitle = page?.title || (isAr ? 'من نحن' : 'About Us');

    return `
      <div style="background:#0c1008; border-bottom:1px solid rgba(255,255,255,0.06); padding: 18px 0;">
        <div class="wrap">
          <nav class="about-breadcrumb" aria-label="Breadcrumb" style="margin-bottom:0;">
            <a href="${homeUrl}">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                <polyline points="9 22 9 12 15 12 15 22"></polyline>
              </svg>
              <span>${homeLabel}</span>
            </a>
            <span class="sep" aria-hidden="true">/</span>
            <span class="current">${escapeHtml(pageTitle)}</span>
          </nav>
        </div>
      </div>
    `;
  }

  function renderPageHeroBanner(page, locale) {
    const isAr = locale === 'ar';
    const homeUrl = isAr ? '/ar' : '/';
    const homeLabel = isAr ? 'الرئيسية' : 'Home';
    const pageTitle = page?.title || (isAr ? 'من نحن' : 'About Us');
    const heroImage = page?.banner_image;
    const bodyContent = page?.content || '';

    // If bodyContent contains headers (<h1>, <h2>, <p>), render directly; otherwise wrap with title
    let contentHtml = '';
    if (bodyContent && (bodyContent.includes('<h1') || bodyContent.includes('<h2') || bodyContent.includes('<p>') || bodyContent.includes('<div'))) {
      contentHtml = bodyContent;
    } else {
      contentHtml = `
        <h1 style="color:#ffffff; font-size:clamp(2.1rem, 3.8vw, 2.9rem); font-weight:800; line-height:1.25; margin-bottom:18px;">
          ${escapeHtml(pageTitle)}
        </h1>
        ${bodyContent ? `<div style="color:rgba(255,255,255,0.88); font-size:1.05rem; line-height:1.8;">${bodyContent}</div>` : ''}
      `;
    }

    const bgStyle = heroImage
      ? `background: linear-gradient(90deg, rgba(12, 16, 8, 0.95) 0%, rgba(12, 16, 8, 0.88) 55%, rgba(12, 16, 8, 0.72) 100%), url('${heroImage}') center center / cover no-repeat;`
      : `background: #0c1008;`;

    return `
      <section class="about-hero-dark" id="page-hero-banner" style="${bgStyle} padding-top: 52px; padding-bottom: 64px; position: relative;">
        <div class="wrap">
          
          <!-- Top Breadcrumb -->
          <nav class="about-breadcrumb" aria-label="Breadcrumb" style="margin-bottom: 24px;">
            <a href="${homeUrl}">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                <polyline points="9 22 9 12 15 12 15 22"></polyline>
              </svg>
              <span>${homeLabel}</span>
            </a>
            <span class="sep" aria-hidden="true">/</span>
            <span class="current">${escapeHtml(pageTitle)}</span>
          </nav>

          <!-- Dynamic Database Content Layer -->
          <div class="hero-db-content" style="max-width: 860px;">
            ${contentHtml}
          </div>

        </div>
      </section>
    `;
  }

  function renderPageProseBody(page, locale) {
    if (!page || !page.content || !page.content.trim()) return '';
    return `
      <section style="padding: 56px 0; background: #ffffff; border-bottom: 1px solid var(--line);">
        <div class="wrap">
          <div class="article-prose" style="max-width: 860px; margin: 0 auto; font-size: 1.05rem; line-height: 1.8; color: var(--ink);">
            ${page.content}
          </div>
        </div>
      </section>
    `;
  }

  async function loadAndRenderPageSections() {
    const root = document.getElementById('dynamic-sections-root');
    if (!root) return;

    // Detect slug from data attribute or current pathname
    let slug = root.dataset.slug || '';
    if (!slug) {
      const pathParts = window.location.pathname.replace(/^\/(en|ar)\//, '/').split('/').filter(Boolean);
      slug = pathParts[pathParts.length - 1] || 'about-us';
    }

    // Detect active locale
    const locale = root.dataset.locale || (window.location.pathname.startsWith('/ar') || document.documentElement.lang === 'ar' ? 'ar' : 'en');

    try {
      const apiUrl = `/api/sections/${encodeURIComponent(slug)}?locale=${encodeURIComponent(locale)}`;
      const resp = await fetch(apiUrl);
      if (!resp.ok) throw new Error(`HTTP error ${resp.status}`);
      
      const data = await resp.json();
      const page = data.page || {};
      const sections = data.sections || [];

      // Update document title and meta description dynamically
      if (page.title) {
        document.title = `${page.title} | ${locale === 'ar' ? 'تايرز فيجن الإمارات' : 'TyresVision UAE'}`;
      }
      if (page.meta_description) {
        const metaDesc = document.querySelector('meta[name="description"]');
        if (metaDesc) metaDesc.setAttribute('content', page.meta_description);
      }

      let finalHtml = '';

      // 1. If page has a hero banner image configured in Pages Admin, render the Hero Banner using database content
      if (page.banner_image) {
        finalHtml += renderPageHeroBanner(page, locale);
      } else {
        finalHtml += renderBreadcrumbBar(page, locale);
        finalHtml += renderPageProseBody(page, locale);
      }

      // 2. Render all dynamic sub-sections created in Sections Admin
      if (sections.length > 0) {
        sections.forEach(sec => {
          switch (sec.section_type) {
            case 'content_image':
              finalHtml += renderContentImageSection(sec, page, locale);
              break;
            case 'features':
              finalHtml += renderFeaturesSection(sec, page, locale);
              break;
            case 'stats':
              finalHtml += renderStatsSection(sec, page, locale);
              break;
            case 'mission_vision':
              finalHtml += renderMissionSection(sec, page, locale);
              break;
            case 'cta':
              finalHtml += renderCtaSection(sec, page, locale);
              break;
            default:
              finalHtml += renderContentImageSection(sec, page, locale);
              break;
          }
        });
      }

      root.innerHTML = finalHtml;

    } catch (err) {
      console.error('Failed to load page sections dynamically:', err);
      root.innerHTML = `
        <div style="padding: 60px 20px; text-align: center; max-width: 600px; margin: 0 auto;">
          <h2 style="color: var(--ink); font-weight: 800;">Content Loading Error</h2>
          <p style="color: var(--muted); font-size: 0.95rem; margin-top: 8px;">Please check your connection and refresh the page.</p>
        </div>
      `;
    }
  }

  // Initialize on DOM load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadAndRenderPageSections);
  } else {
    loadAndRenderPageSections();
  }

})();
