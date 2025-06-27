# AppBinHub Administrator Guide

This guide provides comprehensive information for system administrators managing the AppBinHub application repository system. It covers installation, configuration, monitoring, maintenance, and troubleshooting procedures.

## 🏗️ System Overview

AppBinHub is a fully automated system consisting of:
- **Python automation scripts** for monitoring and conversion
- **GitHub Actions workflows** for scheduled execution
- **Static website** hosted on GitHub Pages
- **JSON-based data storage** for application metadata

### Architecture Components

**Backend Automation**
- `monitor.py`: GitHub repository monitoring (13,610 lines)
- `converter.py`: Package conversion system (15,116 lines)
- `config.py`: System configuration (5,997 lines)
- `verify_system.py`: System validation (7,082 lines)

**GitHub Actions Workflows**
- `monitor-and-convert.yml`: Automated monitoring and conversion
- `deploy.yml`: Website deployment automation

**Data Management**
- JSON files for application metadata
- Git-based version control and backup
- Automated data validation and cleanup

## 🔧 System Installation

### Prerequisites Verification

Before installation, verify system requirements:

```bash
# Run system verification
cd scripts
python verify_system.py
```

**Required Components**
- Python 3.9+ with pip
- Git version control
- GitHub account with Actions enabled
- Ubuntu/Debian Linux environment

### Installation Steps

**1. Repository Setup**
```bash
# Clone repository
git clone https://github.com/your-username/appbinhub.git
cd appbinhub

# Set up Python environment
cd scripts
pip install -r requirements.txt
```

**2. System Tools Installation**
```bash
# Install conversion tools
sudo snap install appimage2deb
sudo apt-get update
sudo apt-get install alien dpkg-dev

# Verify tool installation
appimage2deb --version
alien --version
dpkg-deb --version
```

**3. GitHub Configuration**
```bash
# Set GitHub token (required for API access)
export GITHUB_TOKEN="your_personal_access_token"

# Configure Git for automated commits
git config user.name "AppBinHub Bot"
git config user.email "bot@appbinhub.com"
```

**4. GitHub Actions Setup**
- Navigate to repository Settings → Secrets and variables → Actions
- Add `GITHUB_TOKEN` secret with your Personal Access Token
- Enable GitHub Actions in repository settings
- Enable GitHub Pages with source set to "GitHub Actions"

## ⚙️ Configuration Management

### Primary Configuration File

Edit `scripts/config.py` for system configuration:

**Repository Monitoring**
```python
APPIMAGE_REPOSITORIES = [
    "AppImage/AppImageKit",
    "AppImageCommunity/pkg2appimage",
    # Add additional repositories here
]
```

**GitHub API Settings**
```python
GITHUB_TOKEN_ENV_VAR = "GITHUB_TOKEN"
API_RATE_LIMIT_BUFFER = 100  # Reserve API calls
REQUEST_TIMEOUT = 30  # Seconds
```

**Conversion Tool Configuration**
```python
CONVERSION_TOOLS = {
    "appimage2deb": {
        "timeout": 300,
        "enabled": True,
        "retry_attempts": 3
    },
    "alien": {
        "timeout": 180,
        "enabled": True
    }
}
```

**Logging Configuration**
```python
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(levelname)s - %(message)s",
    "file": "appbinhub.log"
}
```

### Environment Variables

**Required Variables**
```bash
# GitHub API authentication
export GITHUB_TOKEN="ghp_your_token_here"

# Optional: Custom configuration
export APPBINHUB_CONFIG_PATH="/path/to/custom/config.py"
export APPBINHUB_LOG_LEVEL="DEBUG"
```

## 🔍 Monitoring and Logging

### System Monitoring

**Automated Monitoring Features**
- GitHub API integration with rate limit management
- Repository monitoring for new AppImage releases
- Metadata extraction and validation
- Error handling and recovery procedures
- Comprehensive logging system

**Monitoring Schedule**
- **Automatic**: Every 4 hours via GitHub Actions
- **Manual**: Triggered via GitHub Actions UI
- **On-demand**: Direct script execution

### Log Management

**Log Files Location**
```bash
scripts/
├── monitor.log          # Repository monitoring logs
├── converter.log        # Package conversion logs
├── appbinhub.log       # General system logs
└── error.log           # Error-specific logs
```

**Log Levels**
- **DEBUG**: Detailed execution information
- **INFO**: Normal operation status
- **WARNING**: Non-critical issues
- **ERROR**: Critical failures requiring attention

**Log Rotation**
```bash
# Manual log cleanup (run weekly)
cd scripts
find . -name "*.log" -size +10M -delete
find . -name "*.log.*" -mtime +30 -delete
```

### Performance Monitoring

**Key Metrics to Monitor**
- GitHub API rate limit usage
- Conversion success/failure rates
- Website response times
- Repository size growth
- Bandwidth usage

**Monitoring Commands**
```bash
# Check system status
python verify_system.py

# Monitor GitHub API rate limits
python -c "from scripts.monitor import check_rate_limit; check_rate_limit()"

# Check conversion tool availability
appimage2deb --version && alien --version
```

## 🚀 GitHub Actions Management

### Workflow Configuration

**Monitor and Convert Workflow**
- **File**: `.github/workflows/monitor-and-convert.yml`
- **Schedule**: Every 4 hours (`0 */4 * * *`)
- **Triggers**: Schedule, manual dispatch, script changes
- **Environment**: Ubuntu latest with Python 3.9+

**Deploy Workflow**
- **File**: `.github/workflows/deploy.yml`
- **Triggers**: Website changes, manual dispatch
- **Function**: Deploy website to GitHub Pages
- **Validation**: JSON structure and asset optimization

### Workflow Management

**Manual Workflow Execution**
1. Navigate to repository → Actions tab
2. Select desired workflow
3. Click "Run workflow" button
4. Monitor execution in real-time

**Workflow Debugging**
```bash
# Download workflow logs
gh run download [run-id] --dir ./logs

# View recent workflow runs
gh run list --limit 10

# Check workflow status
gh run view [run-id]
```

### Secrets Management

**Required GitHub Secrets**
- `GITHUB_TOKEN`: Personal Access Token for API access
- `DEPLOY_KEY`: SSH key for deployment (if needed)

**Secret Rotation**
1. Generate new Personal Access Token
2. Update `GITHUB_TOKEN` secret in repository settings
3. Test workflow execution
4. Revoke old token

## 📊 Data Management

### JSON Data Structure

**Primary Data Files**
- `website/data/applications.json`: Application metadata
- `website/data/categories.json`: Category definitions (10 categories)
- `website/data/changelog.json`: Update history

**Data Validation**
```bash
# Validate JSON structure
cd scripts
python -c "import json; json.load(open('../website/data/applications.json'))"

# Check data integrity
python verify_system.py --check-data
```

### Database Maintenance

**Regular Maintenance Tasks**
```bash
# Clean up outdated entries (monthly)
python scripts/cleanup.py --remove-outdated

# Validate all package links (weekly)
python scripts/validate_links.py

# Optimize JSON file sizes (as needed)
python scripts/optimize_data.py
```

**Backup Procedures**
```bash
# Create data backup
tar -czf backup-$(date +%Y%m%d).tar.gz website/data/

# Restore from backup
tar -xzf backup-YYYYMMDD.tar.gz
```

## 🔒 Security Management

### Access Control

**GitHub Repository Security**
- Enable branch protection for main branch
- Require pull request reviews
- Enable security alerts and dependency scanning
- Regular security audit of dependencies

**API Token Security**
```bash
# Generate token with minimal required permissions:
# - public_repo (for public repositories)
# - read:org (if monitoring organization repositories)

# Token rotation schedule: Every 90 days
# Store tokens securely in GitHub Secrets only
```

### Security Monitoring

**Regular Security Tasks**
```bash
# Update dependencies (monthly)
cd scripts
pip install --upgrade -r requirements.txt

# Security audit
pip audit

# Check for vulnerable packages
safety check -r requirements.txt
```

## 🛠️ Maintenance Procedures

### Daily Maintenance

**Automated Tasks**
- Repository monitoring (every 4 hours)
- Package conversion processing
- Website deployment updates
- Log rotation and cleanup

**Manual Checks**
- Review GitHub Actions execution logs
- Monitor system resource usage
- Check error logs for critical issues

### Weekly Maintenance

**System Health Checks**
```bash
# Run comprehensive system verification
python verify_system.py --full-check

# Check conversion tool status
appimage2deb --version
alien --version

# Validate website functionality
curl -I https://your-username.github.io/appbinhub
```

**Data Maintenance**
```bash
# Validate all JSON data files
python scripts/validate_data.py

# Check for broken download links
python scripts/check_links.py

# Clean up temporary files
find /tmp -name "appbinhub-*" -mtime +7 -delete
```

### Monthly Maintenance

**Performance Optimization**
```bash
# Analyze repository size
du -sh .git/
git gc --aggressive

# Optimize JSON data files
python scripts/optimize_json.py

# Review and clean up old logs
find scripts/ -name "*.log.*" -mtime +30 -delete
```

**Security Updates**
```bash
# Update system packages
sudo apt update && sudo apt upgrade

# Update Python dependencies
pip install --upgrade -r requirements.txt

# Rotate GitHub tokens (quarterly)
```

## 🚨 Troubleshooting

### Common Issues

**GitHub API Rate Limit Exceeded**
```bash
# Symptoms: Monitor script fails with rate limit error
# Check current rate limit status
curl -H "Authorization: token $GITHUB_TOKEN"      https://api.github.com/rate_limit

# Solutions:
# 1. Wait for rate limit reset (shown in response)
# 2. Reduce monitoring frequency temporarily
# 3. Use authenticated requests (ensure GITHUB_TOKEN is set)
```

**Conversion Tool Failures**
```bash
# Symptoms: Package conversion fails
# Check tool availability
which appimage2deb alien dpkg-deb

# Reinstall tools if missing
sudo snap install appimage2deb
sudo apt-get install --reinstall alien dpkg-dev

# Check permissions
ls -la /snap/bin/appimage2deb
```

**Website Deployment Issues**
```bash
# Symptoms: Website not updating after changes
# Check GitHub Pages status
curl -I https://your-username.github.io/appbinhub

# Verify GitHub Actions execution
gh run list --workflow=deploy.yml

# Manual deployment trigger
gh workflow run deploy.yml
```

**JSON Data Corruption**
```bash
# Symptoms: Website shows errors or missing data
# Validate JSON syntax
python -m json.tool website/data/applications.json

# Restore from Git history if corrupted
git checkout HEAD~1 -- website/data/applications.json
```

### Performance Issues

**High Memory Usage**
```bash
# Monitor Python process memory
ps aux | grep python

# Optimize large JSON files
python scripts/split_large_json.py

# Implement pagination for large datasets
```

**Slow Conversion Processing**
```bash
# Check available disk space
df -h

# Monitor conversion process
top -p $(pgrep -f converter.py)

# Increase timeout values in config.py if needed
```

### Emergency Procedures

**System Recovery**
```bash
# Stop all running processes
pkill -f "python.*monitor.py"
pkill -f "python.*converter.py"

# Reset to last known good state
git reset --hard HEAD~1

# Restart monitoring system
python scripts/monitor.py &
```

**Data Recovery**
```bash
# Restore from backup
tar -xzf backup-latest.tar.gz

# Rebuild from source repositories
python scripts/rebuild_database.py

# Validate restored data
python scripts/validate_data.py --full
```

## 📈 Performance Optimization

### System Optimization

**Resource Management**
- Monitor GitHub API rate limits (5000 requests/hour)
- Implement efficient caching strategies
- Use parallel processing where possible
- Regular cleanup of temporary files

**Storage Optimization**
```bash
# Compress large JSON files
gzip -k website/data/applications.json

# Optimize image assets
find website/assets -name "*.png" -exec optipng {} \;

# Clean up old package files
find converted_packages/ -mtime +90 -delete
```

### Monitoring Optimization

**Efficient Repository Monitoring**
- Use conditional requests with ETags
- Implement incremental updates
- Cache repository metadata
- Batch API requests when possible

**Conversion Optimization**
```bash
# Parallel conversion processing
python converter.py --parallel --workers 4

# Skip already converted packages
python converter.py --skip-existing

# Prioritize popular applications
python converter.py --priority-list popular_apps.txt
```

## 📋 Maintenance Checklist

### Daily Tasks
- [ ] Check GitHub Actions execution status
- [ ] Review error logs for critical issues
- [ ] Monitor system resource usage
- [ ] Verify website accessibility

### Weekly Tasks
- [ ] Run full system verification
- [ ] Validate JSON data integrity
- [ ] Check conversion tool availability
- [ ] Review and clean up logs
- [ ] Test manual workflow triggers

### Monthly Tasks
- [ ] Update Python dependencies
- [ ] Optimize repository size
- [ ] Review security settings
- [ ] Analyze performance metrics
- [ ] Update documentation

### Quarterly Tasks
- [ ] Rotate GitHub tokens
- [ ] Comprehensive security audit
- [ ] Review and update monitored repositories
- [ ] Performance optimization review
- [ ] Backup verification and testing

## 📞 Support and Escalation

### Internal Support

**Log Analysis**
```bash
# Search for specific errors
grep -r "ERROR" scripts/*.log

# Monitor real-time logs
tail -f scripts/appbinhub.log

# Generate system report
python scripts/generate_report.py
```

**System Diagnostics**
```bash
# Complete system check
python verify_system.py --verbose --full-check

# Network connectivity test
python scripts/test_connectivity.py

# GitHub API status check
python scripts/check_github_status.py
```

### External Support

**GitHub Support**
- Repository issues and discussions
- GitHub Actions support documentation
- GitHub Pages troubleshooting guides

**Community Resources**
- AppImage community forums
- Linux packaging documentation
- Python automation best practices

---

## 📝 Quick Reference

### Essential Commands
```bash
# System verification
python verify_system.py

# Manual monitoring
python monitor.py

# Manual conversion
python converter.py

# Check logs
tail -f scripts/appbinhub.log

# GitHub Actions status
gh run list --limit 5
```

### Configuration Files
- `scripts/config.py`: Main system configuration
- `.github/workflows/`: GitHub Actions workflows
- `website/data/`: JSON data files
- `scripts/requirements.txt`: Python dependencies

### Important URLs
- **Website**: https://your-username.github.io/appbinhub
- **Repository**: https://github.com/your-username/appbinhub
- **Actions**: https://github.com/your-username/appbinhub/actions
- **Issues**: https://github.com/your-username/appbinhub/issues

---

**Last Updated**: June 27, 2025  
**Version**: 1.0.0  
**Administrator**: System Administrator  
**Support**: GitHub Issues and Discussions
