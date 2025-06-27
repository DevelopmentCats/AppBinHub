# AppBinHub Setup Guide

Complete setup instructions for deploying the AppBinHub automation system.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [GitHub Repository Setup](#github-repository-setup)
3. [Environment Configuration](#environment-configuration)
4. [Local Development Setup](#local-development-setup)
5. [GitHub Actions Configuration](#github-actions-configuration)
6. [GitHub Pages Setup](#github-pages-setup)
7. [Testing the System](#testing-the-system)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements
- **Operating System**: Ubuntu 20.04+ or Debian-based Linux
- **Python**: Version 3.9 or higher
- **Git**: Latest version
- **GitHub Account**: With Actions and Pages enabled
- **Internet Connection**: For downloading AppImages and API access

### Required Permissions
- GitHub repository admin access
- Ability to create GitHub Personal Access Tokens
- Sudo access on local system (for tool installation)

## GitHub Repository Setup

### 1. Create New Repository
```bash
# Create a new repository on GitHub
# Name: appbinhub (or your preferred name)
# Visibility: Public (required for GitHub Pages)
# Initialize with README: No (we'll add our own)
```

### 2. Clone and Setup Repository
```bash
# Clone your repository
git clone https://github.com/YOUR_USERNAME/appbinhub.git
cd appbinhub

# Copy AppBinHub files to repository
cp -r /path/to/appbinhub/final/* .

# Initial commit
git add .
git commit -m "Initial AppBinHub setup"
git push origin main
```

### 3. Repository Structure Verification
Ensure your repository has this structure:
```
appbinhub/
├── .github/
│   └── workflows/
│       ├── monitor-and-convert.yml
│       └── deploy.yml
├── scripts/
│   ├── monitor.py
│   ├── converter.py
│   ├── config.py
│   └── requirements.txt
├── website/
│   └── data/
│       ├── applications.json
│       ├── categories.json
│       └── changelog.json
└── docs/
    ├── README.md
    └── SETUP.md
```

## Environment Configuration

### 1. Create GitHub Personal Access Token
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Click "Generate new token (classic)"
3. Set expiration (recommend 90 days)
4. Select scopes:
   - `repo` (Full control of private repositories)
   - `workflow` (Update GitHub Action workflows)
   - `read:org` (Read org and team membership)

### 2. Add Repository Secrets
1. Go to your repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add the following secrets:

```
Name: GITHUB_TOKEN
Value: [Your Personal Access Token]
```

### 3. Environment Variables (Local Development)
Create a `.env` file in the scripts directory:
```bash
cd scripts
cat > .env << 'EOF'
GITHUB_TOKEN=your_personal_access_token_here
EOF

# Add .env to .gitignore to prevent committing secrets
echo "scripts/.env" >> .gitignore
```

## Local Development Setup

### 1. Install Python Dependencies
```bash
cd scripts
pip install -r requirements.txt
```

### 2. Install System Tools

#### Install appimage2deb (via Snap)
```bash
sudo snap install appimage2deb

# Verify installation
appimage2deb --version
```

#### Install alien and dpkg tools
```bash
sudo apt-get update
sudo apt-get install -y alien dpkg-dev

# Verify installations
alien --version
dpkg-deb --version
```

### 3. Test Local Setup
```bash
# Test monitoring script (dry run)
cd scripts
python -c "
import monitor
try:
    monitor.AppImageMonitor()
    print('✅ Monitor setup successful')
except Exception as e:
    print(f'❌ Monitor setup failed: {e}')
"

# Test converter script
python -c "
import converter
try:
    converter.AppImageConverter()
    print('✅ Converter setup successful')
except Exception as e:
    print(f'❌ Converter setup failed: {e}')
"
```

## GitHub Actions Configuration

### 1. Enable GitHub Actions
1. Go to your repository → Actions tab
2. If prompted, click "I understand my workflows, go ahead and enable them"

### 2. Verify Workflow Files
Check that workflow files are present:
- `.github/workflows/monitor-and-convert.yml`
- `.github/workflows/deploy.yml`

### 3. Test Workflow Execution
```bash
# Trigger monitor workflow manually
# Go to Actions tab → Monitor and Convert → Run workflow

# Check workflow status
# Green checkmark = success
# Red X = failure (check logs)
```

### 4. Workflow Permissions
Ensure workflows have proper permissions:
1. Go to Settings → Actions → General
2. Under "Workflow permissions":
   - Select "Read and write permissions"
   - Check "Allow GitHub Actions to create and approve pull requests"

## GitHub Pages Setup

### 1. Enable GitHub Pages
1. Go to repository Settings → Pages
2. Under "Source":
   - Select "GitHub Actions"
3. Click "Save"

### 2. Configure Pages Settings
```yaml
# Verify deploy.yml has correct permissions
permissions:
  contents: read
  pages: write
  id-token: write
```

### 3. Test Pages Deployment
1. Make a change to any file in `website/` directory
2. Commit and push changes
3. Check Actions tab for deployment workflow
4. Visit your GitHub Pages URL: `https://YOUR_USERNAME.github.io/appbinhub`

## Testing the System

### 1. Manual Testing

#### Test Monitoring Script
```bash
cd scripts
export GITHUB_TOKEN="your_token_here"
python monitor.py

# Check outputs:
# - monitor.log file created
# - website/data/applications.json updated
# - No critical errors in logs
```

#### Test Conversion Script
```bash
cd scripts
python converter.py

# Check outputs:
# - converter.log file created
# - converted_packages/ directory created
# - Package conversion attempts logged
```

### 2. Automated Testing

#### Trigger GitHub Actions
```bash
# Push a change to trigger workflows
echo "# Test change" >> README.md
git add README.md
git commit -m "Test workflow trigger"
git push origin main

# Monitor workflow execution in Actions tab
```

#### Verify Automation
1. Check Actions tab for successful workflow runs
2. Verify website deployment at GitHub Pages URL
3. Check that JSON files are updated automatically
4. Confirm logs are uploaded as artifacts

### 3. End-to-End Testing
1. Wait for scheduled workflow (runs every 4 hours)
2. Check for new applications in JSON files
3. Verify website displays updated content
4. Test package download links

## Troubleshooting

### Common Setup Issues

#### 1. GitHub Token Issues
```
Error: GITHUB_TOKEN environment variable is required
```
**Solutions:**
- Verify token is added to repository secrets
- Check token permissions include `repo` and `workflow`
- Ensure token hasn't expired

#### 2. Tool Installation Failures
```
Error: appimage2deb tool not found
```
**Solutions:**
```bash
# Reinstall appimage2deb
sudo snap remove appimage2deb
sudo snap install appimage2deb

# Check snap installation
snap list | grep appimage2deb
```

#### 3. Workflow Permission Errors
```
Error: Resource not accessible by integration
```
**Solutions:**
- Enable "Read and write permissions" in repository settings
- Check workflow file permissions section
- Verify repository secrets are properly set

#### 4. GitHub Pages Not Deploying
```
Error: Pages deployment failed
```
**Solutions:**
- Ensure repository is public
- Check Pages settings use "GitHub Actions" source
- Verify deploy.yml workflow permissions
- Check website/ directory structure

### Debug Mode

#### Enable Detailed Logging
```python
# Edit scripts/config.py
LOGGING_CONFIG["level"] = "DEBUG"
```

#### Check Workflow Logs
1. Go to Actions tab
2. Click on failed workflow run
3. Expand log sections to see detailed output
4. Download artifacts for local analysis

### Performance Issues

#### Large Repository Size
```bash
# Check repository size
du -sh .
git count-objects -vH

# Clean up if needed
git gc --aggressive --prune=now
```

#### Slow Workflow Execution
- Check GitHub Actions usage limits
- Optimize script execution time
- Consider reducing monitoring frequency

### Validation Commands

#### Verify JSON Structure
```bash
cd website/data
python -m json.tool applications.json > /dev/null && echo "✅ Valid JSON" || echo "❌ Invalid JSON"
python -m json.tool categories.json > /dev/null && echo "✅ Valid JSON" || echo "❌ Invalid JSON"
python -m json.tool changelog.json > /dev/null && echo "✅ Valid JSON" || echo "❌ Invalid JSON"
```

#### Check File Permissions
```bash
# Ensure scripts are executable
chmod +x scripts/*.py

# Check file ownership
ls -la scripts/
```

## Maintenance

### Regular Tasks
1. **Token Rotation**: Update GitHub token every 90 days
2. **Log Cleanup**: Monitor log file sizes
3. **Repository Size**: Check against GitHub limits
4. **Dependency Updates**: Update Python packages regularly

### Monitoring
- Check GitHub Actions usage in repository insights
- Monitor workflow success rates
- Review error logs for patterns
- Verify website accessibility

### Updates
```bash
# Update Python dependencies
cd scripts
pip install --upgrade -r requirements.txt

# Update system tools
sudo snap refresh appimage2deb
sudo apt-get update && sudo apt-get upgrade alien dpkg-dev
```

## Support

If you encounter issues not covered in this guide:

1. **Check Logs**: Review workflow logs and local log files
2. **GitHub Issues**: Search existing issues in the repository
3. **Documentation**: Review README.md and other docs
4. **Community**: Check AppImage community resources

## Next Steps

After successful setup:
1. Customize monitored repositories in `config.py`
2. Add website frontend (HTML/CSS/JS)
3. Configure custom domain for GitHub Pages
4. Set up monitoring alerts
5. Add more conversion formats

---

**Setup Complete!** Your AppBinHub automation system should now be running and monitoring AppImage repositories automatically.