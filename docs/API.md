# AppBinHub API Documentation

Technical documentation for the AppBinHub automation system, JSON data structures, and script interfaces.

## Table of Contents
1. [Data Structure Overview](#data-structure-overview)
2. [JSON Schema Specifications](#json-schema-specifications)
3. [Monitoring Script API](#monitoring-script-api)
4. [Conversion Script API](#conversion-script-api)
5. [GitHub Actions Integration](#github-actions-integration)
6. [Configuration API](#configuration-api)
7. [Error Handling](#error-handling)

## Data Structure Overview

AppBinHub uses a JSON-based data structure to store application metadata, categories, and changelog information. All data files are stored in the `website/data/` directory.

### File Structure
```
website/data/
├── applications.json    # Main application database
├── categories.json      # Application categories
└── changelog.json       # Update history
```

## JSON Schema Specifications

### Applications Database (`applications.json`)

#### Root Structure
```json
{
  "metadata": {
    "last_updated": "ISO 8601 timestamp",
    "total_applications": "integer",
    "version": "string (semantic version)"
  },
  "applications": [
    // Array of application objects
  ]
}
```

#### Application Object Schema
```json
{
  "id": "string (unique identifier)",
  "name": "string (application name)",
  "description": "string (application description)",
  "version": "string (application version)",
  "category": ["array of category strings"],
  "appimage": {
    "url": "string (download URL)",
    "size": "string (human readable size)",
    "checksum": "string (sha256:hash)"
  },
  "converted_packages": {
    "deb": {
      "url": "string (relative path or URL)",
      "size": "string (human readable size)",
      "checksum": "string (sha256:hash)",
      "status": "string (available|pending|failed|tool_unavailable)",
      "created": "ISO 8601 timestamp (optional)"
    },
    "rpm": {
      "url": "string (relative path or URL)",
      "size": "string (human readable size)", 
      "checksum": "string (sha256:hash)",
      "status": "string (available|pending|failed|tool_unavailable)",
      "created": "ISO 8601 timestamp (optional)"
    }
  },
  "metadata": {
    "icon": "string (path to icon file)",
    "desktop_file": "string (desktop file content)",
    "executable": "string (executable name)",
    "mime_types": ["array of MIME type strings"]
  },
  "source": {
    "repository": "string (GitHub repository URL)",
    "release_tag": "string (Git tag)",
    "release_date": "ISO 8601 timestamp"
  },
  "last_updated": "ISO 8601 timestamp",
  "conversion_status": "string (pending|completed|failed)"
}
```

#### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique identifier generated from repo and app name |
| `name` | string | Yes | Application name from .desktop file |
| `description` | string | No | Application description from .desktop file |
| `version` | string | Yes | Version from GitHub release tag |
| `category` | array | No | Categories from .desktop file Categories field |
| `appimage.url` | string | Yes | Direct download URL for AppImage |
| `appimage.size` | string | Yes | Human-readable file size (e.g., "25.6 MB") |
| `appimage.checksum` | string | Yes | SHA256 checksum with "sha256:" prefix |
| `conversion_status` | string | Yes | Overall conversion status |

### Categories Database (`categories.json`)

#### Schema
```json
{
  "categories": [
    {
      "id": "string (category identifier)",
      "name": "string (display name)",
      "description": "string (category description)",
      "count": "integer (number of applications)",
      "icon": "string (icon identifier)"
    }
  ]
}
```

#### Standard Categories
Based on FreeDesktop.org Desktop Entry Specification:

| ID | Name | Description | Icon |
|----|------|-------------|------|
| `audio` | Audio | Audio players, editors, and multimedia | `volume-up` |
| `education` | Education | Educational software and learning tools | `graduation-cap` |
| `games` | Games | Gaming applications and entertainment | `gamepad` |
| `graphics` | Graphics | Image editors, viewers, and graphics tools | `image` |
| `internet` | Internet | Web browsers, email clients, network tools | `globe` |
| `office` | Office | Office suites, text editors, productivity | `file-text` |
| `programming` | Programming | Development tools, IDEs, coding utilities | `code` |
| `utilities` | Utilities | System tools and utility applications | `tool` |
| `video` | Video | Video players, editors, multimedia tools | `video` |
| `other` | Other | Miscellaneous applications | `package` |

### Changelog Database (`changelog.json`)

#### Schema
```json
{
  "updates": [
    {
      "date": "ISO 8601 timestamp",
      "applications_added": ["array of application IDs"],
      "applications_updated": ["array of application IDs"],
      "total_count": "integer (total applications)",
      "summary": "string (human readable summary)"
    }
  ]
}
```

## Monitoring Script API

### Class: `AppImageMonitor`

#### Constructor
```python
monitor = AppImageMonitor()
```

**Environment Requirements:**
- `GITHUB_TOKEN` environment variable must be set

#### Methods

##### `monitor_repositories()`
Main monitoring function that processes all configured repositories.

**Returns:** None  
**Side Effects:** Updates JSON data files

##### `get_repository_releases(repo_name)`
Fetches releases from a GitHub repository.

**Parameters:**
- `repo_name` (str): Repository name in format "owner/repo"

**Returns:** List of GitHub Release objects

##### `extract_appimage_metadata(appimage_path)`
Extracts metadata from an AppImage file.

**Parameters:**
- `appimage_path` (Path): Path to AppImage file

**Returns:** Dictionary with metadata or None if extraction fails

**Metadata Structure:**
```python
{
    'name': str,
    'description': str,
    'executable': str,
    'icon': str,
    'categories': list,
    'mime_types': list,
    'icon_path': str  # Optional
}
```

##### `parse_desktop_file(desktop_file, squashfs_root)`
Parses .desktop file content.

**Parameters:**
- `desktop_file` (Path): Path to .desktop file
- `squashfs_root` (Path): Path to extracted AppImage root

**Returns:** Dictionary with parsed metadata

##### `update_application_data(new_records)`
Updates the applications.json file with new records.

**Parameters:**
- `new_records` (list): List of application record dictionaries

**Side Effects:** Writes to applications.json file

## Conversion Script API

### Class: `AppImageConverter`

#### Constructor
```python
converter = AppImageConverter()
```

#### Methods

##### `convert_pending_applications()`
Converts all applications with "pending" conversion status.

**Returns:** None  
**Side Effects:** Updates JSON files and creates package files

##### `convert_appimage_to_deb(appimage_path, output_dir)`
Converts AppImage to Debian package using appimage2deb.

**Parameters:**
- `appimage_path` (Path): Path to AppImage file
- `output_dir` (Path): Output directory for .deb file

**Returns:** Path to created .deb file or None

**Requirements:** `appimage2deb` tool must be installed

##### `convert_deb_to_rpm(deb_path, output_dir)`
Converts .deb package to .rpm using alien.

**Parameters:**
- `deb_path` (Path): Path to .deb file
- `output_dir` (Path): Output directory for .rpm file

**Returns:** Path to created .rpm file or None

**Requirements:** `alien` tool must be installed

##### `validate_deb_package(deb_path)`
Validates .deb package integrity.

**Parameters:**
- `deb_path` (Path): Path to .deb file

**Returns:** Boolean indicating validation success

##### `store_converted_package(package_path, app_id, package_type)`
Stores converted package and returns metadata.

**Parameters:**
- `package_path` (Path): Path to package file
- `app_id` (str): Application identifier
- `package_type` (str): Package type ("deb" or "rpm")

**Returns:** Dictionary with package metadata

## GitHub Actions Integration

### Workflow Triggers

#### Monitor and Convert Workflow
- **Schedule:** Every 4 hours (`0 */4 * * *`)
- **Manual:** `workflow_dispatch` event
- **Code Changes:** Push to `scripts/**` or workflow files

#### Deploy Workflow
- **Website Changes:** Push to `website/**`
- **Manual:** `workflow_dispatch` event

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GITHUB_TOKEN` | Yes | GitHub Personal Access Token |

### Workflow Outputs

#### Artifacts
- `conversion-logs`: Log files from monitoring and conversion
- Retention: 7 days

#### Step Summary
- Tool installation status
- Execution timestamps
- Log excerpts
- Error summaries

## Configuration API

### Module: `config.py`

#### Constants

##### Repository Configuration
```python
APPIMAGE_REPOSITORIES = [
    "AppImage/AppImageKit",
    "AppImageCommunity/pkg2appimage",
    # Additional repositories
]
```

##### Tool Configuration
```python
CONVERSION_TOOLS = {
    "appimage2deb": {
        "command": "appimage2deb",
        "timeout": 300,
        "enabled": True
    }
}
```

#### Functions

##### `get_github_token()`
Retrieves GitHub token from environment.

**Returns:** String token  
**Raises:** ValueError if token not found

##### `ensure_directories()`
Creates required directories if they don't exist.

**Side Effects:** Creates directories in filesystem

##### `map_desktop_category(desktop_category)`
Maps .desktop file category to AppBinHub category.

**Parameters:**
- `desktop_category` (str): Category from .desktop file

**Returns:** String category ID

##### `is_valid_appimage_url(url)`
Validates if URL appears to be an AppImage download.

**Parameters:**
- `url` (str): URL to validate

**Returns:** Boolean

## Error Handling

### Exception Types

#### Configuration Errors
```python
ValueError: "GITHUB_TOKEN environment variable is required"
```

#### GitHub API Errors
```python
github.GithubException: Rate limit exceeded
github.UnknownObjectException: Repository not found
```

#### Conversion Errors
```python
subprocess.TimeoutExpired: Tool execution timeout
FileNotFoundError: Conversion tool not found
```

### Error Logging

All errors are logged with the following format:
```
YYYY-MM-DD HH:MM:SS - LEVEL - MESSAGE
```

#### Log Levels
- **DEBUG**: Detailed execution information
- **INFO**: Normal operation messages
- **WARNING**: Non-critical issues
- **ERROR**: Critical failures
- **CRITICAL**: System-level failures

### Error Recovery

#### Automatic Retry
- Network operations: 3 retries with 5-second delay
- Tool execution: Single retry on timeout
- File operations: No automatic retry

#### Graceful Degradation
- Missing tools: Mark packages as "tool_unavailable"
- Network failures: Continue with available data
- Parsing errors: Skip problematic entries

## Rate Limiting

### GitHub API
- **Authenticated**: 5,000 requests per hour
- **Threshold**: Stop when < 100 requests remaining
- **Reset**: Wait for rate limit reset time

### Implementation
```python
def check_rate_limits(self):
    rate_limit = self.github.get_rate_limit()
    remaining = rate_limit.core.remaining
    if remaining < 100:
        return False
    return True
```

## Data Validation

### JSON Schema Validation
All JSON files are validated before writing:
```python
import json

def validate_json(data, schema):
    try:
        json.dumps(data)  # Validate JSON serializable
        # Additional schema validation here
        return True
    except (TypeError, ValueError):
        return False
```

### File Size Limits
- **JSON files**: 1MB maximum
- **Total repository**: 900MB maximum
- **Single package**: 100MB maximum

### Checksum Verification
All downloaded files are verified using SHA256 checksums:
```python
def calculate_file_checksum(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()
```

## Performance Considerations

### Optimization Strategies
- **Parallel Processing**: Multiple AppImage downloads
- **Caching**: Avoid re-downloading unchanged files
- **Incremental Updates**: Only process new/changed applications
- **Cleanup**: Remove temporary files after processing

### Memory Management
- **Streaming Downloads**: Process large files in chunks
- **Temporary Directories**: Automatic cleanup with context managers
- **Log Rotation**: Prevent log files from growing too large

---

This API documentation provides comprehensive technical details for integrating with and extending the AppBinHub automation system.