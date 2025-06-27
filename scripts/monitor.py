#!/usr/bin/env python3
"""
AppImage Repository Monitor Script for AppBinHub
Monitors GitHub repositories for AppImage releases and extracts metadata
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AppImageMonitor:
    def __init__(self):
        self.github_token = os.environ.get('GITHUB_TOKEN')
        if not self.github_token:
            raise ValueError("GITHUB_TOKEN environment variable is required")
        
        self.github = Github(self.github_token)
        self.data_dir = Path('../website/data')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Known AppImage repositories to monitor
        self.repositories = [
            'AppImage/AppImageKit',
            'AppImageCommunity/pkg2appimage',
            'AppImageCommunity/AppImageUpdate',
            'AppImageCommunity/libappimage'
        ]
        
        # Load existing application data
        self.applications_file = self.data_dir / 'applications.json'
        self.load_existing_data()
    
    def load_existing_data(self):
        """Load existing application data from JSON file"""
        if self.applications_file.exists():
            with open(self.applications_file, 'r') as f:
                self.data = json.load(f)
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
    
    def download_appimage(self, asset_url, temp_dir):
        """Download AppImage file to temporary directory"""
        try:
            response = requests.get(asset_url, stream=True)
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
            config = ConfigParser()
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
    
    def create_application_record(self, repo_name, release, asset, metadata, appimage_path):
        """Create application record from extracted data"""
        app_id = f"{repo_name.replace('/', '-')}-{asset.name.replace('.AppImage', '').lower()}"
        
        record = {
            "id": app_id,
            "name": metadata.get('name', asset.name.replace('.AppImage', '')),
            "description": metadata.get('description', ''),
            "version": release.tag_name,
            "category": metadata.get('categories', []),
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
    
    def update_application_data(self, new_records):
        """Update application data with new records"""
        existing_ids = {app['id'] for app in self.data['applications']}
        
        added_count = 0
        updated_count = 0
        
        for record in new_records:
            if record['id'] in existing_ids:
                # Update existing record
                for i, app in enumerate(self.data['applications']):
                    if app['id'] == record['id']:
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
    
    def monitor_repositories(self):
        """Main monitoring function"""
        logger.info("Starting AppImage repository monitoring")
        
        if not self.check_rate_limits():
            logger.error("GitHub API rate limit too low, skipping monitoring")
            return
        
        new_records = []
        
        for repo_name in self.repositories:
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
                    record = self.create_application_record(
                        repo_name, latest_release, asset, metadata, appimage_path
                    )
                    new_records.append(record)
        
        # Update data files
        if new_records:
            self.update_application_data(new_records)
            logger.info(f"Monitoring complete. Processed {len(new_records)} applications")
        else:
            logger.info("No new applications found")

def main():
    """Main entry point"""
    try:
        monitor = AppImageMonitor()
        monitor.monitor_repositories()
    except Exception as e:
        logger.error(f"Monitoring failed: {e}")
        raise

if __name__ == "__main__":
    main()