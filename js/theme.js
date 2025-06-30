/**
 * AppBinHub Theme Management
 * Handles dark/light theme switching with localStorage persistence
 */

class ThemeManager {
    constructor() {
        this.themeToggle = null;
        this.currentTheme = 'light';
        this.init();
    }

    init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            this.setup();
        }
    }

    setup() {
        this.themeToggle = document.getElementById('themeToggle');
        
        if (!this.themeToggle) {
            console.warn('Theme toggle button not found');
            return;
        }

        // Load saved theme or detect system preference
        this.loadTheme();
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Apply initial theme
        this.applyTheme(this.currentTheme);
    }

    setupEventListeners() {
        // Theme toggle button click
        this.themeToggle.addEventListener('click', () => {
            this.toggleTheme();
        });

        // Listen for system theme changes
        if (window.matchMedia) {
            const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            mediaQuery.addEventListener('change', (e) => {
                // Only auto-switch if user hasn't manually set a preference
                if (!localStorage.getItem('appbinhub-theme')) {
                    this.currentTheme = e.matches ? 'dark' : 'light';
                    this.applyTheme(this.currentTheme);
                }
            });
        }

        // Keyboard shortcut (Ctrl/Cmd + Shift + T)
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'T') {
                e.preventDefault();
                this.toggleTheme();
            }
        });
    }

    loadTheme() {
        // Check localStorage first
        const savedTheme = localStorage.getItem('appbinhub-theme');
        
        if (savedTheme && (savedTheme === 'light' || savedTheme === 'dark')) {
            this.currentTheme = savedTheme;
        } else {
            // Detect system preference
            if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
                this.currentTheme = 'dark';
            } else {
                this.currentTheme = 'light';
            }
        }
    }

    toggleTheme() {
        this.currentTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.applyTheme(this.currentTheme);
        this.saveTheme();
        
        // Dispatch custom event for other components
        window.dispatchEvent(new CustomEvent('themeChanged', {
            detail: { theme: this.currentTheme }
        }));
    }

    applyTheme(theme) {
        const html = document.documentElement;
        const body = document.body;
        
        if (theme === 'dark') {
            html.classList.add('dark-mode');
            body.classList.add('dark');
        } else {
            html.classList.remove('dark-mode');
            body.classList.remove('dark');
        }

        // Update theme toggle button aria-label
        if (this.themeToggle) {
            this.themeToggle.setAttribute('aria-label', 
                theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'
            );
        }

        // Update meta theme-color for mobile browsers
        this.updateMetaThemeColor(theme);
        
        // Smooth transition effect
        this.addTransitionClass();
    }

    addTransitionClass() {
        const elements = document.querySelectorAll('*');
        elements.forEach(el => {
            el.classList.add('theme-transition');
        });
        
        // Remove transition class after animation completes
        setTimeout(() => {
            elements.forEach(el => {
                el.classList.remove('theme-transition');
            });
        }, 300);
    }

    updateMetaThemeColor(theme) {
        let metaThemeColor = document.querySelector('meta[name="theme-color"]');
        
        if (!metaThemeColor) {
            metaThemeColor = document.createElement('meta');
            metaThemeColor.name = 'theme-color';
            document.head.appendChild(metaThemeColor);
        }
        
        metaThemeColor.content = theme === 'dark' ? '#121212' : '#ffffff';
    }

    saveTheme() {
        try {
            localStorage.setItem('appbinhub-theme', this.currentTheme);
        } catch (error) {
            console.warn('Could not save theme preference:', error);
        }
    }

    getCurrentTheme() {
        return this.currentTheme;
    }

    setTheme(theme) {
        if (theme === 'light' || theme === 'dark') {
            this.currentTheme = theme;
            this.applyTheme(theme);
            this.saveTheme();
            
            window.dispatchEvent(new CustomEvent('themeChanged', {
                detail: { theme: this.currentTheme }
            }));
        }
    }

    // Method to get CSS custom property values for the current theme
    getThemeColors() {
        const computedStyle = getComputedStyle(document.documentElement);
        
        return {
            bgPrimary: computedStyle.getPropertyValue('--bg-primary').trim(),
            bgSecondary: computedStyle.getPropertyValue('--bg-secondary').trim(),
            textPrimary: computedStyle.getPropertyValue('--text-primary').trim(),
            textSecondary: computedStyle.getPropertyValue('--text-secondary').trim(),
            accentPrimary: computedStyle.getPropertyValue('--accent-primary').trim(),
            borderColor: computedStyle.getPropertyValue('--border-color').trim()
        };
    }

    // Method to check if dark mode is preferred by system
    static isSystemDarkMode() {
        return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    }

    // Method to check if user has set a manual preference
    static hasManualPreference() {
        return localStorage.getItem('appbinhub-theme') !== null;
    }
}

// Initialize theme manager
const themeManager = new ThemeManager();

// Export for use in other modules
/* global module */
if (typeof module !== 'undefined' && typeof module.exports !== 'undefined') {
    module.exports = ThemeManager;
} else {
    window.ThemeManager = ThemeManager;
    window.themeManager = themeManager;
}

// Utility functions for theme-aware components
window.AppBinHub = window.AppBinHub || {};
window.AppBinHub.theme = {
    getCurrentTheme: () => themeManager.getCurrentTheme(),
    setTheme: (theme) => themeManager.setTheme(theme),
    getThemeColors: () => themeManager.getThemeColors(),
    isSystemDarkMode: ThemeManager.isSystemDarkMode,
    hasManualPreference: ThemeManager.hasManualPreference,
    
    // Event listener helper
    onThemeChange: (callback) => {
        window.addEventListener('themeChanged', (e) => {
            callback(e.detail.theme);
        });
    }
};