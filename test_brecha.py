from backend.services.dolar import get_dolar_data

data = get_dolar_data()
if data:
    euro_venta = data['euro_oficial']['venta']
    dolar_venta = data['dolar_oficial']['venta']
    brecha = data['brecha']
    
    print(f"Euro Oficial (venta): ${euro_venta}")
    print(f"Dólar Oficial (venta): ${dolar_venta}")
    print(f"Brecha calculada: {brecha}%")
    
    # Verificar cálculo
    euros_per_dolar = euro_venta / dolar_venta
    brecha_calculada = (euros_per_dolar - 1) * 100
    print(f"Cálculo manual: {brecha_calculada:.2f}%")
    print(f"¿Coinciden? {abs(brecha - brecha_calculada) < 0.01}")
else:
    print("No se pudieron obtener datos")