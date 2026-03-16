# Contexto IA - Landing Page Dólar + Clima + Favoritos

## Descripción del Proyecto
Aplicación web completa que muestra en tiempo real cotizaciones del dólar argentino, datos climáticos y un sistema de gestión de sitios web favoritos con scraping automático de logos.

## Stack Tecnológico
- **Backend:** Python 3.12 + Flask + SQLite (JSON file storage)
- **Frontend:** HTML5 + CSS3 + Vanilla JavaScript (sin frameworks)
- **APIs Externas:**
  - Dólar: Bluelytics API (gratuita, sin autenticación)
  - Clima: OpenWeatherMap API (requiere API key gratuita)
- **Almacenamiento:** JSON files para persistencia de datos

## Arquitectura General
```
┌─────────────────────────────────────────────────────────────┐
│                       Frontend (Browser)                    │
│  ┌─────────────┐  ┌─────────────┐  ┌───────────────────┐  │
│  │   Dólar     │  │   Clima     │  │  Favoritos/Tareas │  │
│  │   Panel     │  │   Panel     │  │     Manager       │  │
│  └─────────────┘  └─────────────┘  └───────────────────┘  │
│                    (Actualización automática cada 5 min)    │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP/JSON
┌───────────────────────────▼─────────────────────────────────┐
│                     Backend (Flask)                         │
│  ┌─────────────┐  ┌─────────────┐  ┌───────────────────┐  │
│  │  Servicio   │  │  Servicio   │  │  Servicio        │  │
│  │   Dólar     │  │   Clima     │  │   Favoritos      │  │
│  └─────────────┘  └─────────────┘  └───────────────────┘  │
│         │              │                      │            │
│    Bluelytics API  OpenWeatherMap         JSON File        │
│                     (con API Key)        (favorites.json)  │
└─────────────────────────────────────────────────────────────┘
```

## Referencia de Archivos de Contexto

Este proyecto utiliza un sistema de documentación modular para mantener el contexto del desarrollo:

1. **`context-ai.md`** - (Este archivo) Documento principal de diseño por IA
2. **`context-library.md`** - Diccionario completo de endpoints, variables, formatos y estructuras
3. **`context-code.md`** - Arquitectura detallada, algoritmos y estructuras de código
4. **`context-memory.md`** - Historial de cambios, problemas resueltos y decisiones técnicas
5. **`context-rta1.md`** - Información adicional y notas misceláneas

---

## Estructura de Archivos del Proyecto

```
landing-page/
├── context-ai.md              # Documento principal de diseño
├── context-library.md         # Diccionario de referencia
├── context-code.md           # Arquitectura y algoritmos
├── context-memory.md         # Historial de cambios
├── context-rta1.md           # Notas adicionales
├── README.md                 # Documentación de usuario
├── backend/
│   ├── app.py                # Aplicación Flask principal
│   ├── config.py             # Configuración del backend
│   ├── requirements.txt      # Dependencias Python
│   ├── services/
│   │   ├── __init__.py
│   │   ├── dolar.py         # Servicio de datos de dólar
│   │   ├── weather.py       # Servicio de datos climáticos
│   │   └── favorites.py     # Servicio de gestión de favoritos
│   └── __pycache__/
├── frontend/
│   ├── index.html           # HTML principal
│   ├── css/
│   │   └── styles.css       # Estilos CSS (tema claro/oscuro)
│   └── js/
│       └── app.js           # Lógica JavaScript principal
├── favorites/
│   ├── favorites.json       # Base de datos JSON de favoritos
│   └── logos/               # Logos descargados de sitios web
└── venv/                    # Entorno virtual Python
```

---

## Características Principales

### 1. Panel de Divisas en Tiempo Real
- **Euro Oficial** - Cotización actual del Euro
- **Dólar Oficial** - Cotización oficial del Banco Central
- **Dólar Blue** - Cotización del mercado paralelo
- **Brecha Euro vs Dólar** - Diferencia porcentual entre Euro y Dólar oficial
- **Actualización automática** cada 5 minutos
- **Formato argentino** de números con `Intl.NumberFormat('es-AR')`

### 2. Panel Climático
- Temperatura actual y sensación térmica en Celsius
- Humedad y descripción del clima en español
- Iconos dinámicos según condiciones climáticas
- Datos en tiempo real de OpenWeatherMap
- **Graceful degradation** si no hay API key configurada

### 3. Sistema de Favoritos y Tareas Pendientes
- **Dos categorías:** "Favoritos" y "Tareas Pendientes"
- **Formulario inteligente** con scraping automático de logos
- **Cards clickeables** (toda la tarjeta abre el sitio excepto el botón basurero)
- **Layout separado:** Tareas Pendientes (arriba), divisorio, Favoritos (abajo)
- **Gestión completa:** Agregar, visualizar, eliminar
- **Backward compatibility** para favoritos existentes

### 4. Interfaz de Usuario
- **Tema claro/oscuro** con persistencia en localStorage
- **Diseño responsive** (escritorio, tablet, móvil)
- **Layout de dos columnas** en escritorio
- **Animaciones suaves** y efectos hover
- **Accesibilidad** con soporte de teclado (Enter/Space)

---

## Variables de Configuración (config.py)

| Variable | Valor Default | Descripción |
|----------|---------------|-------------|
| `DOLAR_API_URL` | `https://api.bluelytics.com.ar/v2/latest` | API de cotizaciones de dólar |
| `WEATHER_API_URL` | `https://api.openweathermap.org/data/2.5/weather` | API de datos climáticos |
| `WEATHER_CITY` | `Córdoba` | Ciudad para consulta climática |
| `WEATHER_API_KEY` | (vacío) | API Key de OpenWeatherMap (requerida) |
| `UPDATE_INTERVAL` | `300` | Segundos entre actualizaciones automáticas |
| `FLASK_HOST` | `127.0.0.1` | Host del servidor Flask |
| `FLASK_PORT` | `5000` | Puerto del servidor Flask |
| `ENABLE_CORS` | `True` | Habilitar CORS para desarrollo |

**Nota:** Todas las variables pueden ser sobrescritas por variables de entorno.

---

## Contratos de Datos JSON

### 1. Endpoint: `GET /api/data`
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

### 2. Endpoint: `GET /api/favorites`
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

### 3. Endpoint: `POST /api/favorites`
**Request:**
```json
{
  "url": "https://ejemplo.com",
  "title": "Título opcional",
  "tipo": "favorito"  // o "tarea_pendiente"
}
```

**Response (201 Created):**
```json
{
  "id": "20260311130959",
  "url": "https://ejemplo.com",
  "title": "Ejemplo",
  "domain": "ejemplo.com",
  "logo": "ejemplo.com_20260311_130958.ico",
  "tipo": "favorito",
  "created_at": "2026-03-11T13:09:59.109372"
}
```

### 4. Endpoint: `DELETE /api/favorites/{id}`
**Response (200 OK):**
```json
{
  "success": true
}
```

---

## Instrucciones por Agente

### AGENTE: Sisyphus (Orquestador Principal)
**Rol:** Coordinación, delegación y control de calidad

**Responsabilidades:**
1. Analizar solicitudes del usuario y clasificar intención
2. Delegar tareas a agentes especializados según dominio
3. Verificar resultados y garantizar calidad
4. Mantener documentación actualizada
5. Gestionar tareas en paralelo para máxima eficiencia

**Reglas de Operación:**
- **NUNCA implementar directamente** cuando se pueden delegar agentes especializados
- **SIEMPRE crear TODOs** para tareas no triviales
- **PARALELIZAR** búsquedas, lecturas y agentes independientes
- **VERIFICAR** resultados antes de marcar como completado
- **CONSULTAR Oracle** para decisiones arquitectónicas complejas

### AGENTE: Hephaestus (Implementación Backend)
**Rol:** Desarrollo de servicios backend y lógica de negocio

**Tareas Típicas:**
1. Implementar endpoints Flask nuevos
2. Modificar servicios existentes (dolar.py, weather.py, favorites.py)
3. Manejar migraciones de datos y backward compatibility
4. Optimizar performance y manejo de errores

**Consideraciones:**
- Usar `logging` para registro de eventos
- Implementar timeout en llamadas HTTP externas
- Validar entradas del usuario
- Manejar errores con `try/except` apropiados

### AGENTE: Artistry (Implementación Frontend)
**Rol:** Desarrollo de interfaz de usuario y experiencia

**Tareas Típicas:**
1. Modificar HTML/CSS/JavaScript del frontend
2. Implementar nuevas funcionalidades de UI
3. Mejorar responsive design y accesibilidad
4. Optimizar performance del lado del cliente

**Restricciones:**
- ✅ Vanilla JavaScript puro (sin frameworks)
- ✅ `.then()` en lugar de `async/await` complejo
- ✅ `Intl.NumberFormat('es-AR')` para formateo numérico
- ✅ `toLocaleDateString('es-AR')` para fechas
- ❌ No usar `as any`, `@ts-ignore`, `@ts-expect-error`
- ❌ No suprimir errores de tipo TypeScript

### AGENTE: Visual-Engineering (Diseño UI/UX)
**Rol:** Diseño visual, estilos CSS, layout y animaciones

**Tareas Típicas:**
1. Crear o modificar estilos CSS
2. Implementar temas claro/oscuro
3. Diseñar layouts responsive
4. Crear animaciones y transiciones

**Habilidades Disponibles:**
- `frontend-ui-ux`: Diseñador-desarrollador para UI/UX de alta calidad

### AGENTE: Oracle (Consultor de Arquitectura)
**Rol:** Consultoría read-only para problemas complejos

**Cuándo Usar:**
- Decisiones arquitectónicas complejas
- Revisión de implementaciones importantes
- 2+ intentos fallidos de solución
- Preocupaciones de seguridad/performance

**Cuándo NO Usar:**
- Operaciones simples de archivos
- Primer intento de cualquier solución
- Decisiones triviales de nombrado/formato

### AGENTE: Explore (Búsqueda Contextual)
**Rol:** Búsqueda grep contextual en el codebase

**Cuándo Usar:**
- Encontrar patrones en el código existente
- Descubrir estructura de módulos desconocidos
- Búsqueda de implementaciones específicas

**Ejemplo:**
```python
task(subagent_type="explore", run_in_background=true, 
     description="Buscar implementaciones de autenticación",
     prompt="Encontrar middleware de auth, handlers de login, generación de tokens")
```

### AGENTE: Librarian (Búsqueda de Referencias)
**Rol:** Búsqueda en documentación externa y ejemplos OSS

**Cuándo Usar:**
- Documentación de librerías externas
- Ejemplos de implementación en GitHub
- Mejores prácticas para frameworks

**Ejemplo:**
```python
task(subagent_type="librarian", run_in_background=true,
     description="Buscar documentación de JWT",
     prompt="Encontrar guías de seguridad OWASP para JWT, patrones de Express para auth")
```

---

## Comandos de Ejecución

### 1. Configurar entorno (Windows PowerShell)
```powershell
# Navegar al directorio del proyecto
cd landing-page

# Crear y activar entorno virtual
python -m venv venv
.\venv\Scripts\Activate.ps1

# Instalar dependencias
cd backend
pip install -r requirements.txt

# Configurar API Key de clima (opcional)
$env:WEATHER_API_KEY="tu_api_key_aquí"
```

### 2. Ejecutar servidor backend
```bash
# Método 1: Directo
cd backend
python app.py

# Método 2: Con variables de entorno
$env:FLASK_PORT=5000; $env:WEATHER_API_KEY="tu_key"; python app.py

# Método 3: Usar script PowerShell
.\start_flask.ps1
```

### 3. Acceder a la aplicación
- **URL:** `http://localhost:5000`
- **API Endpoint:** `http://localhost:5000/api/data`
- **Favoritos API:** `http://localhost:5000/api/favorites`

---

## Reglas de Desarrollo (NO VIOLAR)

### Reglas Estrictas
1. **✅ Validación de tipos:** Nunca usar `as any`, `@ts-ignore`, `@ts-expect-error`
2. **✅ Manejo de errores:** Nunca usar bloques `catch` vacíos
3. **✅ Commits:** Solo cuando el usuario lo solicite explícitamente
4. **✅ Backward compatibility:** Siempre mantener compatibilidad con datos existentes
5. **✅ Delegación:** Siempre delegar a agentes especializados en lugar de implementar directamente

### Patrones de Diseño
1. **Formato numérico:** `Intl.NumberFormat('es-AR')` para montos en pesos
2. **Formato de fecha:** `toLocaleDateString('es-AR')` para fechas
3. **Temas:** CSS Variables para tema claro/oscuro con `data-theme` attribute
4. **Responsive:** Mobile-first con media queries
5. **Accesibilidad:** Atributos `role`, `aria-label`, soporte de teclado

### Flujo de Trabajo Sisyphus
1. **Fase 0:** Verbalizar intención y clasificar solicitud
2. **Fase 1:** Evaluar codebase (disciplinado vs caótico)
3. **Fase 2A:** Exploración/investigación (agentes paralelos)
4. **Fase 2B:** Implementación (delegar, no implementar directamente)
5. **Fase 3:** Verificación y entrega

---

## Fuentes de Datos Externas

| Fuente | URL | Autenticación | Uso |
|--------|-----|---------------|-----|
| Bluelytics | `https://api.bluelytics.com.ar/v2/latest` | No | Cotizaciones de dólar oficial, blue y euro |
| OpenWeatherMap | `https://openweathermap.org/api` | Sí (gratuita) | Datos climáticos en tiempo real |

---

## Prioridades de Desarrollo

### Alta Prioridad (Core Functionality)
1. ✅ Panel de divisas funcional con datos reales
2. ✅ Panel climático con graceful degradation
3. ✅ Sistema de favoritos con scraping de logos
4. ✅ Separación Favoritos/Tareas Pendientes
5. ✅ Tema claro/oscuro con persistencia

### Media Prioridad (UX Improvements)
1. ✅ Cards clickeables completas (excepto basurero)
2. ✅ Layout responsive (mobile, tablet, desktop)
3. ✅ Animaciones suaves y feedback visual
4. ✅ Validación de formularios en tiempo real
5. ✅ Manejo de errores robusto

### Baja Prioridad (Enhancements)
1. Exportación de datos (JSON/CSV)
2. Categorías adicionales para favoritos
3. Búsqueda y filtrado de favoritos
4. Estadísticas de uso
5. Notificaciones push para cambios de cotización

---

## Notas de Diseño

### Interfaz Visual
- **Paleta de colores:** Azul corporativo para finanzas, naranja para clima, rosa para favoritos
- **Tipografía:** Inter de Google Fonts para legibilidad
- **Espaciado:** Sistema de espaciado consistente (--spacing-xs, --spacing-sm, etc.)
- **Sombras:** Sistema de sombras para jerarquía visual

### Experiencia de Usuario
- **Feedback inmediato** al agregar/eliminar favoritos
- **Estado de carga** visible durante operaciones
- **Mensajes de error** claros y accionables
- **Persistencia** de preferencias en localStorage

### Performance
- **Cache de logos** local para reducir requests
- **Lazy loading** potencial para imágenes
- **Minificación** manual de recursos
- **Compresión** gzip en servidor

---

## Problemas Conocidos y Soluciones

### 1. SSL Certificate Verification (Windows)
**Problema:** `SSLCertVerificationError` al scrapear algunos sitios
**Solución Actual:** Try/catch con fallback a favorito sin logo
**Solución Ideal:** Configurar certificados SSL del sistema

### 2. Rate Limiting de APIs Externas
**Problema:** Bluelytics/OpenWeatherMap pueden tener limits
**Solución:** Cache de respuestas por 1-5 minutos

### 3. Logos No Disponibles
**Problema:** Algunos sitios bloquean scraping de logos
**Solución:** Fallback a favicon.ico, luego placeholder genérico

---

## Roadmap de Desarrollo

### Fase 1: Core MVP ✅
- [x] Divisas en tiempo real
- [x] Datos climáticos  
- [x] Sistema básico de favoritos
- [x] Interfaz responsive

### Fase 2: Categorización ✅
- [x] Separación Favoritos/Tareas Pendientes
- [x] Formulario con selector de tipo
- [x] Visualización por secciones
- [x] Backward compatibility

### Fase 3: Optimización (En Progreso)
- [ ] Cache de logos offline
- [ ] Mejora de performance
- [ ] Testing automatizado
- [ ] Documentación completa

### Fase 4: Features Avanzados (Futuro)
- [ ] Exportación de datos
- [ ] Búsqueda y filtrado
- [ ] Estadísticas
- [ ] Notificaciones

---

## Contacto y Soporte

- **Documentación:** `README.md` para usuarios finales
- **Contexto Técnico:** Archivos `context-*.md` para desarrolladores
- **Backup:** Los archivos de contexto deben mantenerse con el proyecto
- **Recuperación:** En caso de reinstalación, leer `context-ai.md` primero

---

*Última actualización: 11 de marzo de 2026 - Versión 2.0 (con sistema de favoritos y categorización)*