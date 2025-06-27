# AppBinHub Deployment Guide

This guide provides comprehensive instructions for deploying the AppBinHub system to production environments. It covers GitHub Pages deployment, GitHub Actions configuration, environment setup, and maintenance procedures.

## 🏗️ Deployment Architecture

### Overview

AppBinHub uses a modern CI/CD deployment architecture:
- **Static Website**: Hosted on GitHub Pages
- **Automation Backend**: Runs on GitHub Actions runners
- **Data Storage**: Git-based with JSON files
- **CDN**: GitHub Pages global CDN for fast content delivery

### Deployment Components

**GitHub Actions Workflows**
- `monitor-and-convert.yml`: Automated monitoring and conversion (3,767 chars)
- `deploy.yml`: Website deployment automation (4,760 chars)

**Hosting Infrastructure**
- **GitHub Pages**: Static website hosting with global CDN
- **GitHub Actions**: Ubuntu runners for automation tasks
- **GitHub Repository**: Source code and data storage

## 🚀 Production Deployment

### Prerequisites

**GitHub Repository Requirements**
- GitHub account with repository creation permissions
- GitHub Actions enabled on the repository
- GitHub Pages enabled with appropriate source configuration
- Personal Access Token with required permissions

**Required Permissions**
```
GitHub Personal Access Token Scopes:
- public_repo (for public repositories)
- workflow (for GitHub Actions)
- read:org (if monitoring organization repositories)
```

### Step-by-Step Deployment

**1. Repository Setup**
```bash
# Create new repository on GitHub
# Clone the AppBinHub repository
git clone https://github.com/your-username/appbinhub.git
cd appbinhub

# Configure remote for your deployment
git remote set-url origin https://github.com/your-username/your-appbinhub-repo.git
```

**2. GitHub Secrets Configuration**
Navigate to your repository → Settings → Secrets and variables → Actions

**Required Secrets:**
```
GITHUB_TOKEN: Your Personal Access Token
```

**Optional Secrets:**
```
DEPLOY_KEY: SSH deployment key (if using custom deployment)
NOTIFICATION_WEBHOOK: Webhook URL for deployment notifications
```

**3. GitHub Pages Configuration**
1. Go to repository Settings → Pages
2. Set Source to "GitHub Actions"
3. Configure custom domain (optional)
4. Enable "Enforce HTTPS"

**4. Workflow Configuration**
The system includes two main workflows:

**Monitor and Convert Workflow** (`monitor-and-convert.yml`)
- **Schedule**: Runs every 4 hours automatically
- **Triggers**: Schedule, manual dispatch, script changes
- **Function**: Monitors repositories and converts packages
- **Environment**: Ubuntu latest with Python 3.9+

**Deploy Workflow** (`deploy.yml`)
- **Triggers**: Website changes, manual dispatch
- **Function**: Deploys website to GitHub Pages
- **Validation**: JSON structure and asset optimization

**5. Initial Deployment**
```bash
# Push to main branch to trigger initial deployment
git add .
git commit -m "Initial deployment setup"
git push origin main

# Monitor deployment in GitHub Actions tab
```

### Environment Configuration

**Production Environment Variables**
```bash
# Set in GitHub repository secrets
GITHUB_TOKEN=ghp_your_production_token_here

# Optional environment-specific settings
APPBINHUB_ENV=production
APPBINHUB_LOG_LEVEL=INFO
APPBINHUB_MONITORING_INTERVAL=4h
```

**Configuration Customization**
Edit `scripts/config.py` for production settings:
```python
# Production repository list
APPIMAGE_REPOSITORIES = [
    "AppImage/AppImageKit",
    "AppImageCommunity/pkg2appimage",
    # Add your monitored repositories
]

# Production logging settings
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(levelname)s - %(message)s"
}

# Production conversion settings
CONVERSION_TOOLS = {
    "appimage2deb": {
        "timeout": 300,
        "enabled": True,
        "retry_attempts": 3
    }
}
```

## 🔧 GitHub Actions Configuration

### Workflow Customization

**Monitoring Schedule Adjustment**
Edit `.github/workflows/monitor-and-convert.yml`:
```yaml
on:
  schedule:
    - cron: '0 */4 * * *'  # Every 4 hours (default)
    # - cron: '0 */2 * * *'  # Every 2 hours (more frequent)
    # - cron: '0 8,20 * * *'  # Twice daily at 8 AM and 8 PM
```

**Manual Trigger Configuration**
Both workflows support manual triggering:
```yaml
on:
  workflow_dispatch:  # Enables manual trigger from GitHub UI
    inputs:
      force_rebuild:
        description: 'Force complete rebuild'
        required: false
        default: 'false'
```

**Environment-Specific Workflows**
Create separate workflows for different environments:
```bash
.github/workflows/
├── monitor-and-convert.yml      # Production
├── monitor-and-convert-dev.yml  # Development
└── deploy-staging.yml           # Staging environment
```

### Runner Configuration

**GitHub-Hosted Runners**
```yaml
jobs:
  monitor:
    runs-on: ubuntu-latest  # Default: Ubuntu 22.04
    # runs-on: ubuntu-20.04  # Alternative: Ubuntu 20.04
    # runs-on: windows-latest  # Windows (if needed)
    # runs-on: macos-latest   # macOS (if needed)
```

**Self-Hosted Runners** (Advanced)
```yaml
jobs:
  monitor:
    runs-on: self-hosted
    # Requires setting up your own runner
    # See GitHub documentation for self-hosted runner setup
```

## 🌐 GitHub Pages Deployment

### Static Website Deployment

**Automatic Deployment**
The deploy workflow automatically:
1. Validates JSON data structure
2. Optimizes website assets
3. Deploys to GitHub Pages
4. Invalidates CDN cache

**Manual Deployment**
```bash
# Trigger manual deployment
gh workflow run deploy.yml

# Or via GitHub web interface:
# Repository → Actions → Deploy → Run workflow
```

### Custom Domain Configuration

**Setting Up Custom Domain**
1. Add CNAME file to website root:
```bash
echo "your-domain.com" > website/CNAME
```

2. Configure DNS records:
```
Type: CNAME
Name: www (or @)
Value: your-username.github.io
```

3. Enable custom domain in repository settings
4. Enable "Enforce HTTPS" after DNS propagation

**SSL Certificate**
GitHub Pages automatically provides SSL certificates for:
- GitHub.io domains (automatic)
- Custom domains (via Let's Encrypt)

### Performance Optimization

**Asset Optimization**
```yaml
# In deploy workflow
- name: Optimize Assets
  run: |
    # Minify CSS
    find website/css -name "*.css" -exec cleancss -o {} {} \;

    # Optimize images
    find website/assets -name "*.png" -exec optipng {} \;

    # Compress JSON
    find website/data -name "*.json" -exec gzip -k {} \;
```

**Caching Configuration**
```html
<!-- In website/index.html -->
<meta http-equiv="Cache-Control" content="public, max-age=3600">
<meta http-equiv="Expires" content="3600">
```

## 📊 Monitoring and Maintenance

### Deployment Monitoring

**GitHub Actions Monitoring**
```bash
# Monitor workflow status
gh run list --limit 10

# View specific workflow run
gh run view [run-id]

# Download workflow logs
gh run download [run-id]
```

**Website Health Monitoring**
```bash
# Check website availability
curl -I https://your-username.github.io/appbinhub

# Monitor response time
curl -w "@curl-format.txt" -o /dev/null -s https://your-domain.com

# Check JSON data validity
curl -s https://your-domain.com/data/applications.json | python -m json.tool
```

### Automated Monitoring Setup

**Health Check Script**
```bash
#!/bin/bash
# health-check.sh

WEBSITE_URL="https://your-domain.com"
EXPECTED_STATUS=200

# Check website status
STATUS=$(curl -s -o /dev/null -w "%{http_code}" $WEBSITE_URL)

if [ $STATUS -eq $EXPECTED_STATUS ]; then
    echo "✅ Website is healthy (Status: $STATUS)"
else
    echo "❌ Website issue detected (Status: $STATUS)"
    # Send notification (email, Slack, etc.)
fi

# Check JSON data
curl -s $WEBSITE_URL/data/applications.json | python -m json.tool > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ JSON data is valid"
else
    echo "❌ JSON data validation failed"
fi
```

**Monitoring Workflow**
```yaml
# .github/workflows/health-check.yml
name: Health Check
on:
  schedule:
    - cron: '*/30 * * * *'  # Every 30 minutes

jobs:
  health-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Health Check
        run: ./scripts/health-check.sh
```

## 🔒 Security Configuration

### Production Security

**Repository Security**
```bash
# Enable security features in repository settings:
# - Dependency graph
# - Dependabot alerts
# - Dependabot security updates
# - Code scanning alerts
# - Secret scanning alerts
```

**Workflow Security**
```yaml
# Secure workflow permissions
permissions:
  contents: read
  pages: write
  id-token: write
  actions: read

# Use specific action versions
- uses: actions/checkout@v4  # Specific version
- uses: actions/setup-python@v4  # Not @main
```

**Token Security**
```bash
# Token best practices:
# 1. Use minimal required permissions
# 2. Set token expiration (90 days maximum)
# 3. Rotate tokens regularly
# 4. Store only in GitHub Secrets
# 5. Never commit tokens to repository
```

### Access Control

**Branch Protection**
```bash
# Configure branch protection rules:
# - Require pull request reviews
# - Require status checks to pass
# - Require branches to be up to date
# - Restrict pushes to main branch
```

**Deployment Protection**
```yaml
# Environment protection rules
environment:
  name: production
  protection_rules:
    - type: required_reviewers
      reviewers: ["admin-username"]
    - type: wait_timer
      minutes: 5
```

## 🚨 Troubleshooting Deployment

### Common Deployment Issues

**GitHub Actions Failures**
```bash
# Issue: Workflow fails with permission errors
# Solution: Check GitHub token permissions and secrets

# Issue: Python dependencies installation fails
# Solution: Update requirements.txt or use specific versions

# Issue: Conversion tools not available
# Solution: Verify tool installation in workflow
```

**GitHub Pages Issues**
```bash
# Issue: Website not updating after deployment
# Solution: Check GitHub Pages build status and clear browser cache

# Issue: 404 errors on custom domain
# Solution: Verify DNS configuration and CNAME file

# Issue: SSL certificate errors
# Solution: Wait for certificate provisioning or check domain configuration
```

**Data Synchronization Issues**
```bash
# Issue: JSON data not updating
# Solution: Check monitoring workflow execution and GitHub API limits

# Issue: Broken download links
# Solution: Verify package conversion and storage locations

# Issue: Website showing old data
# Solution: Clear CDN cache and check deployment workflow
```

### Emergency Procedures

**Rollback Deployment**
```bash
# Rollback to previous version
git revert HEAD
git push origin main

# Or rollback to specific commit
git reset --hard [commit-hash]
git push --force origin main
```

**Emergency Maintenance Mode**
```html
<!-- Create maintenance.html in website root -->
<!DOCTYPE html>
<html>
<head>
    <title>AppBinHub - Maintenance</title>
</head>
<body>
    <h1>Maintenance in Progress</h1>
    <p>AppBinHub is currently undergoing maintenance. Please check back soon.</p>
</body>
</html>
```

**Data Recovery**
```bash
# Restore from Git history
git checkout HEAD~1 -- website/data/

# Or restore from backup
tar -xzf backup-latest.tar.gz
git add website/data/
git commit -m "Restore data from backup"
git push origin main
```

## 📈 Scaling and Performance

### Performance Optimization

**GitHub Pages Optimization**
- Enable compression for text assets
- Optimize image sizes and formats
- Implement lazy loading for large datasets
- Use efficient CSS and JavaScript

**GitHub Actions Optimization**
```yaml
# Cache dependencies
- uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}

# Parallel job execution
strategy:
  matrix:
    repository: [repo1, repo2, repo3]
```

**Data Management Optimization**
```bash
# Split large JSON files
python scripts/split_json.py --max-size 1MB

# Implement data pagination
python scripts/paginate_data.py --items-per-page 100

# Compress static assets
gzip -k website/data/*.json
```

### Scaling Considerations

**Repository Size Management**
- Monitor repository size (1GB GitHub limit)
- Implement data archiving for old versions
- Use Git LFS for large binary files if needed
- Regular cleanup of temporary files

**API Rate Limit Management**
- Monitor GitHub API usage
- Implement request caching
- Use conditional requests with ETags
- Distribute monitoring across multiple tokens if needed

## 📋 Deployment Checklist

### Pre-Deployment Checklist
- [ ] Repository forked and configured
- [ ] GitHub secrets configured
- [ ] GitHub Pages enabled
- [ ] Workflows tested in development
- [ ] Custom domain configured (if applicable)
- [ ] SSL certificate verified
- [ ] Monitoring scripts configured

### Post-Deployment Checklist
- [ ] Website accessibility verified
- [ ] GitHub Actions workflows executing successfully
- [ ] JSON data loading correctly
- [ ] Search and filtering functionality working
- [ ] Theme switching operational
- [ ] Mobile responsiveness verified
- [ ] Performance metrics acceptable

### Maintenance Checklist
- [ ] Weekly workflow execution review
- [ ] Monthly dependency updates
- [ ] Quarterly security audit
- [ ] Regular backup verification
- [ ] Performance monitoring
- [ ] Error log analysis

## 📞 Deployment Support

### Support Resources

**GitHub Documentation**
- GitHub Pages deployment guide
- GitHub Actions workflow documentation
- Repository security best practices
- Custom domain configuration

**Community Support**
- GitHub Community Forum
- Stack Overflow (github-pages, github-actions tags)
- AppBinHub project discussions
- Open source community resources

### Getting Help

**Internal Support**
- Check deployment logs in GitHub Actions
- Review troubleshooting section in documentation
- Validate configuration against working examples
- Test in development environment first

**External Support**
- Create issue in project repository
- Post question in GitHub Discussions
- Contact GitHub Support for platform issues
- Consult community forums for general questions

---

## 📝 Quick Reference

### Essential Commands
```bash
# Deploy manually
gh workflow run deploy.yml

# Check deployment status
gh run list --workflow=deploy.yml

# Monitor website health
curl -I https://your-domain.com

# View workflow logs
gh run view [run-id]
```

### Important URLs
- **GitHub Actions**: https://github.com/your-username/appbinhub/actions
- **GitHub Pages Settings**: https://github.com/your-username/appbinhub/settings/pages
- **Repository Secrets**: https://github.com/your-username/appbinhub/settings/secrets/actions
- **Website**: https://your-username.github.io/appbinhub

### Configuration Files
- `.github/workflows/deploy.yml`: Deployment workflow
- `.github/workflows/monitor-and-convert.yml`: Monitoring workflow
- `website/CNAME`: Custom domain configuration
- `scripts/config.py`: System configuration

---

**Last Updated**: June 27, 2025  
**Version**: 1.0.0  
**Environment**: Production  
**Support**: GitHub Issues and Documentation
