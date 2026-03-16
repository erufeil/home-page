# Context Library - Diccionario de Referencia Técnica

Este archivo contiene un diccionario completo de todos los endpoints, variables, estructuras de datos, funciones, clases CSS y constantes utilizadas en el proyecto. Úsalo como referencia para asegurar consistencia en el desarrollo.

---

## 1. Endpoints API (Backend Flask)

### 1.1. Endpoint Principal de Datos
- **URL:** `GET /api/data`
- **Método:** `GET`
- **Descripción:** Retorna datos combinados de divisas y clima
- **Respuesta Exitosa (200 OK):**
```json
{
  "timestamp": "2026-03-11T16:30:00-03:00",
  "dolar": {
    "euro_oficial": {
      "compra": 1390.00,
      "venta": 1441.00,
      "promedio": 1415.50
    },
    "dolar_oficial": {
      "compra": 1390.00,
      "venta": 1441.00,
      "promedio": 1415.50
    },
    "dolar_blue": {
      "compra": 1405.00,
      "venta": 1425.00,
      "promedio": 1415.00
    },
    "brecha": 2.15,
    "ultima_actualizacion": "2026-03-11T10:00:52-03:00"
  },
  "clima": {
    "ciudad": "Córdoba",
    "temperatura": 28.5,
    "sensacion": 30.0,
    "humedad": 65,
    "descripcion": "Parcialmente nublado",
    "icono": "02d"
  },
  "update_interval": 300
}
```
- **Respuesta de Error:** Retorna estructura similar con valores cero/placeholder
- **Notas:** Actualización automática cada 5 minutos (300 segundos)

### 1.2. Endpoints de Gestión de Favoritos

#### `GET /api/favorites`
- **Método:** `GET`
- **Descripción:** Obtiene la lista completa de favoritos/tareas pendientes
- **Respuesta Exitosa (200 OK):**
```json
[
  {
    "id": "20260311130959",
    "url": "https://www.deepseek.com/",
    "title": "DeepSeek",
    "domain": "www.deepseek.com",
    "logo": "www.deepseek.com_20260311_130958.ico",
    "tipo": "favorito",
    "created_at": "2026-03-11T13:09:59.109372"
  }
]
```
- **Respuesta de Error (500):** `{"error": "No se pudieron obtener los favoritos"}`

#### `POST /api/favorites`
- **Método:** `POST`
- **Descripción:** Agrega un nuevo sitio a favoritos o tareas pendientes
- **Headers:** `Content-Type: application/json`
- **Request Body:**
```json
{
  "url": "https://ejemplo.com",
  "title": "Título opcional",
  "tipo": "favorito"
}
```
- **Valores de `tipo`:** `"favorito"` (default), `"tarea_pendiente"`
- **Respuesta Exitosa (201 Created):** Retorna el objeto favorito creado (misma estructura que GET)
- **Respuesta de Error (400):** `{"error": "URL requerida"}`
- **Respuesta de Error (500):** `{"error": "No se pudo agregar el favorito"}`

#### `DELETE /api/favorites/{id}`
- **Método:** `DELETE`
- **Descripción:** Elimina un favorito por ID
- **Path Parameter:** `favorite_id` (string, formato: "20260311130959")
- **Respuesta Exitosa (200 OK):** `{"success": true}`
- **Respuesta de Error (404):** `{"error": "Favorito no encontrado"}`
- **Respuesta de Error (500):** `{"error": "No se pudo eliminar el favorito"}`

### 1.3. Endpoints de Servicio de Archivos

#### `GET /`
- **Método:** `GET`
- **Descripción:** Sirve el archivo `frontend/index.html`
- **Respuesta:** HTML del frontend

#### `GET /<path:path>`
- **Método:** `GET`
- **Descripción:** Sirve archivos estáticos del frontend (CSS, JS)
- **Ejemplos:** `/css/styles.css`, `/js/app.js`

#### `GET /favorites/logos/<filename>`
- **Método:** `GET`
- **Descripción:** Sirve logos de favoritos desde el directorio `favorites/logos/`
- **Path Parameter:** `filename` (nombre del archivo de logo)
- **Ejemplo:** `/favorites/logos/www.deepseek.com_20260311_130958.ico`

---

## 2. Variables de Configuración (config.py)

### 2.1. Variables Principales
| Variable | Valor Default | Tipo | Descripción |
|----------|---------------|------|-------------|
| `DOLAR_API_URL` | `"https://api.bluelytics.com.ar/v2/latest"` | string | URL de API de cotizaciones |
| `WEATHER_API_URL` | `"https://api.openweathermap.org/data/2.5/weather"` | string | URL de API de clima |
| `WEATHER_CITY` | `"Córdoba"` | string | Ciudad para consulta climática |
| `WEATHER_API_KEY` | `""` (vacío) | string | API Key de OpenWeatherMap |
| `UPDATE_INTERVAL` | `300` | int | Segundos entre actualizaciones |
| `FLASK_HOST` | `"127.0.0.1"` | string | Host del servidor Flask |
| `FLASK_PORT` | `5000` | int | Puerto del servidor Flask |
| `ENABLE_CORS` | `True` | bool | Habilitar CORS para desarrollo |

### 2.2. Variables de Entorno Soportadas
Todas las variables anteriores pueden ser sobrescritas por variables de entorno con el mismo nombre en uppercase:
- `DOLAR_API_URL`
- `WEATHER_API_URL`
- `WEATHER_CITY`
- `WEATHER_API_KEY`
- `UPDATE_INTERVAL`
- `FLASK_HOST`
- `FLASK_PORT`
- `ENABLE_CORS`

**Ejemplo (Windows PowerShell):**
```powershell
$env:WEATHER_API_KEY="tu_api_key_aquí"
$env:FLASK_PORT=5001
```

---

## 3. Estructuras de Datos

### 3.1. Objeto Favorito (JSON Schema)
```json
{
  "type": "object",
  "required": ["id", "url", "title", "domain", "tipo", "created_at"],
  "properties": {
    "id": {
      "type": "string",
      "pattern": "^\\d{14}$",
      "description": "ID único en formato YYYYMMDDHHMMSS"
    },
    "url": {
      "type": "string",
      "format": "uri",
      "description": "URL completa del sitio web"
    },
    "title": {
      "type": "string",
      "description": "Título del sitio (extraído automáticamente o proporcionado)"
    },
    "domain": {
      "type": "string",
      "description": "Dominio limpio (sin www, subdominios comunes)"
    },
    "logo": {
      "type": ["string", "null"],
      "description": "Nombre del archivo de logo o null si no hay logo"
    },
    "tipo": {
      "type": "string",
      "enum": ["favorito", "tarea_pendiente"],
      "default": "favorito",
      "description": "Categoría del sitio"
    },
    "created_at": {
      "type": "string",
      "format": "date-time",
      "description": "Fecha de creación en ISO 8601"
    }
  }
}
```

### 3.2. Estructura de Datos de Divisas
```json
{
  "euro_oficial": {
    "compra": "number (float)",
    "venta": "number (float)", 
    "promedio": "number (float)"
  },
  "dolar_oficial": {
    "compra": "number (float)",
    "venta": "number (float)",
    "promedio": "number (float)"
  },
  "dolar_blue": {
    "compra": "number (float)",
    "venta": "number (float)",
    "promedio": "number (float)"
  },
  "brecha": "number (float, 2 decimales)",
  "ultima_actualizacion": "string (ISO 8601)"
}
```

### 3.3. Estructura de Datos Climáticos
```json
{
  "ciudad": "string",
  "temperatura": "number (float, Celsius)",
  "sensacion": "number (float, Celsius)",
  "humedad": "number (integer, porcentaje)",
  "descripcion": "string (capitalizado en español)",
  "icono": "string (código de icono OpenWeatherMap)"
}
```

### 3.4. Archivo favorites.json
- **Ubicación:** `favorites/favorites.json`
- **Formato:** Array JSON de objetos favorito
- **Backup Automático:** Se crean archivos `.backup` automáticamente
- **Migración:** El campo `tipo` se agrega automáticamente a favoritos existentes

---

## 4. Funciones del Backend (services/)

### 4.1. Servicio: `services/favorites.py`

#### `get_favorites() -> List[Dict]`
- **Descripción:** Obtiene la lista de favoritos desde el archivo JSON
- **Retorno:** Lista de objetos favorito
- **Migración:** Agrega campo `tipo` con valor `"favorito"` si falta
- **Manejo de errores:** Retorna lista vacía `[]` si hay error

#### `save_favorites(favorites: List[Dict]) -> None`
- **Descripción:** Guarda la lista de favoritos en el archivo JSON
- **Parámetros:** `favorites` - Lista de objetos favorito
- **Formato:** JSON con indentación 2, ensure_ascii=False

#### `add_favorite(url: str, title: str = None, tipo: str = 'favorito') -> Dict`
- **Descripción:** Agrega un nuevo favorito con scraping de logo
- **Parámetros:**
  - `url`: URL del sitio (requerido)
  - `title`: Título opcional (si es None, se extrae del HTML)
  - `tipo`: `'favorito'` (default) o `'tarea_pendiente'`
- **Retorno:** Objeto favorito creado
- **Proceso:**
  1. Descarga HTML del sitio
  2. Busca logo usando patrones de regex
  3. Descarga y guarda logo localmente
  4. Extrae título si no se proporcionó
  5. Crea objeto favorito con ID timestamp
  6. Guarda en favorites.json

#### `delete_favorite(favorite_id: str) -> bool`
- **Descripción:** Elimina un favorito por ID y su archivo de logo asociado
- **Parámetros:** `favorite_id` - ID del favorito a eliminar
- **Retorno:** `True` si se eliminó, `False` si no se encontró

#### `extract_domain(url: str) -> str`
- **Descripción:** Extrae el dominio de una URL usando `urllib.parse.urlparse`
- **Ejemplo:** `"https://www.example.com/path"` → `"www.example.com"`

#### `clean_domain(domain: str) -> str`
- **Descripción:** Limpia un dominio removiendo subdominios comunes (www, listado, m., etc.)
- **Ejemplo:** `"www.example.com"` → `"example.com"`
- **TLDs soportados:** .com, .org, .net, .ar, .com.ar, .gob.ar, .uk, .co.uk, etc.

#### `clean_domain_name(domain: str) -> str`
- **Descripción:** Convierte un dominio en un nombre legible para título
- **Ejemplo:** `"www.example-site.com"` → `"Example Site"`

#### `find_logo_url(html_content: str, base_url: str) -> str`
- **Descripción:** Busca URLs de logos en contenido HTML usando patrones regex
- **Patrones en orden de prioridad:**
  1. Favicon (rel="icon", rel="shortcut icon")
  2. Open Graph image (og:image)
  3. Twitter image (twitter:image)
  4. Logo en clase CSS (class*="logo")
  5. Logo en alt text (alt*="logo")
  6. Imágenes que contengan "logo" o "brand" en src
  7. Fallback a /favicon.ico

#### `download_logo(logo_url: str, filename: str) -> str`
- **Descripción:** Descarga un logo y lo guarda localmente
- **Headers:** User-Agent de Chrome para evitar bloqueos
- **Retorno:** Ruta del archivo descargado o `None` si falla

### 4.2. Servicio: `services/dolar.py`

#### `get_dolar_data() -> Dict`
- **Descripción:** Obtiene datos de cotización desde Bluelytics API
- **Timeout:** 10 segundos
- **Estructura de retorno:** Ver sección 3.2
- **Cálculo de brecha:** `((euro_oficial.venta / dolar_oficial.venta) - 1) * 100`
- **Manejo de errores:** Retorna `None` si hay error

### 4.3. Servicio: `services/weather.py`

#### `get_weather_data(city: str, api_key: str) -> Dict`
- **Descripción:** Obtiene datos climáticos desde OpenWeatherMap
- **Parámetros:**
  - `city`: Nombre de la ciudad
  - `api_key`: API Key de OpenWeatherMap (si está vacía, retorna `None`)
- **Unidades:** Métricas (Celsius)
- **Idioma:** Español (`lang=es`)
- **Estructura de retorno:** Ver sección 3.3
- **Manejo de errores:** Retorna `None` si hay error o API key vacía

---

## 5. Funciones del Frontend (app.js)

### 5.1. Variables Globales
| Variable | Tipo | Descripción |
|----------|------|-------------|
| `API_URL` | `string` | `'/api/data'` - Endpoint principal |
| `updateInterval` | `number` | Intervalo de actualización en ms (default: 300000) |
| `currentTheme` | `string` | `'light'` o `'dark'` desde localStorage |
| `refreshTimer` | `number` | ID del timer de auto-refresh |
| `numberFormatter` | `Intl.NumberFormat` | Formateador de números argentinos |
| `dateFormatter` | `Intl.DateTimeFormat` | Formateador de fechas argentinas |
| `elements` | `object` | Diccionario de elementos DOM |

### 5.2. Objeto `elements` (Referencias DOM)
```javascript
const elements = {
  // Divisas
  euroCompra: document.getElementById('euroCompra'),
  euroVenta: document.getElementById('euroVenta'),
  oficialCompra: document.getElementById('oficialCompra'),
  oficialVenta: document.getElementById('oficialVenta'),
  blueCompra: document.getElementById('blueCompra'),
  blueVenta: document.getElementById('blueVenta'),
  brecha: document.getElementById('brecha'),
  dolarUpdateTime: document.getElementById('dolarUpdateTime'),
  
  // Clima
  ciudadClima: document.getElementById('ciudadClima'),
  temperatura: document.getElementById('temperatura'),
  sensacion: document.getElementById('sensacion'),
  humedad: document.getElementById('humedad'),
  descripcionClima: document.getElementById('descripcionClima'),
  weatherIcon: document.getElementById('weatherIcon'),
  
  // Controles
  themeToggle: document.getElementById('themeToggle'),
  refreshBtn: document.getElementById('refreshBtn'),
  updateInterval: document.getElementById('updateInterval'),
  fullUpdateTime: document.getElementById('fullUpdateTime'),
  
  // Favoritos
  urlInput: document.getElementById('urlInput'),
  titleInput: document.getElementById('titleInput'),
  typeInput: document.getElementById('typeInput'),
  addFavoriteBtn: document.getElementById('addFavoriteBtn'),
  favoriteStatus: document.getElementById('favoriteStatus'),
  favoritesCount: document.getElementById('favoritesCount'),
  favoritesContainer: document.getElementById('favoritesContainer'),
  favoritesPlaceholder: document.getElementById('favoritesPlaceholder'),
  
  // Error
  errorMessage: document.querySelector('.error-message')
};
```

### 5.3. Funciones Principales

#### `init()`
- **Descripción:** Inicializa la aplicación
- **Llama:** `applyTheme()`, `setupEventListeners()`, `loadData()`, `loadFavorites()`, `startAutoRefresh()`

#### `applyTheme()`
- **Descripción:** Aplica tema claro/oscuro basado en `currentTheme`
- **Actualiza:** `data-theme` attribute en `document.documentElement`
- **Persistencia:** Usa `localStorage.getItem('theme')`

#### `setupEventListeners()`
- **Descripción:** Configura todos los event listeners
- **Eventos:**
  - `themeToggle.click`: Cambia tema claro/oscuro
  - `refreshBtn.click`: Refresca datos manualmente
  - `addFavoriteBtn.click`: Agrega favorito
  - `urlInput.keypress` (Enter): Agrega favorito

#### `loadData(manualRefresh = false)`
- **Descripción:** Carga datos desde API y actualiza UI
- **Parámetros:** `manualRefresh` - true si es refresco manual (muestra animación)
- **Fetch:** `fetch(API_URL)` con manejo de errores
- **Llama:** `updateUI(data)` con datos recibidos

#### `updateUI(data)`
- **Descripción:** Actualiza todos los elementos del DOM con datos
- **Actualiza:** Divisas, clima, timestamps, intervalo
- **Formateo:** Usa `numberFormatter` y `dateFormatter`
- **Colores de brecha:**
  - > 10%: color danger (rojo)
  - > 5%: color warning (naranja)
  - ≤ 5%: color accent (verde)

#### `updateWeatherIcon(iconCode)`
- **Descripción:** Actualiza icono del clima basado en código OpenWeatherMap
- **Mapeo:** Códigos a clases FontAwesome
- **Colores:** Según tipo de clima (soleado, lluvioso, etc.)

#### `addFavorite()`
- **Descripción:** Agrega un nuevo favorito/tarea pendiente
- **Valida:** URL requerida, URL válida
- **Envía:** POST a `/api/favorites` con `{url, title, tipo}`
- **Tipo:** Obtiene de `elements.typeInput.value` (`'favorito'` o `'tarea_pendiente'`)
- **Feedback:** Muestra estado de éxito/error por 5 segundos

#### `loadFavorites()`
- **Descripción:** Carga favoritos desde API y los renderiza
- **Fetch:** `GET /api/favorites`
- **Llama:** `updateFavoritesCount(count)`, `renderFavorites(favorites)`

#### `renderFavorites(favorites)`
- **Descripción:** Renderiza favoritos separados por tipo en el DOM
- **Separación:** Filtra por `tipo`: `'tarea_pendiente'` (arriba), `'favorito'` (abajo)
- **Estructura:**
  ```html
  <div class="favorites-section">
    <h3 class="favorites-section-header">Tareas Pendientes (2)</h3>
    <div class="favorites-grid">...</div>
  </div>
  <hr class="section-divider">
  <div class="favorites-section">
    <h3 class="favorites-section-header">Favoritos (5)</h3>
    <div class="favorites-grid">...</div>
  </div>
  ```
- **Condiciones:** Solo muestra secciones que tienen items, solo muestra divisor si ambas existen

#### `createFavoriteCard(favorite)`
- **Descripción:** Crea elemento DOM para una card de favorito
- **Estructura HTML generada:**
  ```html
  <div class="favorite-card" data-id="20260311130959" role="button" tabindex="0" aria-label="Visitar DeepSeek">
    <!-- Logo (img o placeholder) -->
    <div class="favorite-title">DeepSeek</div>
    <div class="favorite-domain-row">
      <div class="favorite-domain">www.deepseek.com</div>
      <button class="btn-delete-favorite" title="Eliminar favorito">
        <i class="fas fa-trash"></i>
      </button>
    </div>
  </div>
  ```
- **Clicabilidad:** Toda la card abre URL (excepto botón basurero)
- **Teclado:** Soporta Enter/Space para abrir URL
- **Accesibilidad:** `role="button"`, `tabindex="0"`, `aria-label`

#### `deleteFavorite(favoriteId)`
- **Descripción:** Elimina un favorito con confirmación
- **Fetch:** `DELETE /api/favorites/{id}`
- **Confirmación:** `confirm()` nativo del navegador
- **Recarga:** Llama `loadFavorites()` después de eliminar

#### `startAutoRefresh()`
- **Descripción:** Inicia auto-refresh basado en `updateInterval`
- **Intervalo:** Configurable desde API (default: 5 minutos)
- **Clear:** Limpia timer existente antes de crear nuevo

---

## 6. Clases CSS (styles.css)

### 6.1. Variables CSS (Custom Properties)
```css
/* Colores base */
--primary-color: #2563eb;      /* Azul principal */
--secondary-color: #7c3aed;    /* Púrpura */
--accent-color: #059669;       /* Verde */
--danger-color: #dc2626;       /* Rojo */
--warning-color: #d97706;      /* Naranja */

/* Fondos y superficie */
--bg-color: #f8fafc;           /* Fondo de página */
--surface-color: #ffffff;      /* Superficie de cards */
--surface-elevated: #f1f5f9;   /* Fondo elevado */

/* Texto */
--text-primary: #1e293b;       /* Texto principal */
--text-secondary: #64748b;     /* Texto secundario */
--text-muted: #94a3b8;         /* Texto atenuado */

/* Bordes y sombras */
--border-color: #e2e8f0;
--border-radius: 12px;
--shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);

/* Espaciado */
--spacing-xs: 0.5rem;
--spacing-sm: 1rem;
--spacing-md: 1.5rem;
--spacing-lg: 2rem;
--spacing-xl: 3rem;

/* Transiciones */
--transition: all 0.3s ease;
```

### 6.2. Clases de Temas
- **Tema claro:** `:root` (default)
- **Tema oscuro:** `[data-theme="dark"]` (sobrescribe variables)
- **Activación:** `document.documentElement.setAttribute('data-theme', 'dark')`

### 6.3. Layout y Contenedores
| Clase | Propiedades CSS | Uso |
|-------|----------------|-----|
| `.container` | `max-width: 1200px`, `margin: 0 auto`, `padding` | Contenedor principal centrado |
| `.layout-container` | `display: grid`, `grid-template-columns: 1fr 350px` | Layout de 2 columnas |
| `.main-content` | `background-color: var(--surface-color)`, `border-radius`, `padding`, `box-shadow` | Área principal |
| `.sidebar` | `background-color: var(--surface-color)`, `border-radius`, `padding`, `box-shadow` | Barra lateral |

### 6.4. Cards
| Clase | Descripción |
|-------|-------------|
| `.card` | Card base con sombra, borde radius, padding |
| `.card-header` | Encabezado de card con borde inferior |
| `.card-body` | Cuerpo de card con padding superior |
| `.card-blue` | Borde superior azul (dólar blue) |
| `.card-oficial` | Borde superior verde (dólar oficial) |
| `.card-brecha` | Borde superior púrpura (brecha) |
| `.card-weather` | Borde superior naranja (clima) |
| `.card-info` | Borde superior gris (información) |
| `.card-euro` | Borde superior turquesa (euro) |
| `.card-favorites` | Borde superior rosa (favoritos) |

### 6.5. Sistema de Favoritos
| Clase | Descripción |
|-------|-------------|
| `.favorites-container` | Contenedor principal de favoritos |
| `.favorites-placeholder` | Placeholder cuando no hay favoritos |
| `.favorites-grid` | Grid de cards de favoritos |
| `.favorite-card` | Card individual de favorito |
| `.favorite-logo` | Imagen de logo (48x48px) |
| `.favorite-logo-placeholder` | Placeholder de logo con icono globe |
| `.favorite-title` | Título del favorito (negrita) |
| `.favorite-domain` | Dominio del sitio (texto pequeño) |
| `.favorite-domain-row` | Fila que contiene dominio + botón basurero |
| `.btn-delete-favorite` | Botón basurero para eliminar favorito |
| `.favorites-section` | Sección de favoritos por tipo |
| `.favorites-section-header` | Encabezado de sección con contador |
| `.section-divider` | Divisor horizontal entre secciones |

### 6.6. Formularios
| Clase | Descripción |
|-------|-------------|
| `.favorites-form` | Formulario para agregar favoritos |
| `.form-group` | Grupo de campo de formulario |
| `.url-input`, `.title-input` | Campos de entrada de texto |
| `.btn-add-favorite` | Botón para agregar favorito |
| `.favorite-status` | Mensaje de estado (éxito/error) |
| `.favorite-status.success` | Estado de éxito (verde) |
| `.favorite-status.error` | Estado de error (rojo) |

### 6.7. Precios y Valores
| Clase | Descripción |
|-------|-------------|
| `.price-main` | Contenedor principal de precio (compra) |
| `.price-secondary` | Contenedor secundario de precio (venta) |
| `.price-label` | Etiqueta de precio |
| `.price-label-small` | Etiqueta pequeña de precio |
| `.price-value-large` | Valor grande de precio (2.5rem) |
| `.price-value` | Valor normal de precio (1.5rem) |
| `.price-value-small` | Valor pequeño de precio (1.25rem) |
| `.brecha-value` | Valor de brecha grande (2.5rem) |
| `.brecha-desc` | Descripción de brecha |

### 6.8. Clima
| Clase | Descripción |
|-------|-------------|
| `.weather-icon` | Icono grande del clima |
| `.weather-temp` | Contenedor de temperatura |
| `.temp-value` | Valor de temperatura (3rem) |
| `.temp-unit` | Unidad de temperatura (°C) |
| `.weather-desc` | Descripción del clima |
| `.weather-details` | Detalles climáticos (humedad, sensación) |
| `.detail` | Elemento individual de detalle |

### 6.9. Estados y Utilidades
| Clase | Descripción |
|-------|-------------|
| `.loading` | Estado de carga (opacidad reducida) |
| `.error-message` | Mensaje de error global |
| `.error-message.show` | Mensaje de error visible |
| `.badge` | Badge para contadores o etiquetas |
| `.btn-toggle` | Botón para alternar tema |
| `.btn-refresh` | Botón de refrescar datos |
| `.refreshing` | Estado de refresco (animación de giro) |

### 6.10. Responsive Design
| Media Query | Aplicación |
|-------------|------------|
| `@media (max-width: 1024px)` | Layout de 1 columna en tablet |
| `@media (max-width: 768px)` | Grid de 1 columna en móvil |

---

## 7. IDs HTML (index.html)

### 7.1. Panel de Divisas
| ID | Elemento | Uso |
|----|----------|-----|
| `euroCompra` | `span` | Valor de compra del euro |
| `euroVenta` | `span` | Valor de venta del euro |
| `oficialCompra` | `span` | Valor de compra del dólar oficial |
| `oficialVenta` | `span` | Valor de venta del dólar oficial |
| `blueCompra` | `span` | Valor de compra del dólar blue |
| `blueVenta` | `span` | Valor de venta del dólar blue |
| `brecha` | `span` | Porcentaje de brecha |
| `dolarUpdateTime` | `span` | Hora de última actualización de divisas |

### 7.2. Panel Climático
| ID | Elemento | Uso |
|----|----------|-----|
| `ciudadClima` | `span` | Nombre de la ciudad |
| `temperatura` | `span` | Temperatura actual |
| `sensacion` | `span` | Sensación térmica |
| `humedad` | `span` | Porcentaje de humedad |
| `descripcionClima` | `span` | Descripción del clima |
| `weatherIcon` | `div` | Contenedor de icono del clima |

### 7.3. Controles y Estado
| ID | Elemento | Uso |
|----|----------|-----|
| `themeToggle` | `button` | Botón para alternar tema claro/oscuro |
| `refreshBtn` | `button` | Botón para refrescar datos manualmente |
| `updateInterval` | `span` | Minutos de intervalo de actualización |
| `fullUpdateTime` | `span` | Hora de última actualización completa |

### 7.4. Sistema de Favoritos
| ID | Elemento | Uso |
|----|----------|-----|
| `urlInput` | `input` | Campo para URL del sitio |
| `titleInput` | `input` | Campo opcional para título |
| `typeInput` | `select` | Selector de tipo (favorito/tarea pendiente) |
| `addFavoriteBtn` | `button` | Botón para guardar sitio |
| `favoriteStatus` | `div` | Mensaje de estado del formulario |
| `favoritesCount` | `span` | Contador de favoritos totales |
| `favoritesContainer` | `div` | Contenedor de grid de favoritos |
| `favoritesPlaceholder` | `div` | Placeholder cuando no hay favoritos |

### 7.5. Elementos Varios
| ID/Class | Elemento | Uso |
|----------|----------|-----|
| `.error-message` | `div` | Mensaje de error global |
| `.last-update` | `div` | Contenedor de timestamp |

---

## 8. Constantes y Valores Predefinidos

### 8.1. Valores de Tipo (`tipo`)
- `"favorito"` (default): Sitios marcados como favoritos
- `"tarea_pendiente"`: Sitios marcados como tareas pendientes

### 8.2. Formatos de Fecha/Hora
- **ID de favorito:** `YYYYMMDDHHMMSS` (ej: `20260311130959`)
- **ISO 8601:** `YYYY-MM-DDTHH:MM:SS.mmmmmm` para `created_at`
- **Visualización:** `HH:MM:SS DD/MM/YYYY` con `toLocaleDateString('es-AR')`

### 8.3. Formatos Numéricos
- **Divisas:** `$ 1.234,56` con `Intl.NumberFormat('es-AR')`
- **Porcentajes:** `2,15 %` (2 decimales)
- **Temperatura:** `28,5 °C` (1 decimal)

### 8.4. Nombres de Archivo de Logos
- **Formato:** `{dominio}_{YYYYMMDD}_{HHMMSS}{extensión}`
- **Ejemplo:** `www.deepseek.com_20260311_130958.ico`
- **Extensiones soportadas:** `.png`, `.jpg`, `.jpeg`, `.gif`, `.ico`, `.svg`, `.webp`

### 8.5. Mapeo de Iconos de Clima
| Código OpenWeatherMap | Clase FontAwesome | Descripción |
|-----------------------|-------------------|-------------|
| `01d`, `01n` | `fas fa-sun`, `fas fa-moon` | Cielo despejado |
| `02d`, `02n` | `fas fa-cloud-sun`, `fas fa-cloud-moon` | Pocas nubes |
| `03d`, `03n` | `fas fa-cloud` | Nubes dispersas |
| `04d`, `04n` | `fas fa-cloud` | Nubes rotas |
| `09d`, `09n` | `fas fa-cloud-rain` | Lluvia ligera |
| `10d`, `10n` | `fas fa-cloud-sun-rain`, `fas fa-cloud-moon-rain` | Lluvia |
| `11d`, `11n` | `fas fa-bolt` | Tormenta eléctrica |
| `13d`, `13n` | `fas fa-snowflake` | Nieve |
| `50d`, `50n` | `fas fa-smog` | Neblina |

---

## 9. Dependencias Externas

### 9.1. Backend (requirements.txt)
| Paquete | Versión | Uso |
|---------|---------|-----|
| Flask | 2.3.3 | Framework web |
| requests | 2.31.0 | Cliente HTTP para APIs externas |
| Flask-CORS | 4.0.0 | Middleware CORS para desarrollo |

### 9.2. Frontend (CDN)
| Recurso | URL | Uso |
|---------|-----|-----|
| Font Awesome | `cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css` | Iconos |
| Google Fonts (Inter) | `fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap` | Tipografía |

---

## 10. Reglas de Desarrollo (NO VIOLAR)

### 10.1. Backend (Python)
- ✅ Usar `logging` para registro de eventos, no `print()`
- ✅ Timeout de 10 segundos en todas las llamadas HTTP externas
- ✅ Validar entradas del usuario antes de procesar
- ✅ Manejar todos los errores con `try/except` apropiados
- ❌ Nunca exponer datos sensibles en logs

### 10.2. Frontend (JavaScript)
- ✅ Vanilla JavaScript puro (sin frameworks)
- ✅ Usar `.then()` en lugar de `async/await` complejo
- ✅ `Intl.NumberFormat('es-AR')` para formateo numérico
- ✅ `toLocaleDateString('es-AR')` para formateo de fechas
- ❌ Nunca usar `as any`, `@ts-ignore`, `@ts-expect-error`
- ❌ Nunca suprimir errores de tipo TypeScript
- ❌ Nunca dejar bloques `catch` vacíos

### 10.3. CSS
- ✅ Usar variables CSS para colores, espaciado, etc.
- ✅ Mobile-first responsive design
- ✅ Prefijos de navegador solo cuando sea necesario
- ❌ Evitar !important a menos que sea absolutamente necesario

### 10.4. General
- ✅ Mantener backward compatibility con datos existentes
- ✅ Documentar cambios en `context-memory.md`
- ✅ Verificar que todo funcione después de cambios
- ❌ Nunca committear cambios sin solicitud explícita del usuario

---

## 11. Convenciones de Nomenclatura

### 11.1. Python
- **Funciones:** `snake_case` (ej: `get_favorites`)
- **Variables:** `snake_case` (ej: `favorite_id`)
- **Constantes:** `UPPER_SNAKE_CASE` (ej: `UPDATE_INTERVAL`)
- **Clases:** `PascalCase` (no hay clases actualmente)

### 11.2. JavaScript
- **Variables/Constantes:** `camelCase` (ej: `updateInterval`)
- **Funciones:** `camelCase` (ej: `loadFavorites`)
- **Clases CSS en JS:** `.kebab-case` (ej: `favorite-card`)

### 11.3. CSS
- **Clases:** `.kebab-case` (ej: `.favorite-card`)
- **IDs:** `camelCase` (ej: `#favoritesContainer`)
- **Variables CSS:** `--kebab-case` (ej: `--primary-color`)

### 11.4. HTML
- **IDs:** `camelCase` (ej: `typeInput`)
- **Data attributes:** `data-kebab-case` (ej: `data-id`)

---

## 12. Archivos de Datos y Logs

### 12.1. Archivos de Datos
| Archivo | Ubicación | Descripción |
|---------|-----------|-------------|
| `favorites.json` | `favorites/favorites.json` | Base de datos principal de favoritos |
| `favorites.json.backup` | `favorites/` | Backup automático |
| `favorites.json.fix.backup` | `favorites/` | Backup de reparación |
| `*.ico, *.png, *.svg` | `favorites/logos/` | Logos descargados de sitios |

### 12.2. Archivos de Logs
| Archivo | Ubicación | Descripción |
|---------|-----------|-------------|
| `server.log` | `backend/` | Logs del servidor Flask |
| `flask_logs.txt` | `backend/` | Logs de Flask |
| `server_output.log` | `backend/` | Salida del servidor |

---

## 13. Scripts y Utilidades

### 13.1. Scripts de Ejecución
| Script | Ubicación | Uso |
|--------|-----------|-----|
| `start_flask.ps1` | raíz | Inicia servidor Flask (Windows PowerShell) |
| `start_server.ps1` | raíz | Alternativa para iniciar servidor |
| `correrpow.bat` | `backend/` | Batch para ejecutar en Windows |
| `test_api.ps1` | `backend/` | Pruebas de API |

### 13.2. Scripts de Prueba
| Script | Ubicación | Uso |
|--------|-----------|-----|
| `test_favorites.py` | raíz | Pruebas del servicio de favoritos |
| `quick_test.py` | raíz | Pruebas rápidas |
| `test_api_brecha.py` | raíz | Pruebas de cálculo de brecha |
| `test_brecha.py` | raíz | Más pruebas de brecha |
| `test_server.py` | raíz | Pruebas del servidor |
| `test_domain_cleaning.py` | `backend/` | Pruebas de limpieza de dominios |

---

*Última actualización: 11 de marzo de 2026 - Documentación completa del sistema*