# AppBinHub

A comprehensive web-based application repository system that automatically monitors AppImage repositories, converts packages to multiple formats, and presents them through a modern dark-themed website.

## 🚀 Features

- **Automated AppImage Monitoring**: Continuously monitors GitHub repositories for new AppImage releases
- **Multi-Format Package Conversion**: Converts AppImages to .deb and .rpm packages automatically  
- **Modern Dark-Themed Website**: Clean, responsive interface optimized for all devices
- **GitHub Actions Integration**: Fully automated pipeline with scheduled monitoring and deployment
- **Comprehensive Metadata Extraction**: Extracts application information, icons, and desktop files
- **Real-Time Updates**: Website automatically updates with new applications every 4 hours

## 🏗️ System Architecture

```
AppBinHub/
├── website/                 # Static web application (GitHub Pages)
│   ├── css/                # Dark theme stylesheets
│   ├── js/                 # Client-side JavaScript
│   ├── data/               # JSON application database
│   └── index.html          # Main catalog interface
├── scripts/                # Python automation system
│   ├── monitor.py          # AppImage repository monitoring
│   ├── converter.py        # Package conversion engine
│   ├── config.py           # System configuration
│   └── verify_system.py    # System validation
├── .github/workflows/      # GitHub Actions automation
│   ├── monitor-and-convert.yml
│   └── deploy.yml
└── docs/                   # Comprehensive documentation
```

## 📋 System Requirements

### Prerequisites
- **Python 3.9+** for automation scripts
- **Ubuntu/Debian Linux** for package conversion tools
- **GitHub account** with Actions enabled
- **Git** for version control

### Required System Tools
- `appimage2deb` (installed via Snap)
- `alien` (for RPM conversion)
- `dpkg-dev` (for package validation)

## 🔧 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/your-username/appbinhub.git
cd appbinhub
```

### 2. Install Dependencies
```bash
cd scripts
pip install -r requirements.txt
```

### 3. Install System Tools
```bash
# Install conversion tools
sudo snap install appimage2deb
sudo apt-get update
sudo apt-get install alien dpkg-dev
```

### 4. Configure GitHub Token
```bash
# Set your GitHub Personal Access Token
export GITHUB_TOKEN="your_github_token_here"
```

### 5. Run System Verification
```bash
cd scripts
python verify_system.py
```

## 🎯 Usage

### Automated Operation (Recommended)
The system runs automatically via GitHub Actions:
- **Monitoring**: Every 4 hours
- **Website Deployment**: On any website changes
- **Manual Triggers**: Available via GitHub Actions UI

### Manual Operation
```bash
# Monitor AppImage repositories
cd scripts
python monitor.py

# Convert packages
python converter.py
```

## 📊 Current Status

- **Total Applications**: 0 (system ready for monitoring)
- **Supported Categories**: 10 (Games, Programming, Graphics, etc.)
- **Package Formats**: AppImage, .deb, .rpm
- **Update Frequency**: Every 4 hours
- **Website Theme**: Dark mode optimized

## 🔧 Configuration

### Monitored Repositories
Edit `scripts/config.py` to add repositories:
```python
APPIMAGE_REPOSITORIES = [
    "AppImage/AppImageKit",
    "AppImageCommunity/pkg2appimage",
    # Add more repositories
]
```

### Conversion Settings
Modify conversion tools in `config.py`:
```python
CONVERSION_TOOLS = {
    "appimage2deb": {
        "timeout": 300,
        "enabled": True
    }
}
```

## 📚 Documentation

- **[Setup Guide](docs/SETUP.md)** - Detailed installation and configuration
- **[User Guide](docs/USER_GUIDE.md)** - Website usage and application downloads
- **[Admin Guide](docs/ADMIN_GUIDE.md)** - System administration and maintenance
- **[Developer Guide](docs/DEVELOPER.md)** - Development setup and contribution
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Production deployment instructions
- **[API Reference](docs/API.md)** - JSON data structure and automation APIs

## 🛠️ Technology Stack

### Backend Automation
- **Python 3.9+** with requests, PyGithub, BeautifulSoup4
- **GitHub Actions** for CI/CD automation
- **appimage2deb** and **alien** for package conversion

### Frontend Website
- **HTML5/CSS3** with modern dark theme
- **Vanilla JavaScript** for dynamic functionality
- **Responsive design** for all device types
- **GitHub Pages** for static hosting

### Data Management
- **JSON-based** application database
- **Git version control** for data persistence
- **Automated backups** via GitHub repository

## 🔍 Troubleshooting

### Common Issues

**GitHub API Rate Limit**
```bash
Error: API rate limit exceeded
Solution: Wait for reset or use authenticated token
```

**Conversion Tool Missing**
```bash
Error: appimage2deb not found
Solution: sudo snap install appimage2deb
```

**Permission Errors**
```bash
Error: Permission denied
Solution: Check file permissions and GitHub token scope
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and test locally
4. Commit changes (`git commit -m 'Add amazing feature'`)
5. Push to branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

### Development Guidelines
- Follow PEP 8 Python style guidelines
- Add comprehensive error handling and logging
- Include unit tests for new features
- Update documentation for any changes

## 📈 Performance & Limits

### System Limits
- **Repository Size**: 1 GB maximum (GitHub Pages)
- **Bandwidth**: 100 GB/month (GitHub Pages)
- **JSON File Size**: 1 MB maximum per file
- **Package Size**: 100 MB maximum per converted package

### Performance Optimizations
- Efficient GitHub API rate limit management
- Parallel processing for package conversion
- Lazy loading for large application catalogs
- Optimized asset compression and caching

## 🔒 Security

### Best Practices
- GitHub Personal Access Token with minimal required permissions
- Token stored as GitHub Secret, never in code
- Package validation and checksum verification
- Regular security updates for dependencies

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **AppImage Project** for the universal packaging format
- **FreeDesktop.org** for desktop entry specifications  
- **GitHub** for hosting and automation platform
- **Open Source Community** for conversion tools and libraries

## 📞 Support

- **Documentation**: Check the `/docs/` directory for detailed guides
- **Issues**: Report bugs and feature requests on GitHub Issues
- **Discussions**: Join GitHub Discussions for questions and ideas
- **Logs**: Check GitHub Actions logs for troubleshooting

---

**Status**: ✅ System Ready | **Last Updated**: June 27, 2025 | **Version**: 1.0.0
