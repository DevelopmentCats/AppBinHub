/**
 * AppBinHub Search and Filter Management
 * Handles real-time search, category filtering, and sorting functionality
 */

class SearchManager {
    constructor() {
        this.searchInput = null;
        this.categoryFilters = null;
        this.sortSelect = null;
        this.applicationsData = [];
        this.filteredData = [];
        this.currentQuery = '';
        this.currentCategory = 'all';
        this.currentSort = 'name';
        this.searchTimeout = null;
        this.callbacks = {
            onResultsUpdate: null
        };
        
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
        this.searchInput = document.getElementById('searchInput');
        this.categoryFilters = document.getElementById('categoryFilters');
        this.sortSelect = document.getElementById('sortSelect');
        
        if (!this.searchInput) {
            console.warn('Search input not found');
            return;
        }

        this.setupEventListeners();
        this.setupKeyboardShortcuts();
    }

    setupEventListeners() {
        // Search input with debouncing
        if (this.searchInput) {
            this.searchInput.addEventListener('input', (e) => {
                clearTimeout(this.searchTimeout);
                this.searchTimeout = setTimeout(() => {
                    this.handleSearch(e.target.value);
                }, 300);
            });

            // Clear search on Escape key
            this.searchInput.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    this.clearSearch();
                }
            });
        }

        // Category filters
        if (this.categoryFilters) {
            this.categoryFilters.addEventListener('click', (e) => {
                if (e.target.classList.contains('category-filter')) {
                    this.handleCategoryFilter(e.target.dataset.category);
                    this.updateActiveFilter(e.target);
                }
            });
        }

        // Sort selection
        if (this.sortSelect) {
            this.sortSelect.addEventListener('change', (e) => {
                this.handleSort(e.target.value);
            });
        }

        // Handle "All Categories" filter
        const allCategoriesFilter = document.querySelector('.category-filter[data-category="all"]');
        if (allCategoriesFilter) {
            allCategoriesFilter.addEventListener('click', () => {
                this.handleCategoryFilter('all');
                this.updateActiveFilter(allCategoriesFilter);
            });
        }
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Focus search with Ctrl/Cmd + K
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                if (this.searchInput) {
                    this.searchInput.focus();
                }
            }

            // Clear search with Ctrl/Cmd + Backspace
            if ((e.ctrlKey || e.metaKey) && e.key === 'Backspace') {
                if (document.activeElement === this.searchInput) {
                    e.preventDefault();
                    this.clearSearch();
                }
            }
        });
    }

    setApplicationsData(data) {
        this.applicationsData = Array.isArray(data) ? data : [];
        this.filteredData = [...this.applicationsData];
        this.applyCurrentFilters();
    }

    handleSearch(query) {
        this.currentQuery = query.toLowerCase().trim();
        this.applyCurrentFilters();
        
        // Update URL without page reload
        this.updateURL();
        
        // Track search analytics
        this.trackSearch(query);
    }

    handleCategoryFilter(category) {
        this.currentCategory = category;
        this.applyCurrentFilters();
        this.updateURL();
    }

    handleSort(sortBy) {
        this.currentSort = sortBy;
        this.applySorting();
        this.triggerResultsUpdate();
    }

    applyCurrentFilters() {
        let filtered = [...this.applicationsData];

        // Apply search filter
        if (this.currentQuery) {
            filtered = filtered.filter(app => {
                const searchableText = [
                    app.name || '',
                    app.description || '',
                    ...(app.category || []),
                    app.id || ''
                ].join(' ').toLowerCase();
                
                return searchableText.includes(this.currentQuery);
            });
        }

        // Apply category filter
        if (this.currentCategory && this.currentCategory !== 'all') {
            filtered = filtered.filter(app => {
                if (!app.category || !Array.isArray(app.category)) {
                    return false;
                }
                return app.category.some(cat => 
                    cat.toLowerCase() === this.currentCategory.toLowerCase()
                );
            });
        }

        this.filteredData = filtered;
        this.applySorting();
    }

    applySorting() {
        switch (this.currentSort) {
            case 'name':
                this.filteredData.sort((a, b) => {
                    const nameA = (a.name || '').toLowerCase();
                    const nameB = (b.name || '').toLowerCase();
                    return nameA.localeCompare(nameB);
                });
                break;
                
            case 'date':
                this.filteredData.sort((a, b) => {
                    const dateA = new Date(a.last_updated || a.source?.release_date || 0);
                    const dateB = new Date(b.last_updated || b.source?.release_date || 0);
                    return dateB - dateA; // Newest first
                });
                break;
                
            case 'category':
                this.filteredData.sort((a, b) => {
                    const catA = (a.category && a.category[0]) ? a.category[0].toLowerCase() : 'zzz';
                    const catB = (b.category && b.category[0]) ? b.category[0].toLowerCase() : 'zzz';
                    if (catA === catB) {
                        const nameA = (a.name || '').toLowerCase();
                        const nameB = (b.name || '').toLowerCase();
                        return nameA.localeCompare(nameB);
                    }
                    return catA.localeCompare(catB);
                });
                break;
                
            default:
                // Default to name sorting
                this.applySorting.call(this, 'name');
        }

        this.triggerResultsUpdate();
    }

    updateActiveFilter(activeElement) {
        // Remove active class from all filters
        const allFilters = document.querySelectorAll('.category-filter');
        allFilters.forEach(filter => {
            filter.classList.remove('active');
        });

        // Add active class to clicked filter
        if (activeElement) {
            activeElement.classList.add('active');
        }
    }

    clearSearch() {
        if (this.searchInput) {
            this.searchInput.value = '';
            this.currentQuery = '';
            this.applyCurrentFilters();
            this.updateURL();
        }
    }

    getFilteredResults() {
        return this.filteredData;
    }

    getSearchStats() {
        return {
            total: this.applicationsData.length,
            filtered: this.filteredData.length,
            query: this.currentQuery,
            category: this.currentCategory,
            sort: this.currentSort
        };
    }

    // Set callback for when results are updated
    onResultsUpdate(callback) {
        this.callbacks.onResultsUpdate = callback;
    }

    triggerResultsUpdate() {
        if (this.callbacks.onResultsUpdate) {
            this.callbacks.onResultsUpdate(this.filteredData, this.getSearchStats());
        }
    }

    // URL management for bookmarkable searches
    updateURL() {
        if (!window.history || !window.history.pushState) return;

        const params = new URLSearchParams();
        
        if (this.currentQuery) {
            params.set('q', this.currentQuery);
        }
        
        if (this.currentCategory && this.currentCategory !== 'all') {
            params.set('category', this.currentCategory);
        }
        
        if (this.currentSort && this.currentSort !== 'name') {
            params.set('sort', this.currentSort);
        }

        const newURL = params.toString() ? 
            `${window.location.pathname}?${params.toString()}` : 
            window.location.pathname;

        window.history.replaceState(null, '', newURL);
    }

    // Load state from URL parameters
    loadFromURL() {
        const params = new URLSearchParams(window.location.search);
        
        const query = params.get('q');
        if (query && this.searchInput) {
            this.searchInput.value = query;
            this.currentQuery = query.toLowerCase().trim();
        }
        
        const category = params.get('category');
        if (category) {
            this.currentCategory = category;
            // Update active filter button
            const filterButton = document.querySelector(`[data-category="${category}"]`);
            if (filterButton) {
                this.updateActiveFilter(filterButton);
            }
        }
        
        const sort = params.get('sort');
        if (sort && this.sortSelect) {
            this.sortSelect.value = sort;
            this.currentSort = sort;
        }

        this.applyCurrentFilters();
    }

    // Search suggestions and autocomplete
    getSearchSuggestions(query) {
        if (!query || query.length < 2) return [];

        const suggestions = new Set();
        const queryLower = query.toLowerCase();

        this.applicationsData.forEach(app => {
            // Add matching app names
            if (app.name && app.name.toLowerCase().includes(queryLower)) {
                suggestions.add(app.name);
            }

            // Add matching categories
            if (app.category && Array.isArray(app.category)) {
                app.category.forEach(cat => {
                    if (cat.toLowerCase().includes(queryLower)) {
                        suggestions.add(cat);
                    }
                });
            }
        });

        return Array.from(suggestions).slice(0, 5);
    }

    // Analytics tracking
    trackSearch(query) {
        // Simple analytics tracking - can be extended with real analytics
        if (query && query.length > 0) {
            console.log(`Search performed: "${query}"`);
            
            // Track in localStorage for basic analytics
            try {
                const searches = JSON.parse(localStorage.getItem('appbinhub-searches') || '[]');
                searches.push({
                    query: query,
                    timestamp: new Date().toISOString(),
                    results: this.filteredData.length
                });
                
                // Keep only last 100 searches
                if (searches.length > 100) {
                    searches.splice(0, searches.length - 100);
                }
                
                localStorage.setItem('appbinhub-searches', JSON.stringify(searches));
            } catch (error) {
                console.warn('Could not save search analytics:', error);
            }
        }
    }

    // Get popular searches
    getPopularSearches() {
        try {
            const searches = JSON.parse(localStorage.getItem('appbinhub-searches') || '[]');
            const queryCount = {};
            
            searches.forEach(search => {
                queryCount[search.query] = (queryCount[search.query] || 0) + 1;
            });
            
            return Object.entries(queryCount)
                .sort(([,a], [,b]) => b - a)
                .slice(0, 5)
                .map(([query]) => query);
        } catch {
            return [];
        }
    }

    // Reset all filters
    resetFilters() {
        this.clearSearch();
        this.currentCategory = 'all';
        this.currentSort = 'name';
        
        if (this.sortSelect) {
            this.sortSelect.value = 'name';
        }
        
        // Reset active filter
        const allFilter = document.querySelector('.category-filter[data-category="all"]');
        if (allFilter) {
            this.updateActiveFilter(allFilter);
        }
        
        this.applyCurrentFilters();
        this.updateURL();
    }
}

// Initialize search manager
const searchManager = new SearchManager();

// Export for use in other modules
/* global module */
if (typeof module !== 'undefined' && typeof module.exports !== 'undefined') {
    module.exports = SearchManager;
} else {
    window.SearchManager = SearchManager;
    window.searchManager = searchManager;
}

// Add to global AppBinHub namespace
window.AppBinHub = window.AppBinHub || {};
window.AppBinHub.search = {
    setData: (data) => searchManager.setApplicationsData(data),
    getResults: () => searchManager.getFilteredResults(),
    getStats: () => searchManager.getSearchStats(),
    onUpdate: (callback) => searchManager.onResultsUpdate(callback),
    loadFromURL: () => searchManager.loadFromURL(),
    resetFilters: () => searchManager.resetFilters(),
    getSuggestions: (query) => searchManager.getSearchSuggestions(query),
    getPopularSearches: () => searchManager.getPopularSearches()
};