# Contexto IA - Landing Page Dólar + Clima

## Descripción del Proyecto
Landing page que muestra cotizaciones del dólar argentino y datos climáticos en tiempo real.

## Stack Tecnológico
- **Backend:** Python 3.12 + Flask
- **Frontend:** HTML5 + CSS3 + Vanilla JavaScript (sin Node.js)
- **APIs:**
  - Dólar: Bluelytics API (gratuita, sin auth)
  - Clima: OpenWeatherMap API (requiere API key gratuita)

---

## Estructura de Archivos

```
landing-dolar/
├── context-ia.md           # Este archivo
├── backend/
│   ├── config.py           # Variables configurables
│   ├── app.py              # Flask server
│   ├── services/
│   │   ├── __init__.py
│   │   ├── dolar.py        # Scraper dólar
│   │   └── weather.py      # Scraper clima
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── app.js
└── README.md
```

---

## Variables Configurables (config.py)

| Variable | Valor Default | Descripción |
|----------|---------------|-------------|
| DOLAR_API_URL | https://api.bluelytics.com.ar/v2/latest | API de cotizaciones |
| WEATHER_API_URL | https://api.openweathermap.org/data/2.5/weather | API de clima |
| WEATHER_CITY | Córdoba | Ciudad para clima |
| WEATHER_API_KEY | (vacío) | Key de OpenWeatherMap |
| UPDATE_INTERVAL | 300 | Segundos entre updates |
| FLASK_HOST | 127.0.0.1 | Host del servidor |
| FLASK_PORT | 5000 | Puerto del servidor |

---

## Contrato de Datos JSON

### Endpoint: GET /api/data

```json
{
  "timestamp": "2026-03-10T15:30:00-03:00",
  "dolar": {
    "oficial": {
      "compra": 1390.00,
      "venta": 1441.00,
      "promedio": 1415.50
    },
    "blue": {
      "compra": 1405.00,
      "venta": 1425.00,
      "promedio": 1415.00
    },
    "brecha": 0.0,
    "ultima_actualizacion": "2026-03-10T10:00:52-03:00"
  },
  "clima": {
    "ciudad": "Córdoba",
    "temperatura": 28.5,
    "sensacion": 30.0,
    "humedad": 65,
    "descripcion": "Parcialmente nublado",
    "icono": "02d"
  }
}
```

---

## Instrucciones por Agente

### AGENTE: prometheus
**Rol:** Planificación estratégica

**Tareas:**
1. Validar la estructura de carpetas propuesta
2. Confirmar que los contratos JSON son consistentes
3. Documentar cualquier dependencia adicional

**Output esperado:** Documento de arquitectura final

---

### AGENTE: hephaestus
**Rol:** Implementación Backend

**Tareas:**
1. Crear `config.py` con todas las variables
2. Implementar `services/dolar.py`:
   - Función `get_dolar_data()`
   - Manejo de errores con try/except
   - Timeout de 10 segundos
3. Implementar `services/weather.py`:
   - Función `get_weather_data(city, api_key)`
   - Validar que `api_key` no esté vacía
   - Retornar `None` si no hay key (graceful degradation)
4. Crear `app.py` con Flask:
   - Endpoint GET `/api/data`
   - Endpoint GET `/` (sirve index.html)
   - CORS habilitado para desarrollo
5. Crear `requirements.txt`

**Consideraciones:**
- Usar `requests` para HTTP calls
- Logging básico con `print()` o `logging` module
- Variables de entorno opcionales (`os.environ.get`)

**Output esperado:** Backend funcional en `/backend`

---

### AGENTE: artistry
**Rol:** Implementación Frontend

**Tareas:**
1. Crear `index.html`:
   - Meta viewport para responsive
   - Link a `styles.css`
   - Script `app.js` (defer)
   - Estructura: header, main con cards, footer
2. Crear `styles.css`:
   - CSS Variables para colores (light/dark)
   - Cards con sombra y bordes redondeados
   - Grid responsive (mobile-first)
   - Toggle dark mode visible
   - Animaciones suaves (transition)
3. Crear `app.js`:
   - `fetch('/api/data')` cada `UPDATE_INTERVAL`
   - Actualizar DOM con datos
   - Toggle dark mode con localStorage
   - Mostrar hora de última actualización
   - Manejo de errores (mostrar mensaje si API falla)

**Consideraciones:**
- Sin frameworks JS (Vanilla puro)
- No usar async/await complejo, usar `.then()`
- Formatear números con `Intl.NumberFormat('es-AR')`
- Fechas con `toLocaleDateString('es-AR')`

**Output esperado:** Frontend funcional en `/frontend`

---

### AGENTE: oracle
**Rol:** Revisión e Integración

**Tareas:**
1. Verificar que backend corre en puerto 5000
2. Verificar que frontend hace fetch correcto
3. Validar responsive design (mobile, tablet, desktop)
4. Verificar dark mode toggle funciona
5. Validar manejo de errores
6. Sugerir mejoras si las hay

**Output esperado:** Reporte de validación

---

## Comandos de Ejecución

```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python app.py

# Frontend (abrir en navegador)
# http://127.0.0.1:5000
```

---

## Notas Adicionales

- OpenWeatherMap requiere registro gratuito: https://openweathermap.org/api
- Sin API key de clima, el widget de clima no se muestra (graceful)
- Bluelytics no requiere autenticación
- El diseño debe ser minimalista pero informativo
- Priorizar performance sobre animaciones complejas

---

## Fuentes de Datos

| Fuente | URL | Auth | Datos |
|--------|-----|------|-------|
| Bluelytics | https://api.bluelytics.com.ar/v2/latest | No | Dólar oficial, blue, euro |
| OpenWeatherMap | https://openweathermap.org/api | Sí (gratis) | Clima actual |

---

## Prioridad de Cotizaciones a Mostrar

1. **Dólar Blue** (principal)
2. **Dólar Oficial**
3. **Dólar MEP** (si está disponible)
4. **Brecha** (diferencia porcentual blue vs oficial)
