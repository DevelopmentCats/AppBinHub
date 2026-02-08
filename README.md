# AppBinHub

> **Live Site:** [https://developmentcats.github.io/AppBinHub/](https://developmentcats.github.io/AppBinHub/)

Automated AppImage conversion hub that monitors sources, converts packages to multiple formats (DEB, RPM, TAR.GZ), and hosts them via GitHub Releases with a clean web catalog.

## 🚀 Features

- **Automated Monitoring**: Watches AppImage sources for new releases (twice daily)
- **Cross-Platform Conversion**: Creates DEB, RPM, and TAR.GZ packages from AppImages
- **Cross-Compilation**: Builds ARM packages on x86_64 runners (no QEMU needed)
- **GitHub Releases Storage**: Packages stored as release assets (no git bloat)
- **Docker-Based Pipeline**: Fast conversion with pre-built container image
- **Clean Web Interface**: Browse and download packages from GitHub Pages

## 📦 Architecture

```
Monitor (Python) → Convert (Docker) → Upload (GitHub Releases) → Website (Static)
     ↓                  ↓                      ↓                        ↓
  Cursor API     x86_64 + ARM pkgs    cursor-ai-editor-v2.4.28    JSON catalog
```

### Key Components

- **Monitor Script** (`monitor.py`) - Checks sources for new AppImage releases
- **Converter** (`converter.py`) - Extracts AppImages and builds packages
  - Uses `unsquashfs` for extraction (works cross-architecture)
  - Uses `dpkg-deb` for DEB packages
  - Uses `rpmbuild` for native x86_64 RPMs
  - Uses **FPM** for cross-compiled ARM RPMs
- **Docker Image** (`ghcr.io/developmentcats/appbinhub-converter`) - Pre-built with all tools
- **GitHub Actions** - Automated pipeline runs twice daily (8 AM/PM UTC)
- **GitHub Releases** - Package storage (bypasses 100MB git file limit)

## 🏃 Quick Start

### For Users (Download Packages)

Visit **[https://developmentcats.github.io/AppBinHub/](https://developmentcats.github.io/AppBinHub/)** to browse and download converted packages.

### For Developers (Run Locally)

```bash
# Clone
git clone https://github.com/DevelopmentCats/AppBinHub.git
cd AppBinHub

# Install Python deps
cd scripts && pip install -r requirements.txt

# Run monitor
export GITHUB_TOKEN="your_token"
python monitor.py

# Run converter (requires Docker image OR manual tool install)
python converter.py
```

### Adding New Sources

Edit `scripts/config.py`:

```python
DIRECT_API_ENDPOINTS = {
    "your-app": {
        "name": "Your App Name",
        "category": "development",
        "known_architectures": {
            "x86_64": {
                "api_url": "https://example.com/download/linux-x64"
            }
        }
    }
}
```

## 🔧 How It Works

### 1. Monitor Phase
- Checks configured sources (Cursor API, GitHub repos, etc.)
- Compares versions in `website/data/applications.json`
- Marks new/updated apps as `conversion_status: "pending"`

### 2. Convert Phase (runs if pending apps exist)
- Pulls Docker image with conversion tools
- Downloads AppImages for all architectures
- Extracts with `unsquashfs` (cross-platform compatible)
- Builds packages:
  - **x86_64**: DEB (dpkg-deb), RPM (rpmbuild), TAR.GZ
  - **aarch64**: DEB (dpkg-deb), RPM (FPM cross-compile), TAR.GZ
  - **armv7l**: Same as aarch64 (if sources available)

### 3. Upload Phase
- Creates/updates GitHub Release (tag: `app-name-vX.X.X`)
- Uploads all packages as release assets
- Updates JSON with download URLs
- Commits updated JSON to repo

### 4. Website Update
- GitHub Pages auto-deploys on JSON changes
- Users browse catalog and download from releases

## 📊 Current Status

- **Applications**: 1 (Cursor AI Editor)
- **Architectures**: x86_64, aarch64
- **Package Formats**: DEB, RPM, TAR.GZ
- **Update Frequency**: Twice daily (8 AM/PM UTC)
- **Conversion Time**: ~7-9 minutes per run

## 🛠️ Technology Stack

### Conversion Pipeline
- **Python 3.11+** (monitoring & conversion logic)
- **Docker** (containerized build environment)
- **FPM** (Effing Package Management - ARM RPM cross-compilation)
- **GitHub Actions** (CI/CD automation)
- **GitHub Releases** (package storage)

### Tools in Docker Image
- `unsquashfs` - AppImage extraction
- `dpkg-deb` - DEB package creation
- `rpmbuild` - RPM package creation (x86_64)
- `fpm` - RPM cross-compilation (ARM)
- `gh` - GitHub CLI (release uploads)

### Website
- **Static HTML/CSS/JS** (dark theme)
- **GitHub Pages** (hosting)
- **JSON API** (application metadata)

## 🎯 Design Decisions

### Why Docker?
Pre-built image with all tools saves ~2 minutes per run vs installing on every workflow.

### Why FPM for ARM RPMs?
Native `rpmbuild` can't cross-compile. FPM builds ARM RPMs on x86_64 without QEMU overhead.

### Why GitHub Releases?
- No 100MB git file size limit
- Free unlimited storage/bandwidth for public repos
- Built-in CDN
- Clean separation: git = metadata, releases = binaries

### Why Preserve Conversion State?
Only convert when version changes. Prevents wasting 8 minutes of CI time on every monitor run.

## 📝 Contributing

1. Fork the repo
2. Create a feature branch
3. Make changes and test locally
4. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file

## 🔗 Links

- **Website**: [https://developmentcats.github.io/AppBinHub/](https://developmentcats.github.io/AppBinHub/)
- **GitHub**: [https://github.com/DevelopmentCats/AppBinHub](https://github.com/DevelopmentCats/AppBinHub)
- **Docker Image**: [ghcr.io/developmentcats/appbinhub-converter](https://github.com/DevelopmentCats/AppBinHub/pkgs/container/appbinhub-converter)
- **Releases**: [GitHub Releases](https://github.com/DevelopmentCats/AppBinHub/releases)

---

**Status**: ✅ Operational | **Last Updated**: 2026-02-08
