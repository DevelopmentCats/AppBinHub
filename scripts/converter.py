#!/usr/bin/env python3
"""
AppImage Package Conversion Script for AppBinHub
Converts AppImage files to multiple package formats (.deb, .rpm)
"""

import os
import json
import subprocess
import tempfile
import shutil
import logging
from datetime import datetime, timezone
from pathlib import Path
import requests
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('converter.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AppImageConverter:
    def __init__(self):
        self.data_dir = Path('../website/data')
        self.applications_file = self.data_dir / 'applications.json'
        self.converted_dir = Path('converted_packages')
        self.converted_dir.mkdir(exist_ok=True)
        
        # Load application data
        self.load_application_data()
        
        # Check for required tools
        self.check_conversion_tools()
    
    def load_application_data(self):
        """Load application data from JSON file"""
        if not self.applications_file.exists():
            logger.error("Applications data file not found")
            self.data = {"applications": []}
            return
        
        with open(self.applications_file, 'r') as f:
            self.data = json.load(f)
    
    def save_application_data(self):
        """Save updated application data to JSON file"""
        with open(self.applications_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def check_conversion_tools(self):
        """Check if required conversion tools are available"""
        self.tools_available = {}
        
        # Check for appimage2deb (via Snap)
        try:
            result = subprocess.run(['appimage2deb', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.tools_available['appimage2deb'] = True
                logger.info("appimage2deb tool is available")
            else:
                self.tools_available['appimage2deb'] = False
                logger.warning("appimage2deb tool not found")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.tools_available['appimage2deb'] = False
            logger.warning("appimage2deb tool not found or not responding")
        
        # Check for alien (for RPM conversion)
        try:
            result = subprocess.run(['alien', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.tools_available['alien'] = True
                logger.info("alien tool is available for RPM conversion")
            else:
                self.tools_available['alien'] = False
                logger.warning("alien tool not found")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.tools_available['alien'] = False
            logger.warning("alien tool not found")
        
        # Check for dpkg-deb (for package validation)
        try:
            result = subprocess.run(['dpkg-deb', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.tools_available['dpkg-deb'] = True
                logger.info("dpkg-deb tool is available for package validation")
            else:
                self.tools_available['dpkg-deb'] = False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.tools_available['dpkg-deb'] = False
    
    def download_appimage(self, url, temp_dir):
        """Download AppImage file to temporary directory"""
        try:
            logger.info(f"Downloading AppImage from: {url}")
            response = requests.get(url, stream=True, timeout=300)
            response.raise_for_status()
            
            filename = url.split('/')[-1]
            if not filename.endswith('.AppImage'):
                filename += '.AppImage'
            
            filepath = temp_dir / filename
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Make executable
            os.chmod(filepath, 0o755)
            logger.info(f"Downloaded AppImage: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error downloading AppImage from {url}: {e}")
            return None
    
    def convert_appimage_to_deb(self, appimage_path, output_dir):
        """Convert AppImage to Debian package using appimage2deb"""
        if not self.tools_available.get('appimage2deb', False):
            logger.error("appimage2deb tool not available")
            return None
        
        try:
            logger.info(f"Converting {appimage_path} to .deb package")
            
            # Run appimage2deb conversion
            result = subprocess.run([
                'appimage2deb',
                str(appimage_path),
                '--output', str(output_dir)
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                logger.error(f"appimage2deb conversion failed: {result.stderr}")
                return None
            
            # Find generated .deb file
            deb_files = list(output_dir.glob('*.deb'))
            if not deb_files:
                logger.error("No .deb file generated")
                return None
            
            deb_file = deb_files[0]
            logger.info(f"Successfully converted to .deb: {deb_file}")
            return deb_file
            
        except subprocess.TimeoutExpired:
            logger.error("appimage2deb conversion timed out")
            return None
        except Exception as e:
            logger.error(f"Error during .deb conversion: {e}")
            return None
    
    def convert_deb_to_rpm(self, deb_path, output_dir):
        """Convert .deb package to .rpm using alien"""
        if not self.tools_available.get('alien', False):
            logger.error("alien tool not available for RPM conversion")
            return None
        
        try:
            logger.info(f"Converting {deb_path} to .rpm package")
            
            # Run alien conversion
            result = subprocess.run([
                'alien', '--to-rpm', '--scripts',
                str(deb_path)
            ], cwd=output_dir, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                logger.error(f"alien conversion failed: {result.stderr}")
                return None
            
            # Find generated .rpm file
            rpm_files = list(output_dir.glob('*.rpm'))
            if not rpm_files:
                logger.error("No .rpm file generated")
                return None
            
            rpm_file = rpm_files[0]
            logger.info(f"Successfully converted to .rpm: {rpm_file}")
            return rpm_file
            
        except subprocess.TimeoutExpired:
            logger.error("alien conversion timed out")
            return None
        except Exception as e:
            logger.error(f"Error during .rpm conversion: {e}")
            return None
    
    def validate_deb_package(self, deb_path):
        """Validate .deb package integrity"""
        if not self.tools_available.get('dpkg-deb', False):
            logger.warning("dpkg-deb not available for package validation")
            return True  # Assume valid if we can't validate
        
        try:
            # Check package info
            result = subprocess.run([
                'dpkg-deb', '--info', str(deb_path)
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                logger.error(f"Package validation failed: {result.stderr}")
                return False
            
            logger.info("Package validation successful")
            return True
            
        except Exception as e:
            logger.error(f"Error validating package: {e}")
            return False
    
    def calculate_file_checksum(self, filepath):
        """Calculate SHA256 checksum of file"""
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def format_file_size(self, filepath):
        """Get formatted file size"""
        size_bytes = filepath.stat().st_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def store_converted_package(self, package_path, app_id, package_type):
        """Store converted package and return metadata"""
        try:
            # Create app-specific directory
            app_dir = self.converted_dir / app_id
            app_dir.mkdir(exist_ok=True)
            
            # Copy package to storage location
            stored_path = app_dir / package_path.name
            shutil.copy2(package_path, stored_path)
            
            # Generate metadata
            metadata = {
                "url": f"./converted_packages/{app_id}/{package_path.name}",
                "size": self.format_file_size(stored_path),
                "checksum": f"sha256:{self.calculate_file_checksum(stored_path)}",
                "status": "available",
                "created": datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"Stored {package_type} package: {stored_path}")
            return metadata
            
        except Exception as e:
            logger.error(f"Error storing package: {e}")
            return None
    
    def convert_application(self, app_data):
        """Convert a single application to multiple formats"""
        app_id = app_data['id']
        appimage_url = app_data['appimage']['url']
        
        logger.info(f"Converting application: {app_id}")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Download AppImage
            appimage_path = self.download_appimage(appimage_url, temp_path)
            if not appimage_path:
                return False
            
            conversion_success = False
            
            # Convert to .deb
            if self.tools_available.get('appimage2deb', False):
                deb_output_dir = temp_path / 'deb_output'
                deb_output_dir.mkdir(exist_ok=True)
                
                deb_path = self.convert_appimage_to_deb(appimage_path, deb_output_dir)
                if deb_path and self.validate_deb_package(deb_path):
                    # Store .deb package
                    deb_metadata = self.store_converted_package(deb_path, app_id, 'deb')
                    if deb_metadata:
                        app_data['converted_packages']['deb'] = deb_metadata
                        conversion_success = True
                    
                    # Convert .deb to .rpm
                    if self.tools_available.get('alien', False):
                        rpm_output_dir = temp_path / 'rpm_output'
                        rpm_output_dir.mkdir(exist_ok=True)
                        
                        rpm_path = self.convert_deb_to_rpm(deb_path, rpm_output_dir)
                        if rpm_path:
                            rpm_metadata = self.store_converted_package(rpm_path, app_id, 'rpm')
                            if rpm_metadata:
                                app_data['converted_packages']['rpm'] = rpm_metadata
                else:
                    app_data['converted_packages']['deb']['status'] = 'failed'
            else:
                app_data['converted_packages']['deb']['status'] = 'tool_unavailable'
            
            # Update conversion status
            if conversion_success:
                app_data['conversion_status'] = 'completed'
                app_data['last_updated'] = datetime.now(timezone.utc).isoformat()
            else:
                app_data['conversion_status'] = 'failed'
            
            return conversion_success
    
    def convert_pending_applications(self):
        """Convert all applications with pending conversion status"""
        logger.info("Starting package conversion process")
        
        if not any(self.tools_available.values()):
            logger.error("No conversion tools available")
            return
        
        pending_apps = [
            app for app in self.data['applications'] 
            if app.get('conversion_status') == 'pending'
        ]
        
        if not pending_apps:
            logger.info("No applications pending conversion")
            return
        
        logger.info(f"Found {len(pending_apps)} applications to convert")
        
        converted_count = 0
        failed_count = 0
        
        for app in pending_apps:
            try:
                if self.convert_application(app):
                    converted_count += 1
                    logger.info(f"Successfully converted: {app['id']}")
                else:
                    failed_count += 1
                    logger.error(f"Failed to convert: {app['id']}")
            except Exception as e:
                failed_count += 1
                logger.error(f"Error converting {app['id']}: {e}")
        
        # Save updated data
        self.save_application_data()
        
        logger.info(f"Conversion complete. Success: {converted_count}, Failed: {failed_count}")
    
    def retry_failed_conversions(self):
        """Retry applications with failed conversion status"""
        logger.info("Retrying failed conversions")
        
        failed_apps = [
            app for app in self.data['applications'] 
            if app.get('conversion_status') == 'failed'
        ]
        
        if not failed_apps:
            logger.info("No failed conversions to retry")
            return
        
        logger.info(f"Retrying {len(failed_apps)} failed conversions")
        
        for app in failed_apps:
            # Reset status to pending for retry
            app['conversion_status'] = 'pending'
        
        # Run conversion process
        self.convert_pending_applications()

def main():
    """Main entry point"""
    try:
        converter = AppImageConverter()
        
        # Convert pending applications
        converter.convert_pending_applications()
        
        # Optionally retry failed conversions
        # converter.retry_failed_conversions()
        
    except Exception as e:
        logger.error(f"Conversion process failed: {e}")
        raise

if __name__ == "__main__":
    main()