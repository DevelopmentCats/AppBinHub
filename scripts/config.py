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
    # Start with an empty list - add only verified working repositories
    # Example format: "owner/repo"
]

# Architecture mapping - shared between monitor and converter
ARCHITECTURE_MAPPING = {
    # Common architecture names to standard names
    'x86_64': 'x86_64',
    'amd64': 'x86_64', 
    'x64': 'x86_64',
    'intel': 'x86_64',
    'i386': 'i386',
    'i686': 'i386',
    '32bit': 'i386',
    'armv7l': 'armv7l',
    'armhf': 'armv7l',
    'arm': 'armv7l',
    'aarch64': 'aarch64',
    'arm64': 'aarch64',
    # Add more as needed
}

# Package format preferences by architecture
PACKAGE_FORMAT_PREFERENCES = {
    'x86_64': ['deb', 'rpm', 'tar.gz'],
    'i386': ['deb', 'rpm', 'tar.gz'],  
    'armv7l': ['deb', 'tar.gz'],  # RPM less common on ARM
    'aarch64': ['deb', 'rpm', 'tar.gz'],
}

# Debian architecture mapping for DEB packages
DEBIAN_ARCH_MAPPING = {
    'x86_64': 'amd64',
    'i386': 'i386',
    'armv7l': 'armhf',
    'aarch64': 'arm64',
}

# RPM architecture mapping for RPM packages
RPM_ARCH_MAPPING = {
    'x86_64': 'x86_64',
    'i386': 'i386',
    'armv7l': 'armv7hl',
    'aarch64': 'aarch64',
}

# Direct API endpoints for applications that don't use GitHub releases
# Now supports dynamic architecture detection
DIRECT_API_ENDPOINTS = {
    "cursor": {
        "name": "Cursor AI Editor",
        "category": "development",
        "description": "AI-powered code editor built for programming with artificial intelligence",
        "website": "https://cursor.com",
        "icon_url": "https://us1.discourse-cdn.com/flex020/uploads/cursor1/original/2X/a/a4f78589d63edd61a2843306f8e11bad9590f0ca.png",
        # Architecture detection patterns - monitor will try these and detect what's available
        "architecture_detection": {
            "base_api_url": "https://www.cursor.com/api/download?releaseTrack=stable",
            "platform_patterns": {
                "x86_64": ["linux-x64", "linux-amd64"],
                "aarch64": ["linux-arm64", "linux-aarch64"],
                "i386": ["linux-x86", "linux-i386"],
                "armv7l": ["linux-arm", "linux-armv7"]
            }
        },
        # Known working architectures (fallback if detection fails)
        "known_architectures": {
            "x86_64": {
                "api_url": "https://www.cursor.com/api/download?platform=linux-x64&releaseTrack=stable"
            }
        }
    }
}

# Additional repositories that commonly host AppImages
COMMON_APPIMAGE_HOSTS = [
    # These are patterns/organizations known to host AppImages
    "probonopd",  # AppImage creator's repositories
    "ivan-hc",    # Known AppImage packager
]

# Conversion tool settings (based on research)
CONVERSION_TOOLS = {
    "unsquashfs": {
        "command": "unsquashfs",
        "install_method": "apt",  # via squashfs-tools package
        "timeout": 60,  # 1 minute for extraction
        "enabled": True,
        "optional": True  # AppImages have built-in extraction, unsquashfs is fallback only
    },
    "dpkg-deb": {
        "command": "dpkg-deb",
        "install_method": "apt",
        "timeout": 30,
        "enabled": True,
        "optional": False
    },
    "rpmbuild": {
        "command": "rpmbuild",
        "install_method": "apt",  # via rpm package
        "timeout": 300,  # 5 minutes
        "enabled": True,
        "optional": True  # Optional since not all distros support RPM
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
    "AudioVideo": "media",
    "Audio": "media",
    "Video": "media",
    "Development": "development",
    "Graphics": "graphics",
    "Office": "productivity",
    "Settings": "utilities",
    "System": "utilities",
    "Utility": "utilities",
    
    # Additional categories
    "Photography": "graphics",
    "Publishing": "productivity",
    "TextEditor": "productivity",
    "IDE": "development",
    "Debugger": "development",
    "WebDevelopment": "development",
    "Programming": "development",  # For our direct API endpoints
    
    # Default fallback
    "": "other"
}

# File size limits (based on GitHub Pages constraints)
MAX_JSON_FILE_SIZE = 1024 * 1024  # 1MB
MAX_TOTAL_REPO_SIZE = 900 * 1024 * 1024  # 900MB (safety margin)
MAX_SINGLE_PACKAGE_SIZE = 100 * 1024 * 1024  # 100MB

# Logging configuration
LOGS_DIR = BASE_DIR.parent / "logs"
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "monitor_log": LOGS_DIR / "monitor.log",
    "converter_log": LOGS_DIR / "converter.log",
    "max_log_size": 10 * 1024 * 1024,  # 10MB
    "backup_count": 5
}

# Ensure logs directory exists
LOGS_DIR.mkdir(parents=True, exist_ok=True)

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

def normalize_architecture(arch_string):
    """Normalize architecture string to standard format"""
    if not arch_string:
        return 'x86_64'  # Default to x86_64
    
    arch_lower = arch_string.lower()
    
    # Direct mapping first
    if arch_lower in ARCHITECTURE_MAPPING:
        return ARCHITECTURE_MAPPING[arch_lower]
    
    # Pattern matching for complex strings
    if any(x in arch_lower for x in ['x86_64', 'amd64', 'x64']):
        return 'x86_64'
    elif any(x in arch_lower for x in ['i386', 'i686', '32bit']):
        return 'i386'
    elif any(x in arch_lower for x in ['aarch64', 'arm64']):
        return 'aarch64'
    elif 'arm' in arch_lower:
        return 'armv7l'
    
    # Default fallback
    return 'x86_64'

def detect_architecture_from_url(url):
    """Detect architecture from URL patterns"""
    if not url:
        return 'x86_64'
    
    url_lower = url.lower()
    
    # Common URL patterns
    if any(x in url_lower for x in ['x86_64', 'amd64', 'x64', 'intel']):
        return 'x86_64'
    elif any(x in url_lower for x in ['i386', 'i686', '32bit']):
        return 'i386'
    elif any(x in url_lower for x in ['aarch64', 'arm64']):
        return 'aarch64'
    elif 'arm' in url_lower:
        return 'armv7l'
    
    return 'x86_64'

def get_package_formats_for_arch(architecture):
    """Get preferred package formats for an architecture"""
    return PACKAGE_FORMAT_PREFERENCES.get(architecture, ['tar.gz'])

def get_debian_arch(architecture):
    """Get Debian architecture name for a standard architecture"""
    return DEBIAN_ARCH_MAPPING.get(architecture, architecture)

def get_rpm_arch(architecture):
    """Get RPM architecture name for a standard architecture"""
    return RPM_ARCH_MAPPING.get(architecture, architecture)

def generate_version_path(app_id, version):
    """Generate versioned path for converted packages"""
    return CONVERTED_PACKAGES_DIR / app_id / version

def get_available_architectures_for_app(app_config):
    """Get list of available architectures for an application"""
    # For new config format with detection patterns
    if 'architecture_detection' in app_config:
        return list(app_config['architecture_detection']['platform_patterns'].keys())
    # For old config format with explicit architectures
    elif 'architectures' in app_config:
        return list(app_config['architectures'].keys())
    # For known architectures fallback
    elif 'known_architectures' in app_config:
        return list(app_config['known_architectures'].keys())
    return ['x86_64']  # Default to x86_64 if no architecture info

def build_api_url_for_architecture(app_config, architecture):
    """Build API URL for a specific architecture"""
    # Try architecture detection patterns first
    if 'architecture_detection' in app_config:
        base_url = app_config['architecture_detection']['base_api_url']
        patterns = app_config['architecture_detection']['platform_patterns'].get(architecture, [])
        
        # Try each platform pattern for this architecture
        for pattern in patterns:
            url = f"{base_url}&platform={pattern}"
            yield url
    
    # Fallback to known architectures
    if 'known_architectures' in app_config and architecture in app_config['known_architectures']:
        yield app_config['known_architectures'][architecture]['api_url']
    
    # Fallback to old format
    if 'architectures' in app_config and architecture in app_config['architectures']:
        yield app_config['architectures'][architecture]['api_url']

def detect_available_architectures_from_api(app_config):
    """Dynamically detect which architectures are actually available from the API"""
    import requests
    available_architectures = []
    
    potential_architectures = get_available_architectures_for_app(app_config)
    
    for architecture in potential_architectures:
        # Try each possible API URL for this architecture
        for api_url in build_api_url_for_architecture(app_config, architecture):
            try:
                response = requests.head(api_url, timeout=10)
                if response.status_code == 200:
                    available_architectures.append((architecture, api_url))
                    break  # Found working URL for this arch, move to next
            except:
                continue  # Try next URL pattern
    
    return available_architectures

def should_create_package_format(architecture, package_format):
    """Check if a package format should be created for an architecture"""
    preferred_formats = get_package_formats_for_arch(architecture)
    return package_format in preferred_formats

# Export commonly used configurations
__all__ = [
    'APPIMAGE_REPOSITORIES',
    'DIRECT_API_ENDPOINTS',
    'CONVERSION_TOOLS',
    'CATEGORY_MAPPING',
    'ARCHITECTURE_MAPPING',
    'PACKAGE_FORMAT_PREFERENCES',
    'DEBIAN_ARCH_MAPPING',
    'RPM_ARCH_MAPPING',
    'WEBSITE_DATA_DIR',
    'CONVERTED_PACKAGES_DIR',
    'LOGGING_CONFIG',
    'LOGS_DIR',
    'get_github_token',
    'ensure_directories',
    'map_desktop_category',
    'is_valid_appimage_url',
    'normalize_architecture',
    'detect_architecture_from_url',
    'get_package_formats_for_arch',
    'get_debian_arch',
    'get_rpm_arch',
    'generate_version_path',
    'get_available_architectures_for_app',
    'build_api_url_for_architecture',
    'detect_available_architectures_from_api',
    'should_create_package_format'
]