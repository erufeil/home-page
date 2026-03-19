#!/usr/bin/env python3
"""
Download default logos for popular websites.
Logos are stored in /app/favorites/logos/ (or ./favorites/logos/ for local).
"""
import os
import sys
import requests
import time
from urllib.parse import urlparse

# Default sites with their domains and preferred logo URLs
DEFAULT_SITES = [
    {
        'name': 'Google',
        'domain': 'google.com',
        'url': 'https://www.google.com',
        'favicon_url': 'https://www.google.com/favicon.ico'
    },
    {
        'name': 'GitHub',
        'domain': 'github.com',
        'url': 'https://github.com',
        'favicon_url': 'https://github.com/favicon.ico'
    },
    {
        'name': 'YouTube',
        'domain': 'youtube.com',
        'url': 'https://www.youtube.com',
        'favicon_url': 'https://www.youtube.com/favicon.ico'
    },
    {
        'name': 'Twitter',
        'domain': 'twitter.com',
        'url': 'https://twitter.com',
        'favicon_url': 'https://twitter.com/favicon.ico'
    },
    {
        'name': 'Facebook',
        'domain': 'facebook.com',
        'url': 'https://www.facebook.com',
        'favicon_url': 'https://www.facebook.com/favicon.ico'
    },
    {
        'name': 'Gmail',
        'domain': 'gmail.com',
        'url': 'https://mail.google.com',
        'favicon_url': 'https://mail.google.com/favicon.ico'
    },
    {
        'name': 'Outlook',
        'domain': 'outlook.com',
        'url': 'https://outlook.live.com',
        'favicon_url': 'https://outlook.live.com/favicon.ico'
    }
]

def ensure_logos_directory(logos_dir):
    """Ensure logos directory exists."""
    os.makedirs(logos_dir, exist_ok=True)
    print(f"Logos directory: {logos_dir}")

def download_logo(favicon_url, domain, logos_dir, timeout=10):
    """
    Download favicon from given URL.
    
    Returns:
        filename if successful, None otherwise
    """
    try:
        response = requests.get(favicon_url, timeout=timeout, stream=True)
        response.raise_for_status()
        
        # Determine file extension
        content_type = response.headers.get('Content-Type', '')
        if 'image/' in content_type:
            ext = content_type.split('/')[-1].split(';')[0]
            if ext not in ['ico', 'png', 'jpg', 'jpeg', 'gif', 'svg']:
                ext = 'ico'
        else:
            ext = 'ico'
        
        filename = f"{domain}.{ext}"
        filepath = os.path.join(logos_dir, filename)
        
        # Save file
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"  ✓ Downloaded: {filename} ({response.headers.get('Content-Length', '?')} bytes)")
        return filename
        
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Failed to download {favicon_url}: {e}")
        return None
    except Exception as e:
        print(f"  ✗ Error saving logo for {domain}: {e}")
        return None

def main():
    """Main download function."""
    # Determine logos directory
    if len(sys.argv) > 1:
        logos_dir = sys.argv[1]
    else:
        # Default: project favorites/logos directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        logos_dir = os.path.join(script_dir, '..', 'favorites', 'logos')
    
    ensure_logos_directory(logos_dir)
    
    print(f"Downloading default logos to {logos_dir}")
    print(f"Total sites: {len(DEFAULT_SITES)}")
    print("-" * 50)
    
    success_count = 0
    for site in DEFAULT_SITES:
        domain = site['domain']
        favicon_url = site['favicon_url']
        
        print(f"\n{site['name']} ({domain}):")
        
        # Check if logo already exists
        existing_files = [f for f in os.listdir(logos_dir) if f.startswith(domain + '.')]
        if existing_files:
            print(f"  Logo already exists: {existing_files[0]}")
            success_count += 1
            continue
        
        # Download logo
        filename = download_logo(favicon_url, domain, logos_dir)
        if filename:
            success_count += 1
        
        # Be nice to servers
        time.sleep(0.5)
    
    print("\n" + "=" * 50)
    print(f"Download complete: {success_count}/{len(DEFAULT_SITES)} successful")
    
    if success_count < len(DEFAULT_SITES):
        print("Note: Some logos failed to download. The application will use fallback icons.")
    
    return 0 if success_count > 0 else 1

if __name__ == '__main__':
    sys.exit(main())