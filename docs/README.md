# AppBinHub Automation System

A comprehensive Python automation system for monitoring AppImage repositories, converting packages to multiple formats, and maintaining a web-based application catalog.

## Overview

AppBinHub is an automated system that:
- Monitors GitHub repositories for AppImage releases
- Extracts metadata from AppImage files
- Converts AppImages to .deb and .rpm packages
- Maintains a JSON-based application database
- Provides GitHub Actions workflows for automation

## System Architecture

```
AppBinHub/
├── scripts/                 # Python automation scripts
│   ├── monitor.py          # AppImage repository monitoring
│   ├── converter.py        # Package conversion system
│   ├── config.py           # Configuration settings
│   └── requirements.txt    # Python dependencies
├── .github/workflows/      # GitHub Actions automation
│   ├── monitor-and-convert.yml
│   └── deploy.yml
├── website/                # Static web application
│   └── data/              # JSON application database
└── docs/                  # Documentation
```

## Features

### AppImage Monitoring (`monitor.py`)
- **GitHub API Integration**: Monitors repositories using authenticated GitHub API
- **Metadata Extraction**: Extracts application metadata from .desktop files
- **Icon Processing**: Extracts and processes application icons
- **Version Tracking**: Tracks application versions and updates
- **Rate Limit Management**: Respects GitHub API rate limits

### Package Conversion (`converter.py`)
- **Multi-format Support**: Converts AppImages to .deb and .rpm packages
- **Tool Integration**: Uses `appimage2deb` and `alien` conversion tools
- **Validation**: Validates converted packages for integrity
- **Error Handling**: Comprehensive error handling and logging
- **Storage Management**: Manages converted package storage

### GitHub Actions Automation
- **Scheduled Monitoring**: Runs every 4 hours automatically
- **Tool Installation**: Installs required conversion tools
- **Deployment**: Automated GitHub Pages deployment
- **Logging**: Comprehensive logging and artifact storage

## Prerequisites

### System Requirements
- Python 3.9 or higher
- Ubuntu/Debian-based Linux system (for conversion tools)
- Git
- GitHub account with Actions enabled

### Required Tools
- `appimage2deb` (installed via Snap)
- `alien` (for RPM conversion)
- `dpkg-deb` (for package validation)

## Installation

### 1. Clone Repository
```bash
git clone https://github.com/your-username/appbinhub.git
cd appbinhub
```

### 2. Install Python Dependencies
```bash
cd scripts
pip install -r requirements.txt
```

### 3. Install System Tools
```bash
# Install appimage2deb via Snap
sudo snap install appimage2deb

# Install alien and dpkg tools
sudo apt-get update
sudo apt-get install alien dpkg-dev
```

### 4. Set Environment Variables
```bash
# GitHub Personal Access Token (required)
export GITHUB_TOKEN="your_github_token_here"
```

## Usage

### Manual Execution

#### Monitor AppImage Repositories
```bash
cd scripts
python monitor.py
```

#### Convert Packages
```bash
cd scripts
python converter.py
```

### Automated Execution

The system runs automatically via GitHub Actions:
- **Monitoring**: Every 4 hours
- **Deployment**: On website changes
- **Manual Trigger**: Available via GitHub Actions UI

## Configuration

### Repository Monitoring
Edit `scripts/config.py` to modify monitored repositories:

```python
APPIMAGE_REPOSITORIES = [
    "AppImage/AppImageKit",
    "AppImageCommunity/pkg2appimage",
    # Add more repositories here
]
```

### Conversion Settings
Modify conversion tool settings in `config.py`:

```python
CONVERSION_TOOLS = {
    "appimage2deb": {
        "timeout": 300,
        "enabled": True
    }
}
```

## Data Structure

### Applications Database (`website/data/applications.json`)
```json
{
  "metadata": {
    "last_updated": "2025-06-27T14:20:41Z",
    "total_applications": 0,
    "version": "1.0.0"
  },
  "applications": [
    {
      "id": "unique-app-identifier",
      "name": "Application Name",
      "description": "Application description",
      "version": "1.0.0",
      "category": ["Utility", "Development"],
      "appimage": {
        "url": "https://github.com/user/repo/releases/download/v1.0.0/app.AppImage",
        "size": "25.6 MB",
        "checksum": "sha256:abc123..."
      },
      "converted_packages": {
        "deb": {
          "url": "./converted_packages/app-id/app.deb",
          "size": "23.1 MB",
          "status": "available"
        },
        "rpm": {
          "url": "./converted_packages/app-id/app.rpm",
          "size": "24.8 MB",
          "status": "available"
        }
      }
    }
  ]
}
```

### Categories (`website/data/categories.json`)
Based on FreeDesktop.org specification:
- Audio, Education, Games, Graphics
- Internet, Office, Programming, Utilities
- Video, Other

## GitHub Actions Workflows

### Monitor and Convert Workflow
- **Trigger**: Every 4 hours, manual, or on script changes
- **Actions**: Monitor repositories, convert packages, commit changes
- **Tools**: Installs appimage2deb, alien, dpkg-dev

### Deploy Workflow
- **Trigger**: Website changes or manual
- **Actions**: Validate structure, optimize assets, deploy to GitHub Pages
- **Validation**: JSON validation, size checks

## Logging

### Log Files
- `scripts/monitor.log`: Repository monitoring logs
- `scripts/converter.log`: Package conversion logs

### Log Levels
- **INFO**: Normal operations
- **WARNING**: Non-critical issues
- **ERROR**: Critical failures

## Troubleshooting

### Common Issues

#### GitHub API Rate Limit
```
Error: GitHub API rate limit exceeded
```
**Solution**: Wait for rate limit reset or use authenticated requests

#### Conversion Tool Not Found
```
Error: appimage2deb tool not available
```
**Solution**: Install via Snap: `sudo snap install appimage2deb`

#### AppImage Extraction Failed
```
Error: Failed to extract AppImage
```
**Solution**: Verify AppImage file integrity and permissions

### Debug Mode
Enable debug logging by modifying `config.py`:
```python
LOGGING_CONFIG["level"] = "DEBUG"
```

## Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make changes and test locally
4. Submit a pull request

### Code Style
- Follow PEP 8 Python style guidelines
- Add docstrings to all functions
- Include error handling and logging
- Write unit tests for new features

## Security Considerations

### GitHub Token
- Use a Personal Access Token with minimal required permissions
- Store token as a GitHub Secret, not in code
- Regularly rotate tokens

### Package Validation
- All converted packages are validated before storage
- Checksums are calculated and verified
- File size limits are enforced

## Performance

### Optimization Features
- GitHub API rate limit management
- Efficient file processing with temporary directories
- Parallel processing where possible
- Storage size monitoring

### Limits
- Maximum JSON file size: 1MB
- Maximum repository size: 900MB (GitHub Pages limit)
- Maximum package size: 100MB

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review GitHub Actions logs
3. Create an issue on GitHub
4. Check the documentation in `/docs/`

## Acknowledgments

- AppImage project for the packaging format
- FreeDesktop.org for desktop entry specifications
- GitHub for hosting and automation platform
- Open source conversion tools: appimage2deb, alien