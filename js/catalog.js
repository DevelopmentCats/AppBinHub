/**
 * AppBinHub Application Catalog Management
 * Handles rendering and display of application cards
 */

class CatalogManager {
    constructor() {
        this.applicationsGrid = null;
        this.loadingState = null;
        this.emptyState = null;
        this.loadMoreContainer = null;
        this.loadMoreBtn = null;
        this.applications = [];
        this.categories = [];
        this.displayedCount = 0;
        this.itemsPerPage = 20;
        this.isLoading = false;
        
        this.init();
    }

    init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            this.setup();
        }
    }

    setup() {
        this.applicationsGrid = document.getElementById('applicationsGrid');
        this.loadingState = document.getElementById('loadingState');
        this.emptyState = document.getElementById('emptyState');
        this.loadMoreContainer = document.getElementById('loadMoreContainer');
        this.loadMoreBtn = document.getElementById('loadMoreBtn');
        
        if (!this.applicationsGrid) {
            console.error('Applications grid not found');
            return;
        }

        this.setupEventListeners();
        this.setupIntersectionObserver();
    }

    setupEventListeners() {
        // Load more button
        if (this.loadMoreBtn) {
            this.loadMoreBtn.addEventListener('click', () => {
                this.loadMoreApplications();
            });
        }

        // Listen for theme changes to update card styles
        window.addEventListener('themeChanged', () => {
            this.updateCardStyles();
        });
    }

    setupIntersectionObserver() {
        // Lazy loading with Intersection Observer
        if ('IntersectionObserver' in window) {
            this.imageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        if (img.dataset.src) {
                            img.src = img.dataset.src;
                            img.removeAttribute('data-src');
                            this.imageObserver.unobserve(img);
                        }
                    }
                });
            }, {
                rootMargin: '50px'
            });
        }
    }

    setApplicationsData(applications) {
        this.applications = Array.isArray(applications) ? applications : [];
        this.displayedCount = 0;
        this.clearGrid();
        this.renderApplications(this.applications.slice(0, this.itemsPerPage));
        this.updateLoadMoreButton();
    }

    setCategoriesData(categories) {
        this.categories = Array.isArray(categories) ? categories : [];
        this.renderCategoryFilters();
    }

    renderApplications(apps, append = false) {
        if (!this.applicationsGrid) return;

        this.showLoading(false);
        this.showEmpty(false);

        if (!append) {
            this.clearGrid();
            this.displayedCount = 0;
        }

        if (!apps || apps.length === 0) {
            if (this.displayedCount === 0) {
                this.showEmpty(true);
            }
            return;
        }

        const fragment = document.createDocumentFragment();
        
        apps.forEach((app, index) => {
            const card = this.createApplicationCard(app);
            if (card) {
                // Add fade-in animation with staggered delay
                card.style.animationDelay = `${(index % this.itemsPerPage) * 50}ms`;
                card.classList.add('fade-in');
                fragment.appendChild(card);
            }
        });

        this.applicationsGrid.appendChild(fragment);
        this.displayedCount += apps.length;
        
        // Setup lazy loading for new images
        if (this.imageObserver) {
            const newImages = this.applicationsGrid.querySelectorAll('img[data-src]');
            newImages.forEach(img => this.imageObserver.observe(img));
        }
    }

    createApplicationCard(app) {
        if (!app) return null;

        const card = document.createElement('div');
        card.className = 'app-card';
        card.setAttribute('data-app-id', app.id || '');
        
        // Create card content
        card.innerHTML = `
            <div class="app-header">
                <div class="app-icon">
                    ${this.createAppIcon(app)}
                </div>
                <div class="app-info">
                    <h3 class="app-name">${this.escapeHtml(app.name || 'Unknown Application')}</h3>
                    <span class="app-version">v${this.escapeHtml(app.version || '1.0.0')}</span>
                </div>
            </div>
            
            <p class="app-description">
                ${this.escapeHtml(app.description || 'No description available.')}
            </p>
            
            ${this.createCategoryTags(app.category)}
            
            <div class="app-meta">
                <div class="app-size">
                    <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path>
                    </svg>
                    ${this.formatFileSize(app.appimage?.size)}
                </div>
                <div class="app-date">
                    <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                    </svg>
                    ${this.formatDate(app.last_updated || app.source?.release_date)}
                </div>
            </div>
            
            <div class="app-actions">
                ${this.createDownloadButtons(app)}
            </div>
            
            ${this.createSourceLink(app)}
        `;

        // Add click handler for card interaction
        this.addCardInteractions(card, app);
        
        return card;
    }

    createAppIcon(app) {
        const iconPath = app.metadata?.icon;
        const appName = app.name || 'App';
        
        if (iconPath && iconPath !== 'data/icons/app-icon.png') {
            // Use lazy loading for real icons
            return `<img data-src="${this.escapeHtml(iconPath)}" alt="${this.escapeHtml(appName)} icon" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                    <div style="display:none; width:100%; height:100%; align-items:center; justify-content:center; font-size:1.5rem; background:var(--bg-secondary);">
                        ${this.getAppInitials(appName)}
                    </div>`;
        } else {
            // Fallback to initials
            return `<div style="width:100%; height:100%; display:flex; align-items:center; justify-content:center; font-size:1.5rem; background:var(--bg-secondary); color:var(--text-secondary);">
                        ${this.getAppInitials(appName)}
                    </div>`;
        }
    }

    getAppInitials(name) {
        if (!name) return '📦';
        
        const words = name.trim().split(/\s+/);
        if (words.length === 1) {
            return words[0].charAt(0).toUpperCase();
        } else {
            return words.slice(0, 2).map(word => word.charAt(0).toUpperCase()).join('');
        }
    }

    createCategoryTags(categories) {
        if (!categories || !Array.isArray(categories) || categories.length === 0) {
            return '';
        }

        const tags = categories.slice(0, 3).map(category => 
            `<span class="app-category">${this.escapeHtml(category)}</span>`
        ).join('');

        return `<div class="app-categories">${tags}</div>`;
    }

    createDownloadButtons(app) {
        const buttons = [];
        
        // AppImage download (primary)
        if (app.appimage?.url) {
            buttons.push(`
                <a href="${this.escapeHtml(app.appimage.url)}" 
                   class="download-btn primary" 
                   download
                   title="Download AppImage">
                    <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                    </svg>
                    AppImage
                </a>
            `);
        }

        // Converted packages
        if (app.converted_packages) {
            if (app.converted_packages.deb?.status === 'available') {
                buttons.push(`
                    <a href="${this.escapeHtml(app.converted_packages.deb.url)}" 
                       class="download-btn" 
                       download
                       title="Download Debian package">
                        DEB
                    </a>
                `);
            }
            
            if (app.converted_packages.rpm?.status === 'available') {
                buttons.push(`
                    <a href="${this.escapeHtml(app.converted_packages.rpm.url)}" 
                       class="download-btn" 
                       download
                       title="Download RPM package">
                        RPM
                    </a>
                `);
            }
        }

        return buttons.join('');
    }

    createSourceLink(app) {
        if (!app.source?.repository) {
            return '';
        }

        return `
            <div class="app-source">
                <a href="${this.escapeHtml(app.source.repository)}" 
                   class="source-link" 
                   target="_blank" 
                   rel="noopener noreferrer"
                   title="View source repository">
                    <svg class="icon" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                    </svg>
                    Source
                </a>
            </div>
        `;
    }

    addCardInteractions(card, app) {
        // Add hover effects and click handlers
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-4px)';
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0)';
        });

        // Track card clicks for analytics
        card.addEventListener('click', (e) => {
            // Don't track if clicking on download buttons or links
            if (e.target.closest('a, button')) return;
            
            this.trackCardClick(app);
        });
    }

    renderCategoryFilters() {
        const categoryFilters = document.getElementById('categoryFilters');
        if (!categoryFilters || !this.categories.length) return;

        const fragment = document.createDocumentFragment();
        
        this.categories.forEach(category => {
            const button = document.createElement('button');
            button.className = 'category-filter';
            button.setAttribute('data-category', category.id);
            button.innerHTML = `
                <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    ${this.getCategoryIcon(category.icon)}
                </svg>
                ${this.escapeHtml(category.name)}
                <span class="count">${category.count || 0}</span>
            `;
            fragment.appendChild(button);
        });

        categoryFilters.appendChild(fragment);
    }

    getCategoryIcon(iconName) {
        const icons = {
            'gamepad': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 4a2 2 0 114 0v1a1 1 0 001 1h3a1 1 0 011 1v3a1 1 0 01-1 1h-1a2 2 0 100 4h1a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1v-1a2 2 0 10-4 0v1a1 1 0 01-1 1H7a1 1 0 01-1-1v-3a1 1 0 011-1h1a2 2 0 100-4H7a1 1 0 01-1-1V7a1 1 0 011-1h3a1 1 0 001-1V4z"></path>',
            'code': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"></path>',
            'image': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>',
            'volume-up': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M9 5L5 9H3a1 1 0 00-1 1v4a1 1 0 001 1h2l4 4V5z"></path>',
            'globe': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"></path>',
            'file-text': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>',
            'tool': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>',
            'video': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path>',
            'graduation-cap': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 14l9-5-9-5-9 5 9 5z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z"></path>',
            'package': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path>'
        };
        
        return icons[iconName] || icons['package'];
    }

    loadMoreApplications() {
        if (this.isLoading) return;
        
        this.isLoading = true;
        this.loadMoreBtn.disabled = true;
        this.loadMoreBtn.innerHTML = `
            <div class="loading-spinner"></div>
            Loading...
        `;

        // Simulate loading delay for better UX
        setTimeout(() => {
            const nextBatch = this.applications.slice(
                this.displayedCount, 
                this.displayedCount + this.itemsPerPage
            );
            
            this.renderApplications(nextBatch, true);
            this.updateLoadMoreButton();
            
            this.isLoading = false;
            this.loadMoreBtn.disabled = false;
            this.loadMoreBtn.innerHTML = `
                Load More Applications
            `;
        }, 500);
    }

    updateLoadMoreButton() {
        if (!this.loadMoreContainer) return;

        if (this.displayedCount >= this.applications.length) {
            this.loadMoreContainer.classList.add('hidden');
        } else {
            this.loadMoreContainer.classList.remove('hidden');
        }
    }

    clearGrid() {
        if (this.applicationsGrid) {
            this.applicationsGrid.innerHTML = '';
        }
    }

    showLoading(show = true) {
        if (this.loadingState) {
            this.loadingState.style.display = show ? 'block' : 'none';
        }
    }

    showEmpty(show = true) {
        if (this.emptyState) {
            this.emptyState.style.display = show ? 'block' : 'none';
        }
    }

    updateCardStyles() {
        // Update card styles when theme changes
        const cards = this.applicationsGrid?.querySelectorAll('.app-card');
        if (cards) {
            cards.forEach(card => {
                card.classList.add('theme-transition');
                setTimeout(() => {
                    card.classList.remove('theme-transition');
                }, 300);
            });
        }
    }

    // Utility functions
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    formatFileSize(size) {
        if (!size) return 'Unknown';
        
        // If size is already formatted (contains units), return as is
        if (typeof size === 'string' && /[KMGT]B/i.test(size)) {
            return size;
        }
        
        // Convert bytes to human readable format
        const bytes = parseInt(size);
        if (isNaN(bytes)) return 'Unknown';
        
        const units = ['B', 'KB', 'MB', 'GB'];
        let unitIndex = 0;
        let value = bytes;
        
        while (value >= 1024 && unitIndex < units.length - 1) {
            value /= 1024;
            unitIndex++;
        }
        
        return `${value.toFixed(1)} ${units[unitIndex]}`;
    }

    formatDate(dateString) {
        if (!dateString) return 'Unknown';
        
        try {
            const date = new Date(dateString);
            const now = new Date();
            const diffTime = Math.abs(now - date);
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            
            if (diffDays === 1) return 'Yesterday';
            if (diffDays < 7) return `${diffDays} days ago`;
            if (diffDays < 30) return `${Math.ceil(diffDays / 7)} weeks ago`;
            if (diffDays < 365) return `${Math.ceil(diffDays / 30)} months ago`;
            
            return date.toLocaleDateString();
        } catch {
            return 'Unknown';
        }
    }

    trackCardClick(app) {
        console.log(`Card clicked: ${app.name}`);
        
        // Track in localStorage for basic analytics
        try {
            const clicks = JSON.parse(localStorage.getItem('appbinhub-clicks') || '[]');
            clicks.push({
                appId: app.id,
                appName: app.name,
                timestamp: new Date().toISOString()
            });
            
            // Keep only last 100 clicks
            if (clicks.length > 100) {
                clicks.splice(0, clicks.length - 100);
            }
            
            localStorage.setItem('appbinhub-clicks', JSON.stringify(clicks));
        } catch (err) {
            console.warn('Could not save click analytics:', err);
        }
    }
}

// Initialize catalog manager
const catalogManager = new CatalogManager();

// Export for use in other modules
/* global module */
if (typeof module !== 'undefined' && typeof module.exports !== 'undefined') {
    module.exports = CatalogManager;
} else {
    window.CatalogManager = CatalogManager;
    window.catalogManager = catalogManager;
}

// Add to global AppBinHub namespace
window.AppBinHub = window.AppBinHub || {};
window.AppBinHub.catalog = {
    setApplications: (apps) => catalogManager.setApplicationsData(apps),
    setCategories: (cats) => catalogManager.setCategoriesData(cats),
    render: (apps, append) => catalogManager.renderApplications(apps, append),
    clear: () => catalogManager.clearGrid(),
    showLoading: (show) => catalogManager.showLoading(show),
    showEmpty: (show) => catalogManager.showEmpty(show)
};