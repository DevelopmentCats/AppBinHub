#!/usr/bin/env python3
"""
Configuration file for AppBinHub automation scripts
Contains settings and repository lists based on research
"""

import os
from pathlib import Path

# GitHub API Configuration
GITHUB_API_BASE_URL = "https://api.github.com"
GITHUB_TOKEN_ENV_VAR = "GITHUB_TOKEN"

# Rate limiting settings (based on GitHub API research)
GITHUB_API_RATE_LIMIT_THRESHOLD = 100  # Minimum requests before stopping
GITHUB_API_REQUEST_TIMEOUT = 30  # seconds

# File paths
BASE_DIR = Path(__file__).parent
WEBSITE_DATA_DIR = BASE_DIR.parent / "website" / "data"
CONVERTED_PACKAGES_DIR = BASE_DIR / "converted_packages"
LOG_DIR = BASE_DIR

# Data files
APPLICATIONS_JSON = WEBSITE_DATA_DIR / "applications.json"
CATEGORIES_JSON = WEBSITE_DATA_DIR / "categories.json"
CHANGELOG_JSON = WEBSITE_DATA_DIR / "changelog.json"

# AppImage repositories to monitor (based on research)
APPIMAGE_REPOSITORIES = [
    # Core AppImage repositories
    "AppImage/AppImageKit",
    "AppImage/appimagetool",
    
    # AppImageCommunity repositories with actual AppImages
    "AppImageCommunity/pkg2appimage",
    "AppImageCommunity/AppImageUpdate",
    "AppImageCommunity/libappimage",
    
    # Popular AppImage applications (examples from research)
    # Note: These would be populated by actual repository discovery
    # during the monitoring process
]

# Additional repositories that commonly host AppImages
COMMON_APPIMAGE_HOSTS = [
    # These are patterns/organizations known to host AppImages
    "probonopd",  # AppImage creator's repositories
    "ivan-hc",    # Known AppImage packager
]

# Conversion tool settings (based on research)
CONVERSION_TOOLS = {
    "appimage2deb": {
        "command": "appimage2deb",
        "install_method": "snap",
        "timeout": 300,  # 5 minutes
        "enabled": True
    },
    "alien": {
        "command": "alien",
        "install_method": "apt",
        "timeout": 300,  # 5 minutes
        "enabled": True
    },
    "dpkg-deb": {
        "command": "dpkg-deb",
        "install_method": "apt",
        "timeout": 30,
        "enabled": True
    }
}

# AppImage extraction settings
APPIMAGE_EXTRACTION = {
    "timeout": 60,  # seconds
    "temp_dir_prefix": "appbinhub_",
    "extract_command": "--appimage-extract",
    "squashfs_root_dir": "squashfs-root"
}

# Desktop file parsing settings
DESKTOP_FILE_SETTINGS = {
    "encoding": "utf-8",
    "section": "Desktop Entry",
    "required_fields": ["Name"],
    "optional_fields": ["Comment", "Exec", "Icon", "Categories", "MimeType"]
}

# Category mapping (based on FreeDesktop.org specification)
CATEGORY_MAPPING = {
    # Main categories from FreeDesktop.org
    "AudioVideo": "audio",
    "Audio": "audio",
    "Video": "video",
    "Development": "programming",
    "Education": "education",
    "Game": "games",
    "Graphics": "graphics",
    "Network": "internet",
    "Office": "office",
    "Science": "education",
    "Settings": "utilities",
    "System": "utilities",
    "Utility": "utilities",
    
    # Additional categories
    "Photography": "graphics",
    "Publishing": "office",
    "WebBrowser": "internet",
    "TextEditor": "office",
    "IDE": "programming",
    "Debugger": "programming",
    "WebDevelopment": "programming",
    
    # Default fallback
    "": "other"
}

# File size limits (based on GitHub Pages constraints)
MAX_JSON_FILE_SIZE = 1024 * 1024  # 1MB
MAX_TOTAL_REPO_SIZE = 900 * 1024 * 1024  # 900MB (safety margin)
MAX_SINGLE_PACKAGE_SIZE = 100 * 1024 * 1024  # 100MB

# Logging configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "monitor_log": LOG_DIR / "monitor.log",
    "converter_log": LOG_DIR / "converter.log",
    "max_log_size": 10 * 1024 * 1024,  # 10MB
    "backup_count": 5
}

# Network settings
NETWORK_SETTINGS = {
    "user_agent": "AppBinHub/1.0 (https://github.com/appbinhub/appbinhub)",
    "request_timeout": 30,
    "download_timeout": 300,
    "max_retries": 3,
    "retry_delay": 5  # seconds
}

# Validation settings
VALIDATION_SETTINGS = {
    "min_appimage_size": 1024 * 1024,  # 1MB minimum
    "max_appimage_size": 500 * 1024 * 1024,  # 500MB maximum
    "required_appimage_extensions": [".AppImage", ".appimage"],
    "validate_checksums": True,
    "validate_desktop_files": True
}

def get_github_token():
    """Get GitHub token from environment variable"""
    token = os.environ.get(GITHUB_TOKEN_ENV_VAR)
    if not token:
        raise ValueError(f"{GITHUB_TOKEN_ENV_VAR} environment variable is required")
    return token

def ensure_directories():
    """Ensure all required directories exist"""
    directories = [
        WEBSITE_DATA_DIR,
        CONVERTED_PACKAGES_DIR,
        LOG_DIR
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

def get_conversion_tool_config(tool_name):
    """Get configuration for a specific conversion tool"""
    return CONVERSION_TOOLS.get(tool_name, {})

def map_desktop_category(desktop_category):
    """Map desktop file category to AppBinHub category"""
    if not desktop_category:
        return "other"
    
    # Try exact match first
    if desktop_category in CATEGORY_MAPPING:
        return CATEGORY_MAPPING[desktop_category]
    
    # Try partial matches for compound categories
    for key, value in CATEGORY_MAPPING.items():
        if key and key in desktop_category:
            return value
    
    return "other"

def is_valid_appimage_url(url):
    """Check if URL appears to be a valid AppImage download"""
    if not url:
        return False
    
    url_lower = url.lower()
    return any(ext in url_lower for ext in VALIDATION_SETTINGS["required_appimage_extensions"])

# Export commonly used configurations
__all__ = [
    'APPIMAGE_REPOSITORIES',
    'CONVERSION_TOOLS',
    'CATEGORY_MAPPING',
    'WEBSITE_DATA_DIR',
    'get_github_token',
    'ensure_directories',
    'map_desktop_category',
    'is_valid_appimage_url'
]