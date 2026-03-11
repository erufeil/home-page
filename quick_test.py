import subprocess
import time
import requests

print("Starting Flask server...")
process = subprocess.Popen(["python", "app.py"], cwd="backend", stdout=subprocess.PIPE, stderr=subprocess.PIPE)

try:
    time.sleep(3)
    
    print("Testing API...")
    response = requests.get("http://localhost:5000/api/data", timeout=5)
    data = response.json()
    
    euro = data['dolar']['euro_oficial']['venta']
    dolar = data['dolar']['dolar_oficial']['venta']
    brecha = data['dolar']['brecha']
    
    print(f"Euro: ${euro}")
    print(f"Dólar: ${dolar}")
    print(f"Brecha: {brecha}%")
    
    # Quick verification
    calculated = (euro / dolar - 1) * 100
    print(f"Calculated: {calculated:.2f}%")
    print(f"Match: {abs(brecha - calculated) < 0.01}")
    
except Exception as e:
    print(f"Error: {e}")
finally:
    process.terminate()