/**
 * Web Vitals Performance Monitoring
 * Tracks Core Web Vitals: LCP, FID, CLS
 */

// Simple Web Vitals implementation
(function() {
    'use strict';
    
    // Configuration
    const CONFIG = {
        endpoint: '/api/web-vitals', // Endpoint for sending metrics (DISABLED)
        debug: false, // Set to true for console logging
        sendToServer: false // DISABLED: Set to true to enable server sending
    };
    
    // Metrics storage
    const metrics = {};
    
    // Utility function to send metrics
    function sendMetric(name, value, rating) {
        const metric = {
            name: name,
            value: value,
            rating: rating,
            url: window.location.href,
            timestamp: Date.now(),
            userAgent: navigator.userAgent
        };
        
        if (CONFIG.debug) {
            console.log('Web Vitals:', metric);
        }
        
        // Store metric
        metrics[name] = metric;
        
        // Send to server (DISABLED - endpoint not implemented)
        if (CONFIG.sendToServer && typeof fetch !== 'undefined') {
            fetch(CONFIG.endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(metric)
            }).catch(err => {
                // Silently fail if endpoint is not available
                if (CONFIG.debug) {
                    console.warn('Failed to send Web Vitals metric:', err);
                }
            });
        }
        
        // Trigger custom event
        window.dispatchEvent(new CustomEvent('webVital', { detail: metric }));
    }
    
    // Get rating based on thresholds
    function getRating(name, value) {
        const thresholds = {
            'LCP': [2500, 4000], // Good: <2.5s, Needs Improvement: 2.5s-4s, Poor: >4s
            'FID': [100, 300],   // Good: <100ms, Needs Improvement: 100ms-300ms, Poor: >300ms
            'CLS': [0.1, 0.25]   // Good: <0.1, Needs Improvement: 0.1-0.25, Poor: >0.25
        };
        
        if (!thresholds[name]) return 'unknown';
        
        const [good, needsImprovement] = thresholds[name];
        
        if (value <= good) return 'good';
        if (value <= needsImprovement) return 'needs-improvement';
        return 'poor';
    }
    
    // Largest Contentful Paint (LCP)
    function measureLCP() {
        if ('PerformanceObserver' in window) {
            try {
                const observer = new PerformanceObserver((list) => {
                    const entries = list.getEntries();
                    const lastEntry = entries[entries.length - 1];
                    if (lastEntry) {
                        const value = lastEntry.startTime;
                        const rating = getRating('LCP', value);
                        sendMetric('LCP', value, rating);
                    }
                });
                
                observer.observe({ type: 'largest-contentful-paint', buffered: true });
                
                // Cleanup observer after page becomes hidden
                document.addEventListener('visibilitychange', function() {
                    if (document.visibilityState === 'hidden') {
                        observer.disconnect();
                    }
                });
                
            } catch (err) {
                if (CONFIG.debug) {
                    console.warn('LCP measurement failed:', err);
                }
            }
        }
    }
    
    // First Input Delay (FID)
    function measureFID() {
        if ('PerformanceObserver' in window) {
            try {
                const observer = new PerformanceObserver((list) => {
                    const entries = list.getEntries();
                    for (const entry of entries) {
                        if (entry.processingStart && entry.startTime) {
                            const value = entry.processingStart - entry.startTime;
                            const rating = getRating('FID', value);
                            sendMetric('FID', value, rating);
                            observer.disconnect();
                            break;
                        }
                    }
                });
                
                observer.observe({ type: 'first-input', buffered: true });
                
            } catch (err) {
                if (CONFIG.debug) {
                    console.warn('FID measurement failed:', err);
                }
            }
        }
    }
    
    // Cumulative Layout Shift (CLS)
    function measureCLS() {
        if ('PerformanceObserver' in window) {
            try {
                let clsValue = 0;
                let sessionValue = 0;
                let sessionEntries = [];
                
                const observer = new PerformanceObserver((list) => {
                    for (const entry of list.getEntries()) {
                        if (!entry.hadRecentInput) {
                            const firstSessionEntry = sessionEntries[0];
                            const lastSessionEntry = sessionEntries[sessionEntries.length - 1];
                            
                            // If the entry occurred less than 1 second after the previous entry and
                            // less than 5 seconds after the first entry in the session, include the
                            // entry in the current session. Otherwise, start a new session.
                            if (sessionValue &&
                                entry.startTime - lastSessionEntry.startTime < 1000 &&
                                entry.startTime - firstSessionEntry.startTime < 5000) {
                                sessionValue += entry.value;
                                sessionEntries.push(entry);
                            } else {
                                sessionValue = entry.value;
                                sessionEntries = [entry];
                            }
                            
                            // If the current session value is larger than the current CLS value,
                            // update CLS and the entries contributing to it.
                            if (sessionValue > clsValue) {
                                clsValue = sessionValue;
                            }
                        }
                    }
                });
                
                observer.observe({ type: 'layout-shift', buffered: true });
                
                // Report CLS when page becomes hidden
                document.addEventListener('visibilitychange', function() {
                    if (document.visibilityState === 'hidden') {
                        const rating = getRating('CLS', clsValue);
                        sendMetric('CLS', clsValue, rating);
                        observer.disconnect();
                    }
                });
                
                // Also report CLS on page unload
                window.addEventListener('beforeunload', function() {
                    const rating = getRating('CLS', clsValue);
                    sendMetric('CLS', clsValue, rating);
                });
                
            } catch (err) {
                if (CONFIG.debug) {
                    console.warn('CLS measurement failed:', err);
                }
            }
        }
    }
    
    // Initialize measurements
    function init() {
        // Wait for page to be loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
            return;
        }
        
        measureLCP();
        measureFID();
        measureCLS();
    }
    
    // Public API
    window.WebVitals = {
        getMetrics: function() {
            return { ...metrics };
        },
        
        onMetric: function(callback) {
            window.addEventListener('webVital', function(event) {
                callback(event.detail);
            });
        },
        
        // Manual trigger for SPA navigation
        triggerMeasurement: function() {
            measureLCP();
            measureFID();
            measureCLS();
        }
    };
    
    // Auto-initialize
    init();
    
})(); 