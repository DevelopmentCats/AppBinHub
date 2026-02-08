#!/usr/bin/env python3
"""
AppImage Repository Monitor Script for AppBinHub
Monitors GitHub repositories and direct API endpoints for AppImage releases and extracts metadata
"""

import os
import json
import requests
import subprocess
import tempfile
import shutil
import logging
from datetime import datetime, timezone
from pathlib import Path
from github import Github
from configparser import ConfigParser
import hashlib
import platform

# Import configuration
from config import (
    APPIMAGE_REPOSITORIES,
    DIRECT_API_ENDPOINTS,
    WEBSITE_DATA_DIR,
    CATEGORY_MAPPING,
    LOGGING_CONFIG,
    get_github_token,
    ensure_directories,
    map_desktop_category,
    is_valid_appimage_url,
    normalize_architecture,
    detect_architecture_from_url,
    get_available_architectures_for_app,
    build_api_url_for_architecture,
    detect_available_architectures_from_api,
    generate_version_path
)

# Configure logging using config
logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG["level"]),
    format=LOGGING_CONFIG["format"],
    handlers=[
        logging.FileHandler(LOGGING_CONFIG["monitor_log"]),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AppImageMonitor:
    def __init__(self):
        # Ensure required directories exist
        ensure_directories()
        
        # Initialize GitHub API (only if we have repositories to monitor)
        if APPIMAGE_REPOSITORIES:
            self.github_token = get_github_token()
            self.github = Github(self.github_token)
        else:
            self.github = None
        
        self.data_dir = WEBSITE_DATA_DIR
        
        # Load existing application data
        self.applications_file = self.data_dir / 'applications.json'
        self.load_existing_data()
    
    def load_existing_data(self):
        """Load existing application data from JSON file"""
        if self.applications_file.exists():
            with open(self.applications_file, 'r') as f:
                self.data = json.load(f)
            # Ensure metadata exists (backwards compatibility)
            if 'metadata' not in self.data:
                self.data['metadata'] = {
                    "last_updated": datetime.now(timezone.utc).isoformat(),
                    "total_applications": len(self.data.get('applications', [])),
                    "version": "1.0.0"
                }
        else:
            self.data = {
                "metadata": {
                    "last_updated": datetime.now(timezone.utc).isoformat(),
                    "total_applications": 0,
                    "version": "1.0.0"
                },
                "applications": []
            }
    
    def check_rate_limits(self):
        """Check GitHub API rate limits"""
        if not self.github:
            return True
            
        rate_limit = self.github.get_rate_limit()
        remaining = rate_limit.core.remaining
        logger.info(f"GitHub API rate limit: {remaining} requests remaining")
        
        if remaining < 100:
            reset_time = rate_limit.core.reset
            logger.warning(f"Rate limit low. Resets at {reset_time}")
            return False
        return True
    
    def get_repository_releases(self, repo_name):
        """Get releases from a GitHub repository"""
        try:
            repo = self.github.get_repo(repo_name)
            releases = repo.get_releases()
            return list(releases)
        except Exception as e:
            logger.error(f"Error fetching releases for {repo_name}: {e}")
            return []
    
    def find_appimage_assets(self, release):
        """Find AppImage files in release assets"""
        appimage_assets = []
        for asset in release.get_assets():
            if asset.name.lower().endswith('.appimage'):
                appimage_assets.append(asset)
        return appimage_assets
    
    def fetch_direct_api_data_for_architecture(self, app_config, architecture, arch_config):
        """Fetch AppImage data from direct API endpoints for a specific architecture"""
        try:
            response = requests.get(arch_config['api_url'], timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Extract download URL
            download_url = data.get('downloadUrl') or data.get('url')
            if not download_url or not is_valid_appimage_url(download_url):
                logger.error(f"Invalid or missing AppImage URL in API response for {app_config['name']} ({architecture})")
                return None
            
            # Verify architecture matches expected
            detected_arch = detect_architecture_from_url(download_url)
            normalized_arch = normalize_architecture(detected_arch)
            if normalized_arch != architecture:
                logger.warning(f"Architecture mismatch for {app_config['name']}: expected {architecture}, detected {normalized_arch}")
            
            # Get file size by making a HEAD request
            head_response = requests.head(download_url)
            file_size = int(head_response.headers.get('content-length', 0))
            
            return {
                'version': data.get('version', 'latest'),
                'download_url': download_url,
                'file_size': file_size,
                'commit_sha': data.get('commitSha'),
                'architecture': architecture,
                'app_config': app_config,
                'arch_config': arch_config
            }
            
        except Exception as e:
            logger.error(f"Error fetching data from {arch_config['api_url']} for {architecture}: {e}")
            return None
    
    def fetch_direct_api_data(self, app_config):
        """Fetch AppImage data from direct API endpoints with dynamic architecture detection"""
        results = []
        
        # First, try to dynamically detect available architectures
        logger.info(f"Detecting available architectures for {app_config['name']}...")
        available_archs = detect_available_architectures_from_api(app_config)
        
        if not available_archs:
            logger.warning(f"No architectures auto-detected for {app_config['name']}, using fallback")
            # Fallback to static configuration
            architectures = get_available_architectures_for_app(app_config)
            for architecture in architectures:
                for api_url in build_api_url_for_architecture(app_config, architecture):
                    arch_config = {'api_url': api_url}
                    api_data = self.fetch_direct_api_data_for_architecture(app_config, architecture, arch_config)
                    if api_data:
                        results.append(api_data)
                        break  # Found working API URL for this arch
        else:
            logger.info(f"Detected {len(available_archs)} available architectures: {[arch for arch, _ in available_archs]}")
            # Use detected architectures
            for architecture, api_url in available_archs:
                arch_config = {'api_url': api_url}
                api_data = self.fetch_direct_api_data_for_architecture(app_config, architecture, arch_config)
                if api_data:
                    results.append(api_data)
        
        return results
    
    def download_appimage(self, asset_url, temp_dir):
        """Download AppImage file to temporary directory"""
        try:
            response = requests.get(asset_url, stream=True, timeout=300)
            response.raise_for_status()
            
            filename = asset_url.split('/')[-1]
            filepath = temp_dir / filename
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Make executable
            os.chmod(filepath, 0o755)
            return filepath
        except Exception as e:
            logger.error(f"Error downloading AppImage: {e}")
            return None
    
    def extract_appimage_metadata(self, appimage_path):
        """Extract metadata from AppImage file"""
        try:
            # Check if we can execute this AppImage (architecture compatibility)
            detected_arch = detect_architecture_from_url(str(appimage_path))
            current_arch = normalize_architecture(platform.machine())
            
            # Skip extraction for cross-architecture AppImages to avoid execution errors
            if detected_arch != current_arch:
                logger.info(f"Skipping metadata extraction for cross-architecture AppImage ({detected_arch} on {current_arch})")
                return {
                    'name': '',
                    'description': '',
                    'executable': '',
                    'icon': '',
                    'categories': [],
                    'mime_types': [],
                    'cross_architecture_skip': True
                }
            
            # Extract AppImage contents
            extract_dir = appimage_path.parent / 'extracted'
            extract_dir.mkdir(exist_ok=True)
            
            # Run AppImage with --appimage-extract
            result = subprocess.run(
                [str(appimage_path), '--appimage-extract'],
                cwd=extract_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                logger.error(f"Failed to extract AppImage: {result.stderr}")
                return None
            
            # Look for .desktop file
            squashfs_root = extract_dir / 'squashfs-root'
            desktop_files = list(squashfs_root.glob('*.desktop'))
            
            if not desktop_files:
                logger.warning("No .desktop file found in AppImage")
                return None
            
            # Parse .desktop file
            desktop_file = desktop_files[0]
            return self.parse_desktop_file(desktop_file, squashfs_root)
            
        except Exception as e:
            logger.error(f"Error extracting AppImage metadata: {e}")
            return None
    
    def parse_desktop_file(self, desktop_file, squashfs_root):
        """Parse .desktop file and extract metadata"""
        try:
            # Use RawConfigParser to avoid interpolation issues with field codes like %F
            config = ConfigParser(interpolation=None)
            config.read(desktop_file, encoding='utf-8')
            
            if 'Desktop Entry' not in config:
                return None
            
            entry = config['Desktop Entry']
            
            metadata = {
                'name': entry.get('Name', ''),
                'description': entry.get('Comment', ''),
                'executable': entry.get('Exec', ''),
                'icon': entry.get('Icon', ''),
                'categories': entry.get('Categories', '').split(';') if entry.get('Categories') else [],
                'mime_types': entry.get('MimeType', '').split(';') if entry.get('MimeType') else []
            }
            
            # Clean up categories (remove empty strings)
            metadata['categories'] = [cat for cat in metadata['categories'] if cat]
            metadata['mime_types'] = [mime for mime in metadata['mime_types'] if mime]
            
            # Look for icon file
            if metadata['icon']:
                icon_path = self.find_icon_file(squashfs_root, metadata['icon'])
                if icon_path:
                    metadata['icon_path'] = str(icon_path)
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error parsing .desktop file: {e}")
            return None
    
    def find_icon_file(self, squashfs_root, icon_name):
        """Find icon file in extracted AppImage"""
        # Common icon locations
        icon_dirs = [
            squashfs_root,
            squashfs_root / 'usr' / 'share' / 'icons',
            squashfs_root / 'usr' / 'share' / 'pixmaps'
        ]
        
        # Common icon extensions
        extensions = ['.png', '.svg', '.xpm', '.ico']
        
        for icon_dir in icon_dirs:
            if not icon_dir.exists():
                continue
                
            # Try exact match first
            for ext in extensions:
                icon_file = icon_dir / f"{icon_name}{ext}"
                if icon_file.exists():
                    return icon_file
            
            # Try recursive search
            for ext in extensions:
                matches = list(icon_dir.rglob(f"{icon_name}{ext}"))
                if matches:
                    return matches[0]
        
        return None
    
    def calculate_file_checksum(self, filepath):
        """Calculate SHA256 checksum of file"""
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def format_file_size(self, size_bytes):
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def create_application_record_from_github(self, repo_name, release, asset, metadata, appimage_path):
        """Create application record from GitHub release data"""
        app_id = f"{repo_name.replace('/', '-')}-{asset.name.replace('.AppImage', '').lower()}"
        
        record = {
            "id": app_id,
            "name": metadata.get('name', asset.name.replace('.AppImage', '')),
            "description": metadata.get('description', ''),
            "version": release.tag_name,
            "category": [map_desktop_category(cat) for cat in metadata.get('categories', [])],
            "appimage": {
                "url": asset.browser_download_url,
                "size": self.format_file_size(asset.size),
                "checksum": f"sha256:{self.calculate_file_checksum(appimage_path)}"
            },
            "converted_packages": {
                "deb": {
                    "status": "pending"
                },
                "rpm": {
                    "status": "pending"
                }
            },
            "metadata": {
                "icon": metadata.get('icon_path', ''),
                "desktop_file": str(metadata),
                "executable": metadata.get('executable', ''),
                "mime_types": metadata.get('mime_types', [])
            },
            "source": {
                "repository": f"https://github.com/{repo_name}",
                "release_tag": release.tag_name,
                "release_date": release.published_at.isoformat() if release.published_at else None
            },
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "conversion_status": "pending"
        }
        
        return record
    
    def create_application_record_from_api(self, api_data, metadata, appimage_path):
        """Create application record from direct API data with multi-architecture support"""
        app_config = api_data['app_config']
        architecture = api_data['architecture']
        app_id = f"{app_config['name'].lower().replace(' ', '-')}"
        
        # Handle cross-architecture metadata extraction skipping
        if metadata and metadata.get('cross_architecture_skip', False):
            logger.info(f"Using fallback metadata for cross-architecture AppImage: {app_config['name']} ({architecture})")
            metadata = None  # Use fallback values
        
        # Create architecture-specific record
        record = {
            "id": f"{app_id}-{architecture}",
            "base_id": app_id,  # Base ID for grouping architectures
            "name": f"{app_config['name']} ({architecture})",
            "description": app_config.get('description', ''),
            "version": api_data['version'],
            "architecture": architecture,
            "category": [app_config.get('category', 'other')],
            "appimage": {
                "url": api_data['download_url'],
                "size": self.format_file_size(api_data['file_size']),
                "checksum": f"sha256:{self.calculate_file_checksum(appimage_path)}",
                "architecture": architecture
            },
            "converted_packages": {
                "deb": {
                    "status": "pending"
                },
                "rpm": {
                    "status": "pending"
                },
                "tarball": {
                    "status": "pending"
                }
            },
            "metadata": {
                "icon": metadata.get('icon_path', '') if metadata else app_config.get('icon_url', ''),
                "desktop_file": str(metadata) if metadata else '',
                "executable": metadata.get('executable', '') if metadata else '',
                "mime_types": metadata.get('mime_types', []) if metadata else [],
                "extraction_skipped": not bool(metadata)  # Flag to indicate if extraction was skipped
            },
            "source": {
                "website": app_config.get('website', ''),
                "api_url": api_data['arch_config']['api_url'],
                "commit_sha": api_data.get('commit_sha'),
                "release_date": datetime.now(timezone.utc).isoformat()
            },
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "conversion_status": "pending"
        }
        
        return record
    
    def update_application_data(self, new_records):
        """Update application data with new records"""
        existing_ids = {app['id'] for app in self.data['applications']}
        
        added_count = 0
        updated_count = 0
        
        for record in new_records:
            if record['id'] in existing_ids:
                # Update existing record, preserving conversion state
                for i, app in enumerate(self.data['applications']):
                    if app['id'] == record['id']:
                        old_app = self.data['applications'][i]
                        
                        # Check if version changed (needs re-conversion)
                        version_changed = old_app.get('version') != record.get('version')
                        
                        if version_changed:
                            # New version - reset to pending
                            logger.info(f"Version changed for {record['id']}: {old_app.get('version')} → {record.get('version')}")
                            record['conversion_status'] = 'pending'
                            record['converted_packages'] = {}
                        else:
                            # Same version - preserve conversion state
                            record['conversion_status'] = old_app.get('conversion_status', 'pending')
                            record['converted_packages'] = old_app.get('converted_packages', {})
                        
                        self.data['applications'][i] = record
                        updated_count += 1
                        break
            else:
                # Add new record
                self.data['applications'].append(record)
                added_count += 1
        
        # Update metadata
        self.data['metadata']['last_updated'] = datetime.now(timezone.utc).isoformat()
        self.data['metadata']['total_applications'] = len(self.data['applications'])
        
        logger.info(f"Added {added_count} new applications, updated {updated_count} existing")
        
        # Save updated data
        with open(self.applications_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def monitor_github_repositories(self):
        """Monitor GitHub repositories for AppImage releases"""
        if not APPIMAGE_REPOSITORIES or not self.github:
            logger.info("No GitHub repositories to monitor")
            return []
        
        if not self.check_rate_limits():
            logger.error("GitHub API rate limit too low, skipping GitHub monitoring")
            return []
        
        new_records = []
        
        for repo_name in APPIMAGE_REPOSITORIES:
            logger.info(f"Monitoring repository: {repo_name}")
            
            releases = self.get_repository_releases(repo_name)
            if not releases:
                continue
            
            # Process latest release
            latest_release = releases[0]
            appimage_assets = self.find_appimage_assets(latest_release)
            
            if not appimage_assets:
                logger.info(f"No AppImage assets found in {repo_name}")
                continue
            
            # Process each AppImage asset
            for asset in appimage_assets:
                logger.info(f"Processing AppImage: {asset.name}")
                
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_path = Path(temp_dir)
                    
                    # Download AppImage
                    appimage_path = self.download_appimage(asset.browser_download_url, temp_path)
                    if not appimage_path:
                        continue
                    
                    # Extract metadata
                    metadata = self.extract_appimage_metadata(appimage_path)
                    if not metadata:
                        continue
                    
                    # Create application record
                    record = self.create_application_record_from_github(
                        repo_name, latest_release, asset, metadata, appimage_path
                    )
                    new_records.append(record)
        
        return new_records
    
    def monitor_direct_api_endpoints(self):
        """Monitor direct API endpoints for AppImage releases"""
        if not DIRECT_API_ENDPOINTS:
            logger.info("No direct API endpoints to monitor")
            return []
        
        new_records = []
        
        for app_id, app_config in DIRECT_API_ENDPOINTS.items():
            logger.info(f"Monitoring direct API endpoint: {app_config['name']}")
            
            # Fetch data from API for all architectures
            api_data_list = self.fetch_direct_api_data(app_config)
            if not api_data_list:
                logger.warning(f"No API data found for {app_config['name']}")
                continue
            
            # Process each architecture
            for api_data in api_data_list:
                architecture = api_data['architecture']
                logger.info(f"Processing {app_config['name']} for architecture: {architecture}")
                
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_path = Path(temp_dir)
                    
                    # Download AppImage
                    appimage_path = self.download_appimage(api_data['download_url'], temp_path)
                    if not appimage_path:
                        logger.error(f"Failed to download AppImage for {app_config['name']} ({architecture})")
                        continue
                    
                    # Extract metadata (optional for direct API endpoints)
                    metadata = self.extract_appimage_metadata(appimage_path)
                    # Don't fail if metadata extraction fails for direct API endpoints
                    if not metadata:
                        logger.warning(f"Could not extract metadata for {app_config['name']} ({architecture})")
                    
                    # Create application record
                    record = self.create_application_record_from_api(api_data, metadata, appimage_path)
                    new_records.append(record)
                    
                    logger.info(f"Successfully processed {app_config['name']} ({architecture})")
        
        return new_records
    
    def monitor_all_sources(self):
        """Main monitoring function - monitors both GitHub and direct API sources"""
        logger.info("Starting AppImage monitoring from all sources")
        
        all_records = []
        
        # Monitor GitHub repositories
        github_records = self.monitor_github_repositories()
        all_records.extend(github_records)
        
        # Monitor direct API endpoints
        api_records = self.monitor_direct_api_endpoints()
        all_records.extend(api_records)
        
        # Update data files
        if all_records:
            self.update_application_data(all_records)
            logger.info(f"Monitoring complete. Processed {len(all_records)} applications")
        else:
            logger.info("No new applications found")

def main():
    """Main entry point"""
    try:
        monitor = AppImageMonitor()
        monitor.monitor_all_sources()
    except Exception as e:
        logger.error(f"Monitoring failed: {e}")
        raise

if __name__ == "__main__":
    main()