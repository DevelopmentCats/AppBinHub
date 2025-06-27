#!/usr/bin/env python3
"""
AppBinHub System Verification Script
Tests all components of the automation system
"""

import os
import sys
import json
import subprocess
from pathlib import Path
import importlib.util

def test_file_structure():
    """Test that all required files exist"""
    print("Testing file structure...")

    required_files = [
        'scripts/monitor.py',
        'scripts/converter.py', 
        'scripts/config.py',
        'scripts/requirements.txt',
        '.github/workflows/monitor-and-convert.yml',
        '.github/workflows/deploy.yml',
        'website/data/applications.json',
        'website/data/categories.json',
        'website/data/changelog.json',
        'docs/README.md',
        'docs/SETUP.md',
        'docs/API.md'
    ]

    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)

    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required files present")
        return True

def test_json_validity():
    """Test that all JSON files are valid"""
    print("Testing JSON file validity...")

    json_files = [
        'website/data/applications.json',
        'website/data/categories.json', 
        'website/data/changelog.json'
    ]

    for json_file in json_files:
        try:
            with open(json_file, 'r') as f:
                json.load(f)
            print(f"✅ {json_file} is valid JSON")
        except json.JSONDecodeError as e:
            print(f"❌ {json_file} is invalid JSON: {e}")
            return False
        except FileNotFoundError:
            print(f"❌ {json_file} not found")
            return False

    return True

def test_python_imports():
    """Test that Python scripts can be imported"""
    print("Testing Python script imports...")

    scripts_dir = Path('scripts')
    sys.path.insert(0, str(scripts_dir))

    try:
        import config
        print("✅ config.py imports successfully")

        # Test config functions
        config.ensure_directories()
        print("✅ config.ensure_directories() works")

        category = config.map_desktop_category('Development')
        print(f"✅ Category mapping works: Development -> {category}")

    except Exception as e:
        print(f"❌ Config import failed: {e}")
        return False

    try:
        import monitor
        print("✅ monitor.py imports successfully")
    except Exception as e:
        print(f"❌ Monitor import failed: {e}")
        return False

    try:
        import converter
        print("✅ converter.py imports successfully")
    except Exception as e:
        print(f"❌ Converter import failed: {e}")
        return False

    return True

def test_requirements():
    """Test that requirements.txt is valid"""
    print("Testing requirements.txt...")

    try:
        with open('scripts/requirements.txt', 'r') as f:
            requirements = f.read().strip().split('\n')

        if not requirements or requirements == ['']:
            print("❌ requirements.txt is empty")
            return False

        print(f"✅ Found {len(requirements)} requirements")
        for req in requirements:
            if req.strip():
                print(f"  - {req}")

        return True
    except FileNotFoundError:
        print("❌ requirements.txt not found")
        return False

def test_workflow_syntax():
    """Test GitHub Actions workflow syntax"""
    print("Testing GitHub Actions workflow syntax...")

    workflows = [
        '.github/workflows/monitor-and-convert.yml',
        '.github/workflows/deploy.yml'
    ]

    for workflow in workflows:
        try:
            import yaml
            with open(workflow, 'r') as f:
                yaml.safe_load(f)
            print(f"✅ {workflow} has valid YAML syntax")
        except ImportError:
            print("⚠️  PyYAML not available, skipping YAML validation")
            break
        except Exception as e:
            print(f"❌ {workflow} has invalid YAML: {e}")
            return False

    return True

def test_data_structure():
    """Test JSON data structure compliance"""
    print("Testing data structure compliance...")

    # Test applications.json structure
    try:
        with open('website/data/applications.json', 'r') as f:
            apps_data = json.load(f)

        required_keys = ['metadata', 'applications']
        for key in required_keys:
            if key not in apps_data:
                print(f"❌ applications.json missing key: {key}")
                return False

        metadata_keys = ['last_updated', 'total_applications', 'version']
        for key in metadata_keys:
            if key not in apps_data['metadata']:
                print(f"❌ applications.json metadata missing key: {key}")
                return False

        print("✅ applications.json structure is valid")

    except Exception as e:
        print(f"❌ applications.json structure test failed: {e}")
        return False

    # Test categories.json structure
    try:
        with open('website/data/categories.json', 'r') as f:
            cats_data = json.load(f)

        if 'categories' not in cats_data:
            print("❌ categories.json missing 'categories' key")
            return False

        if not isinstance(cats_data['categories'], list):
            print("❌ categories.json 'categories' is not a list")
            return False

        print("✅ categories.json structure is valid")

    except Exception as e:
        print(f"❌ categories.json structure test failed: {e}")
        return False

    return True

def test_directory_structure():
    """Test that required directories exist"""
    print("Testing directory structure...")

    required_dirs = [
        'scripts',
        '.github/workflows',
        'website/data',
        'docs'
    ]

    for directory in required_dirs:
        if not Path(directory).is_dir():
            print(f"❌ Missing directory: {directory}")
            return False

    print("✅ All required directories present")
    return True

def main():
    """Run all verification tests"""
    print("AppBinHub System Verification")
    print("=" * 40)

    tests = [
        test_directory_structure,
        test_file_structure,
        test_json_validity,
        test_data_structure,
        test_requirements,
        test_python_imports,
        test_workflow_syntax
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        print()
        try:
            if test():
                passed += 1
            else:
                print("Test failed!")
        except Exception as e:
            print(f"Test error: {e}")

    print()
    print("=" * 40)
    print(f"Verification Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! System is ready for deployment.")
        return 0
    else:
        print("❌ Some tests failed. Please fix issues before deployment.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
