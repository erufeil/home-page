import requests
import json

try:
    response = requests.get("http://localhost:5000/api/data", timeout=10)
    data = response.json()
    
    euro = data['dolar']['euro_oficial']
    dolar = data['dolar']['dolar_oficial']
    brecha = data['dolar']['brecha']
    
    print("=== DATOS DE LA API ===")
    print(f"Euro Oficial:")
    print(f"  Compra: ${euro['compra']}")
    print(f"  Venta: ${euro['venta']}")
    print(f"  Promedio: ${euro['promedio']}")
    
    print(f"\nDólar Oficial:")
    print(f"  Compra: ${dolar['compra']}")
    print(f"  Venta: ${dolar['venta']}")
    print(f"  Promedio: ${dolar['promedio']}")
    
    print(f"\nBrecha Euro vs Dólar: {brecha}%")
    
    # Verificar cálculo
    euros_per_dolar = euro['venta'] / dolar['venta']
    brecha_calculada = (euros_per_dolar - 1) * 100
    
    print(f"\n=== VERIFICACIÓN ===")
    print(f"1 Euro = {euros_per_dolar:.4f} Dólares")
    print(f"Brecha calculada: {brecha_calculada:.2f}%")
    print(f"Brecha API: {brecha}%")
    print(f"¿Coinciden? {abs(brecha - brecha_calculada) < 0.01}")
    
except Exception as e:
    print(f"Error: {e}")