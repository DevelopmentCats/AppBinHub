#!/usr/bin/env python3
"""
AppImage Package Conversion Script for AppBinHub
Converts AppImage files to multiple package formats (.deb, .rpm, .tar.gz)
Uses modern extraction methods with unsquashfs and dpkg-deb for reliable conversion
"""

import os
import json
import subprocess
import tempfile
import shutil
import logging
import re
import struct
from datetime import datetime, timezone
from pathlib import Path
import requests
import hashlib

# Import configuration
from config import (
    WEBSITE_DATA_DIR,
    LOGGING_CONFIG,
    normalize_architecture,
    detect_architecture_from_url,
    get_package_formats_for_arch,
    get_debian_arch,
    get_rpm_arch,
    generate_version_path,
    should_create_package_format
)

# Configure logging using config
logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG["level"]),
    format=LOGGING_CONFIG["format"],
    handlers=[
        logging.FileHandler(LOGGING_CONFIG["converter_log"]),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ModernAppImageConverter:
    def __init__(self):
        self.data_dir = WEBSITE_DATA_DIR
        self.applications_file = self.data_dir / 'applications.json'
        self.converted_dir = Path('converted_packages')  # Temporary storage
        self.converted_dir.mkdir(exist_ok=True)
        # Get absolute path for website packages directory
        self.website_packages_dir = self.data_dir.parent / 'packages'  # Web-accessible storage
        self.website_packages_dir.mkdir(parents=True, exist_ok=True)
        
        # Log paths for debugging
        logger.info(f"Converter initialized:")
        logger.info(f"  - Data dir: {self.data_dir}")
        logger.info(f"  - Temp packages dir: {self.converted_dir.absolute()}")
        logger.info(f"  - Web packages dir: {self.website_packages_dir.absolute()}")
        
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
        
        # Check for unsquashfs (primary extraction method)
        try:
            # Try different version commands as unsquashfs may respond differently
            commands_to_try = [
                ['unsquashfs', '-version'],
                ['unsquashfs', '--version'],
                ['unsquashfs', '-help'],
                ['unsquashfs']  # This will show usage and exit with non-zero but tool exists
            ]
            
            unsquashfs_found = False
            for cmd in commands_to_try:
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                    # unsquashfs exists if it runs (even if it exits with error due to no args)
                    if 'squashfs' in result.stdout.lower() or 'squashfs' in result.stderr.lower() or result.returncode in [0, 1, 2]:
                        unsquashfs_found = True
                        logger.info(f"unsquashfs tool is available (detected with: {' '.join(cmd)})")
                        break
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    continue
            
            if unsquashfs_found:
                self.tools_available['unsquashfs'] = True
            else:
                self.tools_available['unsquashfs'] = False
                logger.info("unsquashfs tool not found (optional - built-in extraction will be used)")
        except Exception as e:
            self.tools_available['unsquashfs'] = False
            logger.info(f"unsquashfs not available: {e} (optional - built-in extraction will be used)")
        
        # Check for dpkg-deb (for DEB package creation)
        try:
            result = subprocess.run(['dpkg-deb', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.tools_available['dpkg-deb'] = True
                logger.info("dpkg-deb tool is available for DEB creation")
            else:
                self.tools_available['dpkg-deb'] = False
                logger.warning("dpkg-deb tool not found")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.tools_available['dpkg-deb'] = False
            logger.warning("dpkg-deb tool not found")
        
        # Check for rpmbuild (for native RPM creation)
        try:
            result = subprocess.run(['rpmbuild', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.tools_available['rpmbuild'] = True
                logger.info("rpmbuild tool is available for RPM creation")
            else:
                self.tools_available['rpmbuild'] = False
                logger.warning("rpmbuild tool not found")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.tools_available['rpmbuild'] = False
            logger.warning("rpmbuild tool not found")
        
        # Check for file utility (for file type detection)
        try:
            result = subprocess.run(['file', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.tools_available['file'] = True
                logger.info("file utility is available")
            else:
                self.tools_available['file'] = False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.tools_available['file'] = False
    
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
    
    def find_squashfs_offset(self, appimage_path):
        """Find squashfs filesystem offset in AppImage using magic number"""
        try:
            with open(appimage_path, 'rb') as f:
                # Read file in chunks to find squashfs magic number 'hsqs'
                chunk_size = 1024 * 1024  # 1MB chunks
                offset = 0
                
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    
                    # Look for squashfs magic number
                    magic_pos = chunk.find(b'hsqs')
                    if magic_pos != -1:
                        return offset + magic_pos
                    
                    # Overlap to catch magic number across chunk boundaries
                    if len(chunk) == chunk_size:
                        f.seek(-3, 1)
                        offset += chunk_size - 3
                    else:
                        break
                
                return None
                
        except Exception as e:
            logger.error(f"Error finding squashfs offset: {e}")
            return None
    
    def extract_appimage_with_unsquashfs(self, appimage_path, extract_dir):
        """Extract AppImage using unsquashfs (primary method)"""
        if not self.tools_available.get('unsquashfs', False):
            return False
        
        try:
            logger.info(f"Extracting AppImage with unsquashfs: {appimage_path}")
            
            # Find squashfs offset
            offset = self.find_squashfs_offset(appimage_path)
            if offset is None:
                logger.warning("Could not find squashfs offset, trying without offset")
                
            # Run unsquashfs
            cmd = ['unsquashfs', '-f', '-d', str(extract_dir / 'squashfs-root')]
            if offset is not None:
                cmd.extend(['-o', str(offset)])
            cmd.append(str(appimage_path))
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                logger.info("Successfully extracted with unsquashfs")
                return True
            else:
                logger.warning(f"unsquashfs failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error with unsquashfs extraction: {e}")
            return False
    
    def extract_appimage_builtin(self, appimage_path, extract_dir):
        """Extract AppImage using built-in --appimage-extract (fallback method)"""
        try:
            logger.info(f"Extracting AppImage with built-in method: {appimage_path}")
            
            # Make AppImage executable
            os.chmod(appimage_path, 0o755)
            
            # Run AppImage with --appimage-extract
            result = subprocess.run(
                [str(appimage_path), '--appimage-extract'],
                cwd=extract_dir,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                logger.info("Successfully extracted with built-in method")
                return True
            else:
                logger.warning(f"Built-in extraction failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error with built-in extraction: {e}")
            return False
    
    def extract_appimage(self, appimage_path, extract_dir, target_arch=None):
        """Extract AppImage using the appropriate method for cross-compilation"""
        import platform
        host_arch = normalize_architecture(platform.machine())
        
        # If target arch is different from host, use unsquashfs (cross-compilation)
        if target_arch and target_arch != host_arch:
            logger.info(f"Cross-compiling: {target_arch} on {host_arch} - using unsquashfs")
            if self.extract_appimage_with_unsquashfs(appimage_path, extract_dir):
                return True
            logger.error("unsquashfs extraction failed for cross-compilation")
            return False
        
        # Native architecture: try built-in method first, fallback to unsquashfs
        if self.extract_appimage_builtin(appimage_path, extract_dir):
            return True
        
        logger.warning("Built-in extraction failed, trying unsquashfs as fallback")
        if self.extract_appimage_with_unsquashfs(appimage_path, extract_dir):
            return True
        
        logger.error("All extraction methods failed")
        return False
    
    def detect_architecture(self, appimage_path):
        """Detect architecture from AppImage file using shared config"""
        try:
            # Try to get architecture from file command
            if self.tools_available.get('file', False):
                result = subprocess.run(['file', str(appimage_path)], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    arch_from_file = normalize_architecture(result.stdout)
                    if arch_from_file != 'x86_64':  # Only trust non-default detections
                        return arch_from_file
            
            # Fallback: try to detect from URL or filename
            arch_from_url = detect_architecture_from_url(str(appimage_path))
            if arch_from_url:
                return arch_from_url
            
            # Final fallback
            logger.warning("Could not detect architecture, defaulting to x86_64")
            return 'x86_64'
            
        except Exception as e:
            logger.error(f"Error detecting architecture: {e}")
            return 'x86_64'
    
    def generate_package_name(self, app_data, package_type, architecture):
        """Generate proper package name with version and architecture using shared config"""
        # Extract base app name from full name (remove architecture suffix if present)
        app_name = app_data['name'].lower()
        if f'({architecture})' in app_name:
            app_name = app_name.replace(f'({architecture})', '').strip()
        
        # Clean app name for package naming
        app_name = re.sub(r'[^a-z0-9\-]', '-', app_name)
        app_name = re.sub(r'-+', '-', app_name).strip('-')
        
        version = app_data.get('version', '1.0.0')
        # Clean version string
        version = re.sub(r'[^0-9\.\-]', '', version)
        if not version:
            version = '1.0.0'
        
        if package_type == 'deb':
            arch = get_debian_arch(architecture)
            return f"{app_name}_{version}_{arch}.deb"
        elif package_type == 'rpm':
            arch = get_rpm_arch(architecture)
            return f"{app_name}-{version}-1.{arch}.rpm"
        elif package_type == 'tar.gz':
            return f"{app_name}-{version}-{architecture}.tar.gz"
        
        return f"{app_name}-{version}-{architecture}.{package_type}"
    
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
    
    def store_converted_package(self, package_path, app_data, package_type):
        """Store converted package with version management and return metadata"""
        try:
            # Extract base app ID and create versioned storage path
            app_id = app_data.get('base_id', app_data['id'])
            version = app_data.get('version', '1.0.0')
            architecture = app_data.get('architecture', 'x86_64')
            
            # Create versioned directory structure in temporary storage: converted_packages/{app_id}/{version}/
            temp_version_dir = self.converted_dir / app_id / version
            temp_version_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy package to temporary storage location first
            temp_stored_path = temp_version_dir / package_path.name
            shutil.copy2(package_path, temp_stored_path)
            
            # Create versioned directory structure in web-accessible storage: website/packages/{app_id}/{version}/
            web_version_dir = self.website_packages_dir / app_id / version
            web_version_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy package to web-accessible storage location
            web_stored_path = web_version_dir / package_path.name
            shutil.copy2(temp_stored_path, web_stored_path)
            
            # Generate metadata with web-accessible URL
            metadata = {
                "url": f"./packages/{app_id}/{version}/{package_path.name}",
                "size": self.format_file_size(web_stored_path),
                "checksum": f"sha256:{self.calculate_file_checksum(web_stored_path)}",
                "architecture": architecture,
                "status": "available",
                "created": datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"Stored {package_type} package for {app_id} v{version} ({architecture}): {web_stored_path}")
            return metadata
            
        except Exception as e:
            logger.error(f"Error storing package: {e}")
            return None
    
    def create_deb_package(self, squashfs_root, app_data, architecture, output_dir):
        """Create DEB package from extracted AppImage contents"""
        if not self.tools_available.get('dpkg-deb', False):
            logger.error("dpkg-deb not available for DEB creation")
            return None
        
        try:
            # Generate package name
            package_name = self.generate_package_name(app_data, 'deb', architecture)
            
            # Create debian package structure
            deb_dir = output_dir / 'debian_package'
            deb_dir.mkdir(exist_ok=True)
            
            # Create DEBIAN control directory
            control_dir = deb_dir / 'DEBIAN'
            control_dir.mkdir(exist_ok=True)
            
            # Copy application files to /opt
            app_name = re.sub(r'[^a-z0-9\-]', '-', app_data['name'].lower())
            app_install_dir = deb_dir / 'opt' / app_name
            app_install_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy all files from squashfs-root
            shutil.copytree(squashfs_root, app_install_dir, dirs_exist_ok=True)
            
            # Create control file
            control_content = f"""Package: {app_name}
Version: {app_data.get('version', '1.0.0')}
Section: misc
Priority: optional
Architecture: {get_debian_arch(architecture)}
Maintainer: AppBinHub <automated@appbinhub.com>
Description: {app_data.get('description', app_data['name'])}
 {app_data.get('description', 'Converted from AppImage')}
"""
            
            with open(control_dir / 'control', 'w') as f:
                f.write(control_content)
            
            # Build DEB package
            deb_path = output_dir / package_name
            result = subprocess.run([
                'dpkg-deb', '--build', str(deb_dir), str(deb_path)
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                logger.info(f"Successfully created DEB package: {deb_path}")
                return deb_path
            else:
                logger.error(f"DEB creation failed: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating DEB package: {e}")
            return None
    
    def create_tarball(self, squashfs_root, app_data, architecture, output_dir):
        """Create tarball from extracted AppImage contents"""
        try:
            # Generate package name
            package_name = self.generate_package_name(app_data, 'tar.gz', architecture)
            
            # Create tarball
            tarball_path = output_dir / package_name
            
            # Use tar to create compressed archive
            result = subprocess.run([
                'tar', '-czf', str(tarball_path), '-C', str(squashfs_root.parent), squashfs_root.name
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                logger.info(f"Successfully created tarball: {tarball_path}")
                return tarball_path
            else:
                logger.error(f"Tarball creation failed: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating tarball: {e}")
            return None
    
    def create_rpm_package(self, squashfs_root, app_data, architecture, output_dir):
        """Create RPM package from extracted AppImage contents"""
        if not self.tools_available.get('rpmbuild', False):
            logger.warning("rpmbuild not available for RPM creation")
            return None
        
        try:
            # Generate package name  
            package_name = self.generate_package_name(app_data, 'rpm', architecture)
            
            # Create RPM build environment
            rpm_build_dir = output_dir / 'rpm_build'
            for subdir in ['BUILD', 'RPMS', 'SOURCES', 'SPECS', 'SRPMS']:
                (rpm_build_dir / subdir).mkdir(parents=True, exist_ok=True)
            
            # Create spec file
            app_name = re.sub(r'[^a-z0-9\-]', '-', app_data['name'].lower())
            spec_content = f"""Name: {app_name}
Version: {app_data.get('version', '1.0.0')}
Release: 1
Summary: {app_data.get('description', app_data['name'])}
License: Unknown
Group: Applications/System
BuildArch: {architecture}

%description
{app_data.get('description', 'Converted from AppImage')}

%install
mkdir -p %{{buildroot}}/opt/{app_name}
cp -r {squashfs_root}/* %{{buildroot}}/opt/{app_name}/

%files
/opt/{app_name}/*

%changelog
* {datetime.now().strftime('%a %b %d %Y')} AppBinHub <automated@appbinhub.com>
- Converted from AppImage
"""
            
            spec_file = rpm_build_dir / 'SPECS' / f"{app_name}.spec"
            with open(spec_file, 'w') as f:
                f.write(spec_content)
            
            # Build RPM with target architecture for cross-compilation
            rpm_arch = get_rpm_arch(architecture)
            result = subprocess.run([
                'rpmbuild',
                '--define', f'_topdir {rpm_build_dir}',
                '--target', rpm_arch,
                '-bb', str(spec_file)
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                # Find generated RPM
                rpm_files = list((rpm_build_dir / 'RPMS').rglob('*.rpm'))
                if rpm_files:
                    # Move to output directory with correct name
                    rpm_path = output_dir / package_name
                    shutil.move(str(rpm_files[0]), str(rpm_path))
                    logger.info(f"Successfully created RPM package: {rpm_path}")
                    return rpm_path
                else:
                    logger.error("No RPM file found after build")
                    return None
            else:
                logger.error(f"RPM creation failed: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating RPM package: {e}")
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
            
            # Detect architecture
            architecture = self.detect_architecture(appimage_path)
            logger.info(f"Detected architecture: {architecture}")
            
            # Extract AppImage
            extract_dir = temp_path / 'extracted'
            extract_dir.mkdir(exist_ok=True)
            
            if not self.extract_appimage(appimage_path, extract_dir, target_arch=architecture):
                logger.error("Failed to extract AppImage")
                app_data['conversion_status'] = 'failed'
                return False
            
            # Find squashfs-root directory
            squashfs_root = extract_dir / 'squashfs-root'
            if not squashfs_root.exists():
                logger.error("squashfs-root directory not found")
                app_data['conversion_status'] = 'failed'
                return False
            
            conversion_success = False
            
            # Get preferred package formats for this architecture
            preferred_formats = get_package_formats_for_arch(architecture)
            logger.info(f"Creating packages for {architecture}: {preferred_formats}")
            
            # Create DEB package (if appropriate for architecture)
            if should_create_package_format(architecture, 'deb'):
                deb_path = self.create_deb_package(squashfs_root, app_data, architecture, temp_path)
                if deb_path and self.validate_deb_package(deb_path):
                    deb_metadata = self.store_converted_package(deb_path, app_data, 'deb')
                    if deb_metadata:
                        app_data['converted_packages']['deb'] = deb_metadata
                        conversion_success = True
                else:
                    app_data['converted_packages']['deb']['status'] = 'failed'
            else:
                app_data['converted_packages']['deb']['status'] = 'skipped_architecture'
            
            # Create RPM package (if appropriate for architecture)
            if should_create_package_format(architecture, 'rpm'):
                rpm_path = self.create_rpm_package(squashfs_root, app_data, architecture, temp_path)
                if rpm_path:
                    rpm_metadata = self.store_converted_package(rpm_path, app_data, 'rpm')
                    if rpm_metadata:
                        app_data['converted_packages']['rpm'] = rpm_metadata
                        conversion_success = True
                else:
                    app_data['converted_packages']['rpm']['status'] = 'failed'
            else:
                app_data['converted_packages']['rpm']['status'] = 'skipped_architecture'
            
            # Always create tarball as universal fallback
            tarball_path = self.create_tarball(squashfs_root, app_data, architecture, temp_path)
            if tarball_path:
                tarball_metadata = self.store_converted_package(tarball_path, app_data, 'tar.gz')
                if tarball_metadata:
                    # Add tarball to converted packages
                    if 'tarball' not in app_data['converted_packages']:
                        app_data['converted_packages']['tarball'] = {}
                    app_data['converted_packages']['tarball'] = tarball_metadata
                    conversion_success = True
            
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
        converter = ModernAppImageConverter()
        
        # Convert pending applications
        converter.convert_pending_applications()
        
        # Optionally retry failed conversions
        # converter.retry_failed_conversions()
        
    except Exception as e:
        logger.error(f"Conversion process failed: {e}")
        raise

if __name__ == "__main__":
    main()