# Context Code - Arquitectura y Algoritmos

Este archivo documenta la arquitectura del sistema, algoritmos clave, estructuras de código y patrones de diseño implementados en el proyecto.

---

## 1. Arquitectura del Sistema

### 1.1. Arquitectura General

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Cliente (Browser)                          │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    Single Page Application                    │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │  │
│  │  │    UI/UX    │  │   Estado    │  │      Lógica         │  │  │
│  │  │  (HTML/CSS) │  │ (Variables) │  │   (JavaScript)      │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘  │  │
│  └───────────────────────────┬──────────────────────────────────┘  │
│                              │ HTTP/JSON (REST API)                 │
└──────────────────────────────┼──────────────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Servidor (Flask)                           │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    Capa de Presentación                      │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │  │
│  │  │  Endpoints  │  │   Routing   │  │   Static Serving    │  │  │
│  │  │   RESTful   │  │   (Flask)   │  │  (HTML/CSS/JS)      │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘  │  │
│  └───────────────────────────┬──────────────────────────────────┘  │
│                              │ Llamadas a Servicios                 │
└──────────────────────────────┼──────────────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       Capa de Servicios                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Dólar     │  │   Clima     │  │    Favoritos        │  │
│  │  Service    │  │  Service    │  │    Service          │  │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘  │
│         │                │                     │             │
│    Bluelytics API   OpenWeatherMap      │  JSON File Storage│
│                                         │  + Web Scraping   │
└─────────────────────────────────────────┴───────────────────┘
```

### 1.2. Patrones de Diseño Implementados

#### 1.2.1. Service Layer Pattern
- **Ubicación:** `backend/services/`
- **Propósito:** Separar la lógica de negocio de los endpoints HTTP
- **Implementación:** Cada servicio es un módulo Python independiente
- **Ventajas:**
  - Reutilización de código
  - Testabilidad individual
  - Separación de responsabilidades

#### 1.2.2. Repository Pattern (simplificado)
- **Ubicación:** `services/favorites.py`
- **Propósito:** Abstraer el acceso a datos (JSON file)
- **Implementación:** Funciones `get_favorites()`, `save_favorites()`
- **Ventajas:**
  - Cambio transparente de almacenamiento
  - Centralización de operaciones CRUD

#### 1.2.3. Strategy Pattern (scraping de logos)
- **Ubicación:** `find_logo_url()` en `favorites.py`
- **Propósito:** Múltiples estrategias para encontrar logos
- **Implementación:** Lista de patrones regex evaluados en orden
- **Ventajas:**
  - Flexibilidad para agregar nuevas estrategias
  - Fallback graceful

#### 1.2.4. Observer Pattern (auto-refresh)
- **Ubicación:** `startAutoRefresh()` en `app.js`
- **Propósito:** Actualización automática periódica
- **Implementación:** `setInterval()` que llama a `loadData()`
- **Ventajas:**
  - Desacoplamiento entre temporizador y lógica
  - Fácil de detener/reiniciar

### 1.3. Flujo de Datos

#### 1.3.1. Flujo de Agregar Favorito
```
Usuario ingresa URL → Frontend valida → POST /api/favorites → 
Backend valida → add_favorite() → Scraping HTML → Buscar logo →
Descargar logo → Crear objeto → Guardar JSON → Respuesta 201 →
Frontend recarga lista → Renderizado separado por tipo
```

#### 1.3.2. Flujo de Actualización de Datos
```
Timer (5 min) → loadData() → GET /api/data → 
get_dolar_data() → API Bluelytics → get_weather_data() → 
API OpenWeatherMap → Combinar datos → Respuesta JSON → 
updateUI() → Actualizar DOM
```

#### 1.3.3. Flujo de Renderizado de Favoritos
```
loadFavorites() → GET /api/favorites → Separar por tipo →
renderFavorites() → Crear secciones → createFavoriteCard() →
Agregar event listeners → Insertar en DOM
```

---

## 2. Algoritmos Clave

### 2.1. Algoritmo de Scraping de Logos

#### 2.1.1. Función: `find_logo_url(html_content, base_url)`
**Complejidad:** O(n) donde n es el número de patrones (7)

**Pasos:**
1. **Lista de patrones regex** (ordenados por prioridad):
   ```python
   logo_patterns = [
       # Favicon (más específico)
       r'<link[^>]*?rel=["\'](?:icon|shortcut\s+icon|apple-touch-icon)["\'][^>]*?href=["\']([^"\']+?)["\']',
       # Open Graph image
       r'<meta[^>]*?property=["\']og:image["\'][^>]*?content=["\']([^"\']+?)["\']',
       # Twitter image
       r'<meta[^>]*?name=["\']twitter:image["\'][^>]*?content=["\']([^"\']+?)["\']',
       # Logo en clase CSS
       r'<img[^>]*?class=["\'][^"\']*logo[^"\']*["\'][^>]*?src=["\']([^"\']+?)["\']',
       # Logo en alt text
       r'<img[^>]*?alt=["\'][^"\']*logo[^"\']*["\'][^>]*?src=["\']([^"\']+?)["\']',
       # Imágenes que contengan "logo" o "brand"
       r'<img[^>]*?src=["\']([^"\']*?(?:logo|brand)[^"\']*?)["\'][^>]*?>',
       # Schema.org logo
       r'<meta[^>]*?itemprop=["\']image["\'][^>]*?content=["\']([^"\']+?)["\']',
   ]
   ```

2. **Evaluación secuencial:** Se prueba cada patrón en orden
3. **Transformación de URL relativa a absoluta:**
   ```python
   if logo_url.startswith('//'):
       logo_url = f"https:{logo_url}"
   elif logo_url.startswith('/'):
       parsed = urlparse(base_url)
       logo_url = f"{parsed.scheme}://{parsed.netloc}{logo_url}"
   elif not logo_url.startswith(('http://', 'https://')):
       logo_url = f"{base_url}/{logo_url}"
   ```

4. **Validación de extensión:** Añade extensión si falta
   ```python
   if not re.search(r'\.(png|jpg|jpeg|gif|ico|svg|webp)$', logo_url, re.IGNORECASE):
       if '/favicon' in logo_url.lower():
           logo_url += '.ico'
       elif '/logo' in logo_url.lower():
           logo_url += '.png'
   ```

5. **Fallback:** Retorna `favicon.ico` si no encuentra ningún logo

#### 2.1.2. Algoritmo de Limpieza de Dominio

**Función:** `clean_domain(domain)`
**Propósito:** Extraer dominio principal removiendo subdominios comunes

**Pasos:**
1. **Convertir a minúsculas** y remover `www.` inicial
2. **Lista de TLDs conocidos** (top-level domains):
   ```python
   tlds = ['.com', '.org', '.net', '.edu', '.gov', '.mil', '.int', 
           '.ar', '.com.ar', '.org.ar', '.net.ar', '.gob.ar',
           '.uk', '.co.uk', '.org.uk', 
           '.au', '.com.au',
           '.br', '.com.br',
           '.mx', '.com.mx',
           '.es', '.com.es',
           '.fr', '.com.fr',
           '.de', '.com.de',
           '.it', '.com.it']
   ```

3. **Búsqueda del TLD más largo:**
   ```python
   parts = domain.split('.')
   for i in range(len(parts) - 1):
       test_tld = '.' + '.'.join(parts[i+1:])
       if test_tld in tlds:
           main_domain_part = parts[i]
           return main_domain_part + '.' + '.'.join(parts[i+1:])
   ```

4. **Fallback:** Si no encuentra TLD conocido, usar penúltima parte como dominio principal

**Ejemplos:**
- `www.example.com` → `example.com`
- `listado.mercadolibre.com.ar` → `mercadolibre.com.ar`
- `m.example.co.uk` → `example.co.uk`

#### 2.1.3. Algoritmo de Generación de Nombre de Archivo

**Función:** `generate_filename(url, logo_url)`
**Propósito:** Generar nombre de archivo único y seguro para logos

**Pasos:**
1. Extraer dominio de la URL
2. Obtener timestamp actual: `YYYYMMDD_HHMMSS`
3. Sanear dominio (reemplazar caracteres no alfanuméricos con `_`)
4. Determinar extensión del logo URL (o usar `.png` como default)
5. Combinar: `{safe_domain}_{timestamp}{extension}`

**Ejemplo:** `www.deepseek.com_20260311_130958.ico`

### 2.2. Algoritmo de Cálculo de Brecha

**Función:** Cálculo en `services/dolar.py`
**Fórmula:** 
```
brecha = ((euro_oficial.venta / dolar_oficial.venta) - 1) * 100
```

**Explicación:**
1. **Conversión euro a dólares:** `euros_per_dolar = euro_oficial.venta / dolar_oficial.venta`
2. **Interpretación:** Cuántos dólares se necesitan para comprar 1 euro
3. **Porcentaje de diferencia:** `(euros_per_dolar - 1) * 100`
4. **Ejemplo:** Si 1 euro = 1.10 dólares, brecha = 10%

**Validación:** Solo calcular si `dolar_oficial.venta > 0`

### 2.3. Algoritmo de Renderizado por Tipo

**Función:** `renderFavorites(favorites)` en `app.js`

**Pasos:**
1. **Separación:** Filtrar array por propiedad `tipo`
   ```javascript
   const tareasPendientes = favorites.filter(f => f.tipo === 'tarea_pendiente');
   const favoritos = favorites.filter(f => f.tipo === 'favorito');
   ```

2. **Creación condicional de secciones:**
   - Solo crear sección de "Tareas Pendientes" si `tareasPendientes.length > 0`
   - Solo crear divisor si ambas secciones tienen items
   - Solo crear sección de "Favoritos" si `favoritos.length > 0`

3. **Estructura DOM generada:**
   ```html
   <!-- Si hay tareas pendientes -->
   <div class="favorites-section">
     <h3 class="favorites-section-header">Tareas Pendientes (2)</h3>
     <div class="favorites-grid">
       <!-- Cards de tareas pendientes -->
     </div>
   </div>
   
   <!-- Si hay ambas secciones -->
   <hr class="section-divider">
   
   <!-- Si hay favoritos -->
   <div class="favorites-section">
     <h3 class="favorites-section-header">Favoritos (5)</h3>
     <div class="favorites-grid">
       <!-- Cards de favoritos -->
     </div>
   </div>
   ```

### 2.4. Algoritmo de Migración Backward Compatible

**Función:** `get_favorites()` en `favorites.py`

**Problema:** Favoritos existentes no tienen campo `tipo`
**Solución:** Migración automática al cargar

**Pasos:**
1. Cargar favorites desde JSON
2. Iterar sobre cada favorite
3. Si falta campo `tipo`, agregar con valor `'favorito'`
4. Si se modificó algún favorite, guardar automáticamente
5. Loggear la migración para trazabilidad

**Código:**
```python
modified = False
for favorite in favorites:
    if 'tipo' not in favorite:
        favorite['tipo'] = 'favorito'
        modified = True

if modified:
    save_favorites(favorites)
    logger.info("Migración: campo 'tipo' agregado a favoritos existentes")
```

---

## 3. Estructuras de Código

### 3.1. Estructura del Backend (Python)

#### 3.1.1. Módulo: `services/favorites.py`
```python
# Nivel 1: Funciones de utilidad (bajo nivel)
- ensure_directories()
- extract_domain(url)
- clean_domain(domain)
- clean_domain_name(domain)
- generate_filename(url, logo_url)

# Nivel 2: Funciones de scraping (nivel medio)
- find_logo_url(html_content, base_url)
- download_logo(logo_url, filename)

# Nivel 3: Funciones de negocio (alto nivel)
- get_favorites()
- save_favorites(favorites)
- add_favorite(url, title, tipo)
- delete_favorite(favorite_id)
```

#### 3.1.2. Patrón de Manejo de Errores
```python
try:
    # Operación principal
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    # Procesamiento
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 403:
        # Manejo específico de 403
        logger.warning(f"Acceso denegado (403) para {url}")
        # Fallback: crear favorito sin logo
    else:
        logger.error(f"Error HTTP {e.response.status_code}: {e}")
        raise
except requests.exceptions.Timeout:
    logger.error("Timeout en la solicitud")
    return None
except Exception as e:
    logger.error(f"Error inesperado: {e}")
    raise
```

### 3.2. Estructura del Frontend (JavaScript)

#### 3.2.1. Organización del Módulo `app.js`
```javascript
// Sección 1: Configuración y constantes (líneas 1-28)
// - Constantes globales
// - Formateadores
// - Elementos DOM

// Sección 2: Funciones de inicialización (líneas 70-91)
// - init()
// - applyTheme()
// - setupEventListeners()

// Sección 3: Funciones de datos (líneas 119-265)
// - loadData()
// - updateUI()
// - startAutoRefresh()

// Sección 4: Funciones de clima (líneas 204-237)
// - updateWeatherIcon()

// Sección 5: Funciones de favoritos (líneas 268-471)
// - addFavorite()
// - loadFavorites()
// - renderFavorites()
// - createFavoriteCard()
// - deleteFavorite()

// Sección 6: Utilidades (líneas 240-252, 474-487)
// - Manejo de errores
// - Finalización de init
```

#### 3.2.2. Patrón de Manejo de Promesas
```javascript
// Estructura típica con .then() y .catch()
fetch('/api/favorites')
    .then(response => {
        if (!response.ok) {
            throw new Error('Error del servidor');
        }
        return response.json();
    })
    .then(favorites => {
        // Procesamiento exitoso
        updateFavoritesCount(favorites.length);
        renderFavorites(favorites);
    })
    .catch(error => {
        // Manejo de error
        console.error('Error:', error);
        showFavoriteStatus('Error al cargar favoritos', 'error');
    })
    .finally(() => {
        // Limpieza (si es necesario)
        elements.addFavoriteBtn.disabled = false;
    });
```

### 3.3. Estructura de CSS

#### 3.3.1. Sistema de Diseño
```css
/* 1. Variables CSS (Design Tokens) */
:root {
    /* Colores */
    --primary-color: #2563eb;
    /* Espaciado */
    --spacing-xs: 0.5rem;
    /* Tipografía implícita (heredada) */
}

/* 2. Reset y estilos base */
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Inter'; }

/* 3. Componentes reutilizables */
.card { /* Estilos base de card */ }
.btn { /* Estilos base de botón */ }

/* 4. Componentes específicos */
.favorite-card { /* Card de favorito */ }
.weather-icon { /* Icono de clima */ }

/* 5. Layout y grids */
.layout-container { /* Grid principal */ }
.favorites-grid { /* Grid de favoritos */ }

/* 6. Utilidades y estados */
.loading { opacity: 0.7; }
.error-message { display: none; }
.error-message.show { display: block; }

/* 7. Responsive design */
@media (max-width: 768px) { /* Ajustes móviles */ }
```

#### 3.3.2. Patrón BEM (simplificado)
- **Block:** `.favorite-card` (componente independiente)
- **Element:** `.favorite-card__title` (pero usamos `.favorite-title`)
- **Modifier:** `.favorite-status--success` (pero usamos `.favorite-status.success`)

---

## 4. Patrones de Comunicación

### 4.1. Comunicación Frontend-Backend

#### 4.1.1. Headers Estándar
```javascript
// Frontend (al enviar datos)
headers: {
    'Content-Type': 'application/json'
}

// Backend (al servir logos)
return send_from_directory('../favorites/logos', filename)
```

#### 4.1.2. Formatos de Respuesta
- **Éxito (200/201):** Datos en formato JSON
- **Error cliente (400/404):** `{"error": "mensaje descriptivo"}`
- **Error servidor (500):** `{"error": "mensaje genérico"}` (sin detalles internos)

### 4.2. Comunicación con APIs Externas

#### 4.2.1. Bluelytics API
```python
# Sin autenticación
response = requests.get(DOLAR_API_URL, timeout=10)

# Estructura esperada (simplificada):
{
    "oficial_euro": {"value_buy": 1390, "value_sell": 1441},
    "oficial": {"value_buy": 1390, "value_sell": 1441},
    "blue": {"value_buy": 1405, "value_sell": 1425},
    "last_update": "2026-03-11T10:00:52-03:00"
}
```

#### 4.2.2. OpenWeatherMap API
```python
# Con API key y parámetros
params = {
    "q": city,
    "appid": api_key,
    "units": "metric",  # Celsius
    "lang": "es"       # Español
}

# Estructura esperada:
{
    "main": {"temp": 28.5, "feels_like": 30.0, "humidity": 65},
    "weather": [{"description": "parcialmente nublado", "icon": "02d"}]
}
```

---

## 5. Optimizaciones y Performance

### 5.1. Optimizaciones Implementadas

#### 5.1.1. Cache de Logos
- **Problema:** Redescargar logos en cada visita
- **Solución:** Guardar localmente en `favorites/logos/`
- **Ventaja:** Reduce requests HTTP y mejora load time

#### 5.1.2. Lazy Loading de Imágenes
- **Implementación:** `img.onerror` handler para fallback
```javascript
logo.onerror = function() {
    this.style.display = 'none';
    // Mostrar placeholder
};
```

#### 5.1.3. Debouncing en Auto-Refresh
- **Problema:** Múltiples refrescos superpuestos
- **Solución:** `clearInterval()` antes de `setInterval()`
```javascript
if (refreshTimer) {
    clearInterval(refreshTimer);
}
refreshTimer = setInterval(() => {
    loadData();
}, updateInterval);
```

### 5.2. Consideraciones de Performance

#### 5.2.1. Complejidad Algorítmica
| Operación | Complejidad | Notas |
|-----------|-------------|-------|
| `renderFavorites()` | O(n) | n = número de favoritos |
| `find_logo_url()` | O(m) | m = número de patrones (7) |
| `clean_domain()` | O(k) | k = número de TLDs (aprox 30) |
| Búsqueda en `favorites.json` | O(n) | Archivo pequeño (< 100 items) |

#### 5.2.2. Optimizaciones de Memoria
- **Frontend:** Limpieza de event listeners al re-renderizar
- **Backend:** Streaming de archivos grandes (logos)
- **General:** JSON vs. base de datos (trade-off simplicidad/performance)

---

## 6. Estrategias de Fallback y Resiliencia

### 6.1. Graceful Degradation

#### 6.1.1. Clima sin API Key
```python
if not api_key or api_key.strip() == "":
    logger.warning("API Key de clima no proporcionada")
    return None

# En app.py:
if weather_data is None:
    weather_data = {
        "ciudad": WEATHER_CITY,
        "temperatura": 0,
        "descripcion": "No disponible",
        # ... otros campos con valores por defecto
    }
```

#### 6.1.2. Error en Scraping de Logo
```python
try:
    # Intentar descargar logo
    downloaded_path = download_logo(logo_url, logo_filename)
    if not downloaded_path:
        logo_filename = None  # Fallback sin logo
except Exception as e:
    logger.error(f"Error descargando logo: {e}")
    # Continuar sin logo
```

#### 6.1.3. Error 403 en Scraping
```python
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 403:
        logger.warning(f"Acceso denegado (403) para {url}")
        # Crear favorito con información limitada
        favorite = { ... }  # Sin logo
        return favorite
```

### 6.2. Validación y Sanitización

#### 6.2.1. Validación de URLs
```javascript
// Frontend
try {
    new URL(url);
} catch {
    showFavoriteStatus('URL inválida', 'error');
    return;
}

// Backend (implícito en requests.get)
```

#### 6.2.2. Sanitización de Nombres de Archivo
```python
safe_domain = re.sub(r'[^\w\-\.]', '_', domain)
```

#### 6.2.3. Validación de Extensiones de Imagen
```python
if ext_lower in ['.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.webp']:
    extension = ext_lower
```

---

## 7. Estructuras de Datos en Memoria

### 7.1. Objeto Favorito en Memoria (Python dict)
```python
{
    'id': '20260311130959',          # str: timestamp como ID único
    'url': 'https://www.deepseek.com/',  # str: URL completa
    'title': 'DeepSeek',              # str: título legible
    'domain': 'www.deepseek.com',     # str: dominio limpio
    'logo': 'www.deepseek.com_20260311_130958.ico',  # str o None
    'tipo': 'favorito',               # str: 'favorito' o 'tarea_pendiente'
    'created_at': '2026-03-11T13:09:59.109372'  # str: ISO 8601
}
```

### 7.2. Estructura de Estado en Frontend
```javascript
// Estado implícito (no usa framework de estado)
let currentTheme = 'light';           // Tema actual
let updateInterval = 300000;          // Intervalo en ms
let refreshTimer = null;              // ID del timer

// Estado en DOM (no en memoria)
// - Lista de favoritos renderizada
// - Datos de divisas/clima en elementos DOM
```

### 7.3. Estructura de Configuración
```python
# Jerarquía de configuración:
# 1. Valores por defecto en config.py
# 2. Sobrescritos por variables de entorno
# 3. (Opcional) Sobrescritos por archivo de configuración externo

# Ejemplo de precedencia:
# config.py: UPDATE_INTERVAL = 300
# ENV: export UPDATE_INTERVAL=60
# Resultado: 60 segundos
```

---

## 8. Concurrencia y Thread Safety

### 8.1. Consideraciones de Flask
- **Single-threaded por defecto:** No hay concurrencia en desarrollo
- **Producción:** Usar Gunicorn/uWSGI para múltiples workers
- **Archivo JSON:** Posible race condition en escrituras concurrentes

### 8.2. Estrategias de Thread Safety

#### 8.2.1. Lectura/Escritura de favorites.json
```python
# Estrategia: Read-Modify-Write atómico
favorites = get_favorites()          # 1. Leer
favorites.append(new_favorite)       # 2. Modificar
save_favorites(favorites)            # 3. Escribir (sobrescribe completo)

# Ventaja: Operación atómica por archivo
# Desventaja: No escala para miles de items
```

#### 8.2.2. Descarga Concurrente de Logos
- **Problema:** Múltiples descargas simultáneas
- **Solución actual:** Secuencial (una por request)
- **Mejora potencial:** Thread pool para descargas

### 8.3. Consideraciones para Escalabilidad

#### 8.3.1. Escalado Vertical
- **Límite actual:** ~100 favoritos (JSON file)
- **Límite práctico:** ~1,000 favoritos (performance aceptable)
- **Bottleneck:** Parsing de JSON en cada operación

#### 8.3.2. Escalado Horizontal
- **Problema:** Archivo JSON no es compartible entre múltiples instancias
- **Solución:** Migrar a base de datos (SQLite, PostgreSQL)
- **Transición:** Mantener misma interfaz de funciones

---

## 9. Patrones de Testing (Actual y Potencial)

### 9.1. Testing Actual (Scripts Ad-hoc)
```python
# Ejemplo: test_domain_cleaning.py
test_cases = [
    ("www.example.com", "example.com"),
    ("listado.mercadolibre.com.ar", "mercadolibre.com.ar"),
    # ...
]
for input_domain, expected in test_cases:
    result = clean_domain(input_domain)
    assert result == expected, f"{input_domain} -> {result} != {expected}"
```

### 9.2. Estructura de Testing Potencial

#### 9.2.1. Unit Tests
```
tests/
├── unit/
│   ├── test_favorites_service.py
│   ├── test_dolar_service.py
│   └── test_weather_service.py
```

#### 9.2.2. Integration Tests
```
tests/
├── integration/
│   ├── test_api_endpoints.py
│   └── test_frontend_backend.py
```

#### 9.2.3. E2E Tests
```
tests/
└── e2e/
    └── test_user_workflows.py
```

### 9.3. Casos de Test Clave

#### 9.3.1. Servicio de Favoritos
```python
def test_add_favorite_success():
    # Arrange
    url = "https://example.com"
    
    # Act
    favorite = add_favorite(url, tipo="tarea_pendiente")
    
    # Assert
    assert favorite["url"] == url
    assert favorite["tipo"] == "tarea_pendiente"
    assert "id" in favorite
    assert "created_at" in favorite

def test_backward_compatibility():
    # Arrange: favorite sin campo tipo
    favorite_old = {"id": "1", "url": "https://old.com", "title": "Old"}
    
    # Act: get_favorites debería agregar tipo
    favorites = [favorite_old]
    # (simular carga desde JSON)
    
    # Assert
    assert favorite_old["tipo"] == "favorito"
```

#### 9.3.2. Frontend JavaScript
```javascript
// Ejemplo con Jest (potencial)
test('renderFavorites separa por tipo correctamente', () => {
    const favorites = [
        {id: '1', tipo: 'favorito', title: 'Fav 1'},
        {id: '2', tipo: 'tarea_pendiente', title: 'Task 1'},
        {id: '3', tipo: 'favorito', title: 'Fav 2'},
    ];
    
    const result = renderFavorites(favorites);
    // Verificar que se crean 2 secciones
    // Verificar counts correctos
    // Verificar orden (tasks primero)
});
```

---

## 10. Diagramas de Secuencia

### 10.1. Secuencia: Agregar Favorito con Logo
```
Usuario -> Frontend: Ingresa URL + selecciona tipo
Frontend -> Backend: POST /api/favorites {url, tipo}
Backend -> Sitio Web: GET URL (con User-Agent)
Sitio Web -> Backend: HTML response
Backend -> Backend: find_logo_url(html)
Backend -> Sitio Web: GET logo_url
Sitio Web -> Backend: Imagen logo
Backend -> Filesystem: Guardar logo como {domain}_{timestamp}.ext
Backend -> Filesystem: Agregar a favorites.json
Backend -> Frontend: 201 Created (favorite object)
Frontend -> Frontend: loadFavorites()
Frontend -> Backend: GET /api/favorites
Backend -> Frontend: Lista de favoritos actualizada
Frontend -> DOM: renderFavorites() separado por tipo
```

### 10.2. Secuencia: Auto-Refresh de Datos
```
Timer -> Frontend: setInterval callback
Frontend -> Backend: GET /api/data
Backend -> Bluelytics: GET https://api.bluelytics.com.ar/v2/latest
Bluelytics -> Backend: Datos de divisas
Backend -> OpenWeatherMap: GET weather?q=Córdoba&appid=...
OpenWeatherMap -> Backend: Datos climáticos
Backend -> Backend: Calcular brecha, combinar datos
Backend -> Frontend: JSON con datos combinados
Frontend -> DOM: updateUI() actualiza todos los valores
```

### 10.3. Secuencia: Eliminar Favorito
```
Usuario -> Frontend: Click botón basurero
Frontend -> Usuario: confirm("¿Estás seguro?")
Usuario -> Frontend: Confirmar
Frontend -> Backend: DELETE /api/favorites/{id}
Backend -> Filesystem: Buscar favorito en favorites.json
Backend -> Filesystem: Eliminar entrada
Backend -> Filesystem: Eliminar archivo de logo (si existe)
Backend -> Frontend: 200 OK {success: true}
Frontend -> Frontend: loadFavorites() y re-render
```

---

## 11. Decisiones de Diseño Arquitectónico

### 11.1. JSON vs Base de Datos
**Decisión:** Usar archivo JSON
**Razones:**
1. Simplicidad para MVP
2. Sin overhead de configuración de DB
3. Fácil backup/restore
4. Adecuado para volumen bajo (< 1000 items)

**Trade-offs:**
- ❌ No escala para miles de items
- ❌ No soporta concurrencia avanzada
- ❌ Búsquedas complejas ineficientes

### 11.2. Vanilla JS vs Framework
**Decisión:** Vanilla JavaScript puro
**Razones:**
1. Requerimiento explícito del usuario
2. Cero dependencias frontend
3. Performance óptimo (sin bundle size)
4. Curva de aprendizaje mínima para mantenimiento

**Trade-offs:**
- ❌ Más código boilerplate
- ❌ Gestión manual del estado DOM
- ❌ Menos herramientas de desarrollo

### 11.3. Scraping vs API de Logos
**Decisión:** Scraping HTML de sitios
**Razones:**
1. No hay API universal para logos
2. Mayor cobertura (cualquier sitio web)
3. Control sobre calidad/tamaño

**Trade-offs:**
- ❌ Menos confiable (sitios pueden cambiar HTML)
- ❌ Posibles bloqueos (403, rate limiting)
- ❌ Más lento que API dedicada

### 11.4. Tema Claro/Oscuro CSS vs JS
**Decisión:** CSS Variables + data attribute
**Razones:**
1. Performance (CSS hace el trabajo pesado)
2. Transiciones suaves nativas
3. Fácil mantenimiento (cambiar variables)

**Implementación:**
```css
:root { --primary-color: #2563eb; }
[data-theme="dark"] { --primary-color: #3b82f6; }
```
```javascript
document.documentElement.setAttribute('data-theme', 'dark');
```

---

## 12. Plan de Evolución Arquitectónica

### 12.1. Mejoras Inmediatas (Prioridad Alta)
1. **Cache de respuestas API:** Redis/Memcached para Bluelytics/OpenWeatherMap
2. **Compresión de logos:** Convertir a WebP/AVIF para reducir tamaño
3. **Paginación de favoritos:** Lazy loading para listas grandes

### 12.2. Mejuras a Medio Plazo
1. **Migración a SQLite:** Mantener simplicidad pero ganar queries
2. **Service Worker:** Offline functionality para favoritos
3. **CDN para logos:** Cloudflare/Imgix para servir imágenes optimizadas

### 12.3. Rediseño Completo (Si escala)
1. **Frontend:** React/Vue para mejor gestión de estado
2. **Backend:** FastAPI/Django REST Framework
3. **Base de datos:** PostgreSQL con relaciones (favoritos, usuarios, categorías)
4. **Autenticación:** JWT para usuarios múltiples

---

## 13. Métricas y Monitoreo

### 13.1. Métricas Clave Actuales
- **Tiempo de carga de página:** < 3 segundos
- **Tasa de éxito scraping logos:** ~80% (estimado)
- **Uso de memoria:** < 100MB (Python + Frontend)

### 13.2. Métricas a Implementar
```python
# Ejemplo de logging estructurado (potencial)
logger.info("favorite_added", extra={
    "url": url,
    "tipo": tipo,
    "has_logo": logo_filename is not None,
    "processing_time": end_time - start_time
})
```

### 13.3. Health Checks
```python
# Endpoint potencial: GET /api/health
{
    "status": "healthy",
    "services": {
        "bluelytics": {"status": "up", "response_time": 120},
        "openweathermap": {"status": "up", "response_time": 250},
        "storage": {"status": "up", "favorites_count": 42}
    },
    "timestamp": "2026-03-11T16:30:00-03:00"
}
```

---

*Última actualización: 11 de marzo de 2026 - Documentación completa de arquitectura y algoritmos*