import subprocess
import time
import requests

# Start Flask server
print("Starting Flask server...")
process = subprocess.Popen(["python", "app.py"], cwd="backend", stdout=subprocess.PIPE, stderr=subprocess.PIPE)

try:
    # Wait for server to start
    time.sleep(5)
    
    # Test the server
    print("Testing server...")
    response = requests.get("http://localhost:5000/", timeout=10)
    print(f"Status: {response.status_code}")
    
    if "card-euro" in response.text:
        print("SUCCESS: Euro card found in HTML")
    else:
        print("ERROR: Euro card NOT found in HTML")
        
    # Test API
    api_response = requests.get("http://localhost:5000/api/data", timeout=10)
    print(f"API Status: {api_response.status_code}")
    data = api_response.json()
    print(f"Euro data: {data['dolar']['euro_oficial']}")
    
except Exception as e:
    print(f"Error: {e}")
finally:
    # Kill the process
    process.terminate()
    process.wait()