import subprocess
import time
import requests
import json

print("Starting Flask server...")
process = subprocess.Popen(["python", "app.py"], cwd="backend", stdout=subprocess.PIPE, stderr=subprocess.PIPE)

try:
    time.sleep(5)
    
    print("Testing favorites API...")
    
    # Test 1: Get empty favorites
    response = requests.get("http://localhost:5000/api/favorites", timeout=5)
    favorites = response.json()
    print(f"Initial favorites: {len(favorites)} items")
    
    # Test 2: Add a favorite
    test_url = "https://github.com"
    print(f"\nAdding favorite: {test_url}")
    
    add_response = requests.post("http://localhost:5000/api/favorites", 
        json={"url": test_url, "title": "GitHub"},
        timeout=10
    )
    
    if add_response.status_code == 201:
        favorite = add_response.json()
        print(f"SUCCESS: Favorite added successfully")
        print(f"  ID: {favorite['id']}")
        print(f"  Title: {favorite['title']}")
        print(f"  Domain: {favorite['domain']}")
        print(f"  Logo: {favorite['logo']}")
    else:
        print(f"ERROR: Error adding favorite: {add_response.status_code}")
        print(add_response.text)
    
    # Test 3: Get updated favorites
    response = requests.get("http://localhost:5000/api/favorites", timeout=5)
    favorites = response.json()
    print(f"\nUpdated favorites: {len(favorites)} items")
    
    # Test 4: Test logo serving
    if favorites and favorites[0].get('logo'):
        logo_url = f"http://localhost:5000/favorites/logos/{favorites[0]['logo']}"
        print(f"\nTesting logo access: {logo_url}")
        try:
            logo_response = requests.get(logo_url, timeout=5)
            print(f"SUCCESS: Logo accessible: {logo_response.status_code}")
        except Exception as e:
            print(f"ERROR: Logo error: {e}")
    
    # Test 5: Delete favorite
    if favorites:
        favorite_id = favorites[0]['id']
        print(f"\nDeleting favorite: {favorite_id}")
        delete_response = requests.delete(f"http://localhost:5000/api/favorites/{favorite_id}", timeout=5)
        
        if delete_response.status_code == 200:
            print("SUCCESS: Favorite deleted successfully")
        else:
            print(f"ERROR: Error deleting: {delete_response.status_code}")
    
    # Final check
    response = requests.get("http://localhost:5000/api/favorites", timeout=5)
    favorites = response.json()
    print(f"\nFinal favorites: {len(favorites)} items")
    
except Exception as e:
    print(f"\nError: {e}")
finally:
    process.terminate()
    process.wait()