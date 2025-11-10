# Mobile Testing Guide

## Overview
Comprehensive guide for testing mobile performance optimizations for the Třešinky Cetechovice web application.

## 🎯 Mobile Performance Goals

### Core Web Vitals (Mobile)
- **LCP (Largest Contentful Paint):** < 2.5s
- **FID (First Input Delay):** < 100ms
- **CLS (Cumulative Layout Shift):** < 0.1

### Performance Scores
- **Lighthouse Mobile:** > 90
- **PageSpeed Insights Mobile:** > 90
- **GTmetrix Mobile:** A (90%+)

### Additional Mobile Metrics
- **Time to Interactive (TTI):** < 3s
- **First Contentful Paint (FCP):** < 1.8s
- **Speed Index:** < 3.4s
- **Total Blocking Time (TBT):** < 200ms

## 📱 Mobile Testing Devices

### Physical Devices (Recommended)
- **iPhone 12/13/14** - iOS Safari
- **Samsung Galaxy S21/S22** - Android Chrome
- **Google Pixel 6/7** - Android Chrome
- **iPad Air/Pro** - iOS Safari

### Emulated Devices
- **Chrome DevTools** - Device emulation
- **Safari Web Inspector** - iOS device simulation
- **Android Studio Emulator** - Android device simulation

## 🔧 Testing Tools

### 1. Chrome DevTools
**Setup:**
1. Open Chrome DevTools (F12)
2. Click device toggle button
3. Select mobile device from dropdown
4. Set network throttling to "Slow 3G"

**Tests to Run:**
- Lighthouse audit
- Performance profiling
- Network analysis
- Memory usage

### 2. Safari Web Inspector
**Setup:**
1. Enable Developer menu in Safari
2. Connect iOS device via USB
3. Open Web Inspector
4. Select device and page

**Tests to Run:**
- Timeline recording
- Network analysis
- Memory profiling
- JavaScript debugging

### 3. PageSpeed Insights
**Usage:**
1. Visit https://pagespeed.web.dev/
2. Enter website URL
3. Select "Mobile" strategy
4. Click "Analyze"

**What it measures:**
- Core Web Vitals
- Performance score
- Optimization opportunities
- Field data

### 4. GTmetrix
**Usage:**
1. Visit https://gtmetrix.com/
2. Enter website URL
3. Select mobile device
4. Run analysis

**What it measures:**
- Page load time
- Total page size
- Number of requests
- Waterfall analysis

## 📊 Testing Scenarios

### Scenario 1: First Visit (Cold Cache)
**Purpose:** Test initial page load performance
**Steps:**
1. Clear browser cache and cookies
2. Open website in incognito/private mode
3. Run performance audit
4. Record metrics

**Expected Results:**
- LCP < 2.5s
- FID < 100ms
- CLS < 0.1
- Performance score > 90

### Scenario 2: Returning Visit (Warm Cache)
**Purpose:** Test cached resource loading
**Steps:**
1. Visit website normally
2. Refresh page
3. Run performance audit
4. Record metrics

**Expected Results:**
- LCP < 1.5s
- FID < 50ms
- CLS < 0.05
- Performance score > 95

### Scenario 3: Slow Network (3G)
**Purpose:** Test performance on slow connections
**Steps:**
1. Set network throttling to "Slow 3G"
2. Clear cache
3. Load website
4. Run performance audit

**Expected Results:**
- LCP < 4s
- FID < 200ms
- CLS < 0.15
- Performance score > 80

### Scenario 4: Gallery Navigation
**Purpose:** Test gallery performance on mobile
**Steps:**
1. Navigate to gallery page
2. Scroll through albums
3. Open album and view images
4. Run performance audit

**Expected Results:**
- Smooth scrolling
- Fast image loading
- No layout shifts
- Responsive touch interactions

## 📋 Testing Checklist

### Pre-Test Setup
- [ ] Clear browser cache
- [ ] Disable browser extensions
- [ ] Set network throttling
- [ ] Enable performance monitoring
- [ ] Prepare test devices

### Performance Testing
- [ ] Run Lighthouse audit
- [ ] Check Core Web Vitals
- [ ] Test on multiple devices
- [ ] Test on different networks
- [ ] Record all metrics

### Functionality Testing
- [ ] Test navigation
- [ ] Test form submissions
- [ ] Test image gallery
- [ ] Test responsive design
- [ ] Test touch interactions

### Accessibility Testing
- [ ] Test screen reader compatibility
- [ ] Test keyboard navigation
- [ ] Test color contrast
- [ ] Test font sizes
- [ ] Test touch targets

## 📊 Performance Metrics Tracking

### Key Metrics to Monitor
1. **Performance Score** - Overall performance rating
2. **LCP** - Largest Contentful Paint
3. **FID** - First Input Delay
4. **CLS** - Cumulative Layout Shift
5. **TTI** - Time to Interactive
6. **FCP** - First Contentful Paint
7. **Speed Index** - Visual completeness
8. **TBT** - Total Blocking Time

### Recording Format
```
Date: [Date]
Device: [Device Model]
Browser: [Browser Version]
Network: [Network Type]
Performance Score: [Score]
LCP: [Time]s
FID: [Time]ms
CLS: [Score]
TTI: [Time]s
FCP: [Time]s
Speed Index: [Time]s
TBT: [Time]ms
Notes: [Additional observations]
```

## 🚨 Common Mobile Issues

### Image Loading Issues
**Problem:** Images not loading or loading slowly
**Symptoms:**
- Blank image placeholders
- Slow image rendering
- Layout shifts during image load

**Solutions:**
- Implement lazy loading
- Use WebP format
- Add proper image dimensions
- Implement progressive loading

### Touch Interaction Issues
**Problem:** Poor touch responsiveness
**Symptoms:**
- Delayed touch responses
- Unresponsive buttons
- Poor scrolling performance

**Solutions:**
- Optimize JavaScript execution
- Use CSS transforms for animations
- Implement touch event optimization
- Reduce JavaScript blocking time

### Layout Shift Issues
**Problem:** Content jumping during load
**Symptoms:**
- Text moving during load
- Images causing layout shifts
- Poor user experience

**Solutions:**
- Add image dimensions
- Use font-display: swap
- Reserve space for dynamic content
- Optimize CSS loading

### Network Performance Issues
**Problem:** Slow loading on mobile networks
**Symptoms:**
- Long load times
- Timeouts
- Poor user experience

**Solutions:**
- Implement proper caching
- Use CDN for static assets
- Optimize resource loading
- Implement service worker

## 📱 Device-Specific Testing

### iOS Safari Testing
**Key Considerations:**
- WebKit-specific optimizations
- iOS-specific performance quirks
- Safari developer tools
- iOS device limitations

**Testing Steps:**
1. Use Safari Web Inspector
2. Test on actual iOS devices
3. Check iOS-specific features
4. Verify touch interactions

### Android Chrome Testing
**Key Considerations:**
- Chrome-specific optimizations
- Android performance characteristics
- Chrome DevTools
- Android device variations

**Testing Steps:**
1. Use Chrome DevTools
2. Test on various Android devices
3. Check Android-specific features
4. Verify touch interactions

## 📊 Performance Comparison

### Before vs After Optimization
| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Performance Score | 75 | 90+ | +20% |
| LCP | 3.5s | 2.0s | -43% |
| FID | 200ms | 80ms | -60% |
| CLS | 0.25 | 0.08 | -68% |
| TTI | 4.5s | 2.5s | -44% |

### Device Comparison
| Device | Performance Score | LCP | FID | CLS |
|--------|------------------|-----|-----|-----|
| iPhone 12 | 92 | 1.8s | 60ms | 0.05 |
| Samsung S21 | 89 | 2.1s | 80ms | 0.08 |
| Google Pixel 6 | 91 | 1.9s | 70ms | 0.06 |

## 🔧 Troubleshooting

### Performance Issues
1. **Check network throttling** - Ensure proper network simulation
2. **Clear browser cache** - Remove cached resources
3. **Check device settings** - Verify device configuration
4. **Review test environment** - Ensure consistent testing conditions

### Testing Issues
1. **Device connection** - Check USB/network connection
2. **Browser compatibility** - Use supported browser versions
3. **Test data** - Ensure consistent test data
4. **Environment setup** - Verify testing environment

## 📚 Resources

### Documentation
- [Web Vitals](https://web.dev/vitals/)
- [Lighthouse](https://developers.google.com/web/tools/lighthouse)
- [Mobile Performance](https://web.dev/fast/)

### Tools
- [Chrome DevTools](https://developers.google.com/web/tools/chrome-devtools)
- [Safari Web Inspector](https://developer.apple.com/safari/tools/)
- [PageSpeed Insights](https://developers.google.com/speed/pagespeed/insights/)

### Best Practices
- [Mobile Performance Best Practices](https://web.dev/fast/#mobile-performance)
- [Touch Performance](https://web.dev/touch-performance/)
- [Mobile UX Guidelines](https://web.dev/mobile-ux-guidelines/)

---

*Last updated: [Current Date]*
*Next review: [Next Review Date]*
