/**
 * AppBinHub Main Application
 * Coordinates all components and handles application initialization
 */

class AppBinHub {
    constructor() {
        this.data = {
            applications: [],
            categories: [],
            metadata: {}
        };
        this.isInitialized = false;
        this.loadingPromises = [];
        
        this.init();
    }

    async init() {
        try {
            // Wait for DOM to be ready
            if (document.readyState === 'loading') {
                await new Promise(resolve => {
                    document.addEventListener('DOMContentLoaded', resolve);
                });
            }

            // Initialize components
            await this.initializeComponents();
            
            // Load data
            await this.loadData();
            
            // Setup integrations
            this.setupIntegrations();
            
            // Load state from URL
            this.loadStateFromURL();
            
            // Mark as initialized
            this.isInitialized = true;
            
            // Dispatch ready event
            this.dispatchReadyEvent();
            
            console.log('AppBinHub initialized successfully');
            
        } catch (error) {
            console.error('Failed to initialize AppBinHub:', error);
            this.showErrorState(error);
        }
    }

    async initializeComponents() {
        // Ensure all component managers are available
        const requiredComponents = [
            'themeManager',
            'searchManager', 
            'catalogManager'
        ];

        for (const component of requiredComponents) {
            if (!window[component]) {
                throw new Error(`Required component ${component} not found`);
            }
        }

        // Wait for components to be ready
        await Promise.all([
            this.waitForComponent('themeManager'),
            this.waitForComponent('searchManager'),
            this.waitForComponent('catalogManager')
        ]);
    }

    async waitForComponent(componentName) {
        return new Promise((resolve) => {
            const checkComponent = () => {
                if (window[componentName] && window[componentName].setup) {
                    resolve();
                } else {
                    setTimeout(checkComponent, 50);
                }
            };
            checkComponent();
        });
    }

    async loadData() {
        try {
            // Show loading state
            this.showLoadingState();
            
            // Load applications and categories data
            const [applicationsData, categoriesData] = await Promise.all([
                this.loadJSON('./data/applications.json'),
                this.loadJSON('./data/categories.json')
            ]);

            // Process and store data
            this.data.applications = applicationsData.applications || [];
            this.data.metadata = applicationsData.metadata || {};
            this.data.categories = categoriesData.categories || [];

            // Update category counts based on actual applications
            this.updateCategoryCounts();
            
            // Update UI with loaded data
            this.updateUI();
            
            console.log(`Loaded ${this.data.applications.length} applications and ${this.data.categories.length} categories`);
            
        } catch (error) {
            console.error('Failed to load data:', error);
            this.showErrorState(error);
        }
    }

    async loadJSON(url) {
        try {
            const response = await fetch(url, {
                cache: 'no-cache',
                headers: {
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`Failed to load ${url}:`, error);
            throw error;
        }
    }

    updateCategoryCounts() {
        // Reset all category counts
        this.data.categories.forEach(category => {
            category.count = 0;
        });

        // Count applications in each category
        this.data.applications.forEach(app => {
            if (app.category && Array.isArray(app.category)) {
                app.category.forEach(categoryName => {
                    const category = this.data.categories.find(cat => 
                        cat.name.toLowerCase() === categoryName.toLowerCase() ||
                        cat.id === categoryName.toLowerCase()
                    );
                    if (category) {
                        category.count++;
                    }
                });
            }
        });

        // Sort categories by count (descending) then by name
        this.data.categories.sort((a, b) => {
            if (b.count !== a.count) {
                return b.count - a.count;
            }
            return a.name.localeCompare(b.name);
        });
    }

    updateUI() {
        // Update application count in header
        this.updateAppCount();
        
        // Update footer statistics
        this.updateFooterStats();
        
        // Update last updated timestamp
        this.updateLastUpdated();
        
        // Pass data to components
        if (window.catalogManager) {
            window.catalogManager.setApplicationsData(this.data.applications);
            window.catalogManager.setCategoriesData(this.data.categories);
        }
        
        if (window.searchManager) {
            window.searchManager.setApplicationsData(this.data.applications);
        }
        
        // Hide loading state
        this.hideLoadingState();
    }

    updateAppCount() {
        const appCountElements = document.querySelectorAll('#appCount, #footerAppCount');
        const count = this.data.applications.length;
        
        appCountElements.forEach(element => {
            if (element) {
                element.textContent = count.toLocaleString();
            }
        });
    }

    updateFooterStats() {
        const categoryCountElement = document.getElementById('footerCategoryCount');
        if (categoryCountElement) {
            categoryCountElement.textContent = this.data.categories.length;
        }
    }

    updateLastUpdated() {
        const lastUpdatedElement = document.getElementById('lastUpdated');
        if (lastUpdatedElement && this.data.metadata.last_updated) {
            try {
                const date = new Date(this.data.metadata.last_updated);
                lastUpdatedElement.textContent = date.toLocaleDateString();
            } catch {
                lastUpdatedElement.textContent = 'Unknown';
            }
        }
    }

    setupIntegrations() {
        // Connect search manager to catalog manager
        if (window.searchManager && window.catalogManager) {
            window.searchManager.onResultsUpdate((filteredApps, stats) => {
                window.catalogManager.setApplicationsData(filteredApps);
                this.updateSearchStats(stats);
            });
        }

        // Setup error handling
        window.addEventListener('error', (event) => {
            console.error('Global error:', event.error);
            this.handleGlobalError(event.error);
        });

        // Setup unhandled promise rejection handling
        window.addEventListener('unhandledrejection', (event) => {
            console.error('Unhandled promise rejection:', event.reason);
            this.handleGlobalError(event.reason);
        });

        // Setup performance monitoring
        this.setupPerformanceMonitoring();
        
        // Setup analytics
        this.setupAnalytics();
        
        // Setup auto-refresh mechanism
        this.setupAutoRefresh();
    }

    updateSearchStats(stats) {
        // Update search result count if needed
        const resultCount = stats.filtered;
        const totalCount = stats.total;
        
        // You could add a results counter element here
        console.log(`Showing ${resultCount} of ${totalCount} applications`);
    }

    loadStateFromURL() {
        // Load search and filter state from URL parameters
        if (window.searchManager) {
            window.searchManager.loadFromURL();
        }
    }

    showLoadingState() {
        const loadingElement = document.getElementById('loadingState');
        if (loadingElement) {
            loadingElement.style.display = 'block';
        }
        
        const gridElement = document.getElementById('applicationsGrid');
        if (gridElement) {
            gridElement.style.display = 'none';
        }
    }

    hideLoadingState() {
        const loadingElement = document.getElementById('loadingState');
        if (loadingElement) {
            loadingElement.style.display = 'none';
        }
        
        const gridElement = document.getElementById('applicationsGrid');
        if (gridElement) {
            gridElement.style.display = 'grid';
        }
    }

    showErrorState(error) {
        const loadingElement = document.getElementById('loadingState');
        const emptyElement = document.getElementById('emptyState');
        
        if (loadingElement) {
            loadingElement.style.display = 'none';
        }
        
        if (emptyElement) {
            emptyElement.innerHTML = `
                <div class="text-6xl mb-4">⚠️</div>
                <h3 class="text-xl font-semibold text-gray-900 dark:text-dark-text mb-2">
                    Failed to load applications
                </h3>
                <p class="text-gray-600 dark:text-dark-text-secondary mb-4">
                    ${error.message || 'An unexpected error occurred'}
                </p>
                <button onclick="window.location.reload()" 
                        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                    Retry
                </button>
            `;
            emptyElement.style.display = 'block';
        }
    }

    handleGlobalError(err) {
        // Log error for debugging
        console.error('Global error handled:', err);
        
        // Show user-friendly error message
        this.showNotification('An error occurred. Please refresh the page.', 'error');
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg max-w-sm transition-all duration-300 ${
            type === 'error' ? 'bg-red-500 text-white' : 
            type === 'success' ? 'bg-green-500 text-white' :
            'bg-blue-500 text-white'
        }`;
        notification.textContent = message;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 5000);
    }

    setupPerformanceMonitoring() {
        // Monitor page load performance
        if ('performance' in window) {
            window.addEventListener('load', () => {
                setTimeout(() => {
                    const perfData = performance.getEntriesByType('navigation')[0];
                    if (perfData) {
                        console.log(`Page load time: ${Math.round(perfData.loadEventEnd - perfData.fetchStart)}ms`);
                    }
                }, 0);
            });
        }

        // Monitor memory usage (if available)
        if ('memory' in performance) {
            setInterval(() => {
                const memory = performance.memory;
                if (memory.usedJSHeapSize > memory.jsHeapSizeLimit * 0.9) {
                    console.warn('High memory usage detected');
                }
            }, 30000); // Check every 30 seconds
        }
    }

    setupAnalytics() {
        // Basic analytics tracking
        const analytics = {
            pageViews: 0,
            sessionStart: Date.now(),
            interactions: 0
        };

        // Track page view
        analytics.pageViews++;
        
        // Track user interactions
        document.addEventListener('click', () => {
            analytics.interactions++;
        });

        // Save analytics data periodically
        setInterval(() => {
            try {
                localStorage.setItem('appbinhub-analytics', JSON.stringify({
                    ...analytics,
                    sessionDuration: Date.now() - analytics.sessionStart
                }));
            } catch {
                // Ignore localStorage errors
            }
        }, 60000); // Save every minute
    }

    setupAutoRefresh() {
        // Check for updates every 5 minutes
        const checkInterval = 5 * 60 * 1000; // 5 minutes
        
        setInterval(async () => {
            try {
                // Check if metadata has changed using the last_updated timestamp
                const metadataResponse = await fetch('./data/applications.json', {
                    cache: 'no-cache'
                });
                
                if (metadataResponse.ok) {
                    const data = await metadataResponse.json();
                    const newLastUpdated = data.metadata?.last_updated;
                    const currentLastUpdated = this.data.metadata?.last_updated;
                    
                    if (newLastUpdated && newLastUpdated !== currentLastUpdated) {
                        console.log('Data update detected, refreshing...');
                        await this.refresh();
                        this.showNotification('New applications available! Data refreshed.', 'success');
                    }
                }
            } catch (error) {
                console.log('Auto-refresh check failed:', error);
                // Silently fail - don't spam users with errors
            }
        }, checkInterval);

        // Also check on window focus (when user returns to tab)
        document.addEventListener('visibilitychange', async () => {
            if (!document.hidden && this.isInitialized) {
                // Wait a bit then check for updates
                setTimeout(async () => {
                    try {
                        const metadataResponse = await fetch('./data/applications.json', {
                            cache: 'no-cache'
                        });
                        
                        if (metadataResponse.ok) {
                            const data = await metadataResponse.json();
                            const newLastUpdated = data.metadata?.last_updated;
                            const currentLastUpdated = this.data.metadata?.last_updated;
                            
                            if (newLastUpdated && newLastUpdated !== currentLastUpdated) {
                                console.log('Data update detected on focus, refreshing...');
                                await this.refresh();
                                this.showNotification('Data refreshed with latest updates!', 'success');
                            }
                        }
                    } catch (error) {
                        // Silently fail
                        console.log('Focus refresh check failed:', error);
                    }
                }, 2000); // Wait 2 seconds after focus
            }
        });
    }

    dispatchReadyEvent() {
        const event = new CustomEvent('appbinhub:ready', {
            detail: {
                applications: this.data.applications.length,
                categories: this.data.categories.length,
                version: this.data.metadata.version
            }
        });
        window.dispatchEvent(event);
    }

    // Public API methods
    getApplications() {
        return this.data.applications;
    }

    getCategories() {
        return this.data.categories;
    }

    getMetadata() {
        return this.data.metadata;
    }

    isReady() {
        return this.isInitialized;
    }

    async refresh() {
        console.log('Refreshing application data...');
        await this.loadData();
        this.showNotification('Application data refreshed', 'success');
    }

    // Search methods
    search(query) {
        if (window.searchManager) {
            window.searchManager.handleSearch(query);
        }
    }

    filterByCategory(category) {
        if (window.searchManager) {
            window.searchManager.handleCategoryFilter(category);
        }
    }

    // Theme methods
    toggleTheme() {
        if (window.themeManager) {
            window.themeManager.toggleTheme();
        }
    }

    setTheme(theme) {
        if (window.themeManager) {
            window.themeManager.setTheme(theme);
        }
    }

    getCurrentTheme() {
        return window.themeManager ? window.themeManager.getCurrentTheme() : 'light';
    }
}

// Initialize the application
const app = new AppBinHub();

// Export for global access
window.AppBinHub = window.AppBinHub || {};
window.AppBinHub.app = app;

// Expose main methods globally for console access and debugging
window.appbinhub = {
    refresh: () => app.refresh(),
    search: (query) => app.search(query),
    filterByCategory: (category) => app.filterByCategory(category),
    toggleTheme: () => app.toggleTheme(),
    setTheme: (theme) => app.setTheme(theme),
    getApplications: () => app.getApplications(),
    getCategories: () => app.getCategories(),
    getStats: () => ({
        applications: app.getApplications().length,
        categories: app.getCategories().length,
        theme: app.getCurrentTheme(),
        ready: app.isReady()
    })
};

// Add helpful console message
console.log('%cAppBinHub loaded! 📦', 'color: #4dabf7; font-size: 16px; font-weight: bold;');
console.log('Use window.appbinhub for debugging and manual control');
console.log('Available methods:', Object.keys(window.appbinhub));

// Export for module systems
/* global module */
if (typeof module !== 'undefined' && typeof module.exports !== 'undefined') {
    module.exports = AppBinHub;
}