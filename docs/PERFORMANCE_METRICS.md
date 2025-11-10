# Performance Metrics

## Overview
This document outlines the performance monitoring system for the Třešinky Cetechovice web application, including measurement tools, key metrics, and optimization strategies.

## 🎯 Target Performance Goals

### Core Web Vitals
- **LCP (Largest Contentful Paint):** < 2.5s
- **FID (First Input Delay):** < 100ms
- **CLS (Cumulative Layout Shift):** < 0.1

### Performance Scores
- **Lighthouse Performance:** > 90 (mobile), > 95 (desktop)
- **PageSpeed Insights:** > 90 (mobile), > 95 (desktop)
- **GTmetrix Grade:** A (90%+)

### Additional Metrics
- **Time to Interactive (TTI):** < 3s on mobile
- **First Contentful Paint (FCP):** < 1.8s
- **Speed Index:** < 3.4s
- **Total Blocking Time (TBT):** < 200ms

## 📊 Measurement Tools

### 1. Chrome DevTools Lighthouse
**Usage:**
```bash
# In Chrome DevTools:
# F12 → Lighthouse → Performance → Mobile → Generate Report
```

**What it measures:**
- Performance score
- Core Web Vitals
- Opportunities for optimization
- Diagnostics

### 2. PageSpeed Insights API
**Usage:**
```bash
# Quick check command
curl "https://www.googleapis.com/pagespeed/v5/runPagespeed?url=https://your-site.com&category=performance&strategy=mobile"
```

**What it measures:**
- Real-world performance data
- Field data from Chrome User Experience Report
- Lab data from Lighthouse

### 3. Web Vitals Monitoring (Built-in)
**Usage:**
```javascript
// In browser console
WebVitals.getMetrics();
```

**What it measures:**
- Real-time Core Web Vitals
- User interaction metrics
- Custom performance events

### 4. GTmetrix
**Usage:**
- Visit gtmetrix.com
- Enter website URL
- Run analysis

**What it measures:**
- Page load time
- Total page size
- Number of requests
- Waterfall analysis

## 📈 Current Performance Status

### Baseline Metrics (Before Optimization)
- **Performance Score:** 75-80 (mobile)
- **LCP:** 3-4 seconds
- **FID:** 150-200ms
- **CLS:** 0.2-0.3
- **TTI:** 4-5 seconds

### Target Metrics (After Optimization)
- **Performance Score:** > 90 (mobile)
- **LCP:** < 2.5 seconds
- **FID:** < 100ms
- **CLS:** < 0.1
- **TTI:** < 3 seconds

## 🔧 Optimization Strategies

### Image Optimization
- **WebP conversion** - Convert all images to WebP format
- **Responsive images** - Serve appropriate sizes for different devices
- **Lazy loading** - Load images only when needed
- **Compression** - Optimize image compression ratios

### CSS Optimization
- **Minification** - Remove unnecessary whitespace and comments
- **Critical CSS** - Inline critical CSS for above-the-fold content
- **Unused CSS removal** - Remove unused CSS rules
- **CSS splitting** - Split CSS into critical and non-critical parts

### JavaScript Optimization
- **Minification** - Compress JavaScript files
- **Defer loading** - Defer non-critical JavaScript
- **Code splitting** - Split JavaScript into smaller chunks
- **Tree shaking** - Remove unused code

### Caching Strategy
- **Browser caching** - Set appropriate cache headers
- **CDN usage** - Use Content Delivery Network for static assets
- **Service worker** - Implement offline caching
- **Database caching** - Cache frequently accessed data

## 📋 Performance Testing Workflow

### 1. Pre-Change Testing
```bash
# Run Lighthouse audit
lighthouse http://localhost:5000 --output=json --output-path=./performance-before.json

# Check Web Vitals
# Open browser console and run:
WebVitals.getMetrics()
```

### 2. Post-Change Testing
```bash
# Run Lighthouse audit again
lighthouse http://localhost:5000 --output=json --output-path=./performance-after.json

# Compare results
lighthouse-ci compare --before=./performance-before.json --after=./performance-after.json
```

### 3. Production Testing
```bash
# Test production URL
curl "https://www.googleapis.com/pagespeed/v5/runPagespeed?url=https://your-production-site.com&category=performance&strategy=mobile"
```

## 📊 Performance Monitoring Dashboard

### Key Metrics to Track
1. **Performance Score** - Overall performance rating
2. **Core Web Vitals** - LCP, FID, CLS
3. **Load Times** - FCP, TTI, Speed Index
4. **Resource Usage** - Total size, number of requests
5. **User Experience** - Bounce rate, session duration

### Monitoring Frequency
- **Daily** - Automated Lighthouse CI runs
- **Weekly** - Manual performance audits
- **Monthly** - Comprehensive performance review
- **On Release** - Pre and post-deployment testing

## 🚨 Performance Alerts

### Critical Alerts
- Performance score drops below 80
- LCP exceeds 4 seconds
- FID exceeds 300ms
- CLS exceeds 0.25

### Warning Alerts
- Performance score drops below 90
- LCP exceeds 2.5 seconds
- FID exceeds 100ms
- CLS exceeds 0.1

## 📝 Performance Reports

### Daily Report
- Performance score trend
- Core Web Vitals status
- Top performance issues
- Optimization recommendations

### Weekly Report
- Performance comparison with previous week
- New performance issues identified
- Optimization progress
- Upcoming performance tasks

### Monthly Report
- Overall performance trends
- Major optimization achievements
- Performance budget status
- Future optimization plans

## 🔍 Troubleshooting Common Issues

### Slow LCP
- **Check image loading** - Ensure images are optimized and properly sized
- **Review CSS** - Look for render-blocking CSS
- **Check JavaScript** - Ensure critical JavaScript is not blocking rendering

### High FID
- **Check JavaScript execution** - Look for long-running tasks
- **Review event handlers** - Ensure event handlers are optimized
- **Check third-party scripts** - Review external script performance

### High CLS
- **Check image dimensions** - Ensure images have proper dimensions
- **Review font loading** - Use font-display: swap
- **Check dynamic content** - Ensure dynamic content doesn't cause layout shifts

## 📚 Resources

### Documentation
- [Web Vitals](https://web.dev/vitals/)
- [Lighthouse](https://developers.google.com/web/tools/lighthouse)
- [PageSpeed Insights](https://developers.google.com/speed/pagespeed/insights/)

### Tools
- [Chrome DevTools](https://developers.google.com/web/tools/chrome-devtools)
- [GTmetrix](https://gtmetrix.com/)
- [WebPageTest](https://www.webpagetest.org/)

### Best Practices
- [Web Performance Best Practices](https://web.dev/fast/)
- [Image Optimization](https://web.dev/fast/#optimize-your-images)
- [CSS Optimization](https://web.dev/fast/#optimize-your-css)

---

*Last updated: [Current Date]*
*Next review: [Next Review Date]*
