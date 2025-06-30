#!/usr/bin/env python3
"""
Script to list pending applications that need conversion
Used by the monitoring workflow to determine which apps need conversion
"""

import json
import sys
from pathlib import Path

def main():
    """List pending apps that need conversion"""
    try:
        # Load applications data
        apps_file = Path('../website/data/applications.json')
        if not apps_file.exists():
            print('[]')
            return
        
        with open(apps_file, 'r') as f:
            data = json.load(f)
        
        # Find apps that need conversion
        pending_apps = []
        for app in data.get('applications', []):
            if app.get('conversion_status') == 'pending':
                pending_apps.append({
                    'id': app['id'],
                    'name': app['name'],
                    'architecture': app.get('architecture', 'x86_64'),
                    'url': app['appimage']['url']
                })
        
        print(json.dumps(pending_apps))
        
    except Exception as e:
        print('[]', file=sys.stderr)
        print(f"Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    main() 