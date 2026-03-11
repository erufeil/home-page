# 🌐 Landing Page Dólar + Clima + Favoritos

Una aplicación web completa que muestra en tiempo real:
- **Cotizaciones de divisas** (Euro Oficial, Dólar Oficial, Dólar Blue)
- **Condiciones climáticas** de Córdoba, Argentina
- **Gestión de sitios web favoritos** con scraping automático de logos

## 🚀 Características Principales

### 💱 Panel de Divisas
- **Euro Oficial** - Cotización actual del Euro
- **Dólar Oficial** - Cotización oficial del Banco Central
- **Dólar Blue** - Cotización del mercado paralelo
- **Brecha Euro vs Dólar** - Diferencia porcentual entre Euro y Dólar oficial

### 🌤️ Panel Climático
- Temperatura actual y sensación térmica
- Humedad y descripción del clima
- Iconos dinámicos según condiciones climáticas
- Datos en tiempo real de OpenWeatherMap

### ⭐ Sistema de Favoritos
- **Agregar sitios web** desde el panel lateral
- **Scraping automático** de logos (favicon, og:image, logos en HTML)
- **Visualización en grid** en el área central
- **Gestión completa** (agregar, ver, eliminar)
- **Persistencia** de datos en archivo JSON

### 🎨 Interfaz de Usuario
- **Diseño responsive** (escritorio y móvil)
- **Tema claro/oscuro** con persistencia
- **Actualización automática** cada 5 minutos
- **Animaciones suaves** y efectos hover
- **Layout de dos columnas** (área principal + sidebar)

## 📋 Requisitos Previos

- **Python 3.8+**
- **Git** (opcional, para clonar el repositorio)
- **Conexión a Internet** (para APIs externas)

## 🛠️ Instalación y Configuración

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd landing-page
```

### 2. Crear y activar entorno virtual

#### Windows (PowerShell):
```powershell
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
.\venv\Scripts\Activate.ps1

# Si aparece un error de ejecución de scripts, ejecutar primero:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Windows (CMD):
```cmd
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
venv\Scripts\activate
```

#### macOS/Linux:
```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
# Navegar al directorio backend
cd backend

# Instalar paquetes requeridos
pip install -r requirements.txt
```

### 4. Configurar API Key de OpenWeatherMap (Opcional)

Para obtener datos climáticos, necesitas una API key gratuita de [OpenWeatherMap](https://openweathermap.org/api):

1. Regístrate en [OpenWeatherMap](https://home.openweathermap.org/users/sign_up)
2. Genera una API key en tu panel de control
3. Configura la variable de entorno:

#### Windows (PowerShell):
```powershell
$env:WEATHER_API_KEY="tu_api_key_aquí"
```

#### Windows (CMD):
```cmd
set WEATHER_API_KEY=tu_api_key_aquí
```

#### macOS/Linux:
```bash
export WEATHER_API_KEY="tu_api_key_aquí"
```

**Nota**: Si no configuras la API key, la aplicación funcionará pero no mostrará datos climáticos.

## 🚀 Ejecutar la Aplicación

### Método 1: Ejecución directa
```bash
# Asegúrate de estar en el directorio backend
cd backend

# Ejecutar la aplicación
python app.py
```

### Método 2: Usar el script de inicio (Windows)
```powershell
# Desde la raíz del proyecto
.\start_flask.ps1
```

### Método 3: Ejecutar con variables de entorno
```bash
# Windows (PowerShell)
$env:FLASK_PORT=5000; $env:WEATHER_API_KEY="tu_key"; cd backend; python app.py

# macOS/Linux
FLASK_PORT=5000 WEATHER_API_KEY="tu_key" python backend/app.py
```

## 🌐 Acceder a la Aplicación

Una vez que el servidor esté corriendo:

1. **Abre tu navegador web**
2. **Ve a**: `http://localhost:5000`
3. **¡Listo!** La aplicación debería estar funcionando

### Verificación del servidor
```bash
# Verificar que el servidor responde
curl http://localhost:5000/api/data
```

## ⚙️ Configuración Avanzada

### Variables de Entorno

Puedes personalizar la aplicación mediante variables de entorno:

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `FLASK_PORT` | Puerto del servidor Flask | `5000` |
| `FLASK_HOST` | Host del servidor | `127.0.0.1` |
| `WEATHER_API_KEY` | API Key de OpenWeatherMap | (requerida para clima) |
| `WEATHER_CITY` | Ciudad para clima | `Córdoba` |
| `UPDATE_INTERVAL` | Intervalo de actualización (segundos) | `300` (5 minutos) |
| `ENABLE_CORS` | Habilitar CORS para desarrollo | `True` |

### Ejemplo de configuración completa:
```bash
# Windows PowerShell
$env:FLASK_PORT=8080
$env:FLASK_HOST="0.0.0.0"
$env:WEATHER_API_KEY="tu_api_key_aquí"
$env:WEATHER_CITY="Buenos Aires"
$env:UPDATE_INTERVAL=60
cd backend
python app.py
```

## 📁 Estructura del Proyecto

```
landing-page/
├── backend/                    # Aplicación Flask
│   ├── app.py                 # Aplicación principal
│   ├── config.py              # Configuración
│   ├── requirements.txt       # Dependencias Python
│   └── services/              # Servicios de datos
│       ├── dolar.py          # API de divisas
│       ├── weather.py        # API de clima
│       └── favorites.py      # Gestión de favoritos
├── frontend/                  # Interfaz web
│   ├── index.html            # HTML principal
│   ├── css/
│   │   └── styles.css        # Estilos CSS
│   └── js/
│       └── app.js            # JavaScript principal
├── favorites/                 # Datos de favoritos
│   ├── favorites.json        # Base de datos JSON
│   └── logos/                # Logos descargados
├── README.md                 # Este archivo
└── start_flask.ps1          # Script de inicio (Windows)
```

## 🔧 Solución de Problemas

### Problema: "No se pueden obtener datos de clima"
**Solución**: Verifica que hayas configurado correctamente la variable `WEATHER_API_KEY`

### Problema: "El servidor no inicia"
**Solución**:
1. Verifica que Python 3.8+ esté instalado: `python --version`
2. Verifica que las dependencias estén instaladas: `pip list`
3. Verifica que no haya otro proceso usando el puerto 5000

### Problema: "Error al agregar favorito"
**Solución**:
1. Verifica que la URL sea válida y accesible
2. Verifica que tengas conexión a Internet
3. Revisa la consola del servidor para mensajes de error detallados

### Problema: "Los logos no se muestran"
**Solución**:
1. Verifica que el directorio `favorites/logos/` tenga permisos de escritura
2. Algunos sitios pueden bloquear el scraping de logos

## 🧪 Pruebas

### Probar la API de divisas:
```bash
curl http://localhost:5000/api/data | python -m json.tool
```

### Probar el sistema de favoritos:
```bash
# Agregar un favorito
curl -X POST http://localhost:5000/api/favorites \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com", "title": "GitHub"}'

# Listar favoritos
curl http://localhost:5000/api/favorites

# Eliminar favorito (reemplaza <id> con el ID real)
curl -X DELETE http://localhost:5000/api/favorites/<id>
```

## 🔄 Actualización Automática

La aplicación incluye:
- **Actualización automática** cada 5 minutos
- **Botón de refresco manual** en la interfaz
- **Timestamp** de última actualización

## 📱 Responsive Design

La aplicación se adapta a:
- **Escritorio** (layout de dos columnas)
- **Tablet** (layout adaptable)
- **Móvil** (una sola columna)

## 🔒 Seguridad

- **Validación de URLs** antes de procesar
- **Sanitización de entradas** del usuario
- **Enlaces externos** con `rel="noopener noreferrer"`
- **CORS configurable** para desarrollo

## 🤝 Contribuir

1. Fork el repositorio
2. Crea una rama para tu feature: `git checkout -b mi-nueva-feature`
3. Commit tus cambios: `git commit -am 'Agrega nueva feature'`
4. Push a la rama: `git push origin mi-nueva-feature`
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🙏 Créditos

- **Datos de divisas**: [Bluelytics API](https://bluelytics.com.ar/)
- **Datos climáticos**: [OpenWeatherMap](https://openweathermap.org/)
- **Iconos**: [Font Awesome](https://fontawesome.com/)
- **Fuentes**: [Google Fonts - Inter](https://fonts.google.com/specimen/Inter)

## 📞 Soporte

Si encuentras problemas o tienes preguntas:
1. Revisa la sección de [Solución de Problemas](#-solución-de-problemas)
2. Abre un issue en el repositorio
3. Contacta al mantenedor del proyecto

---

**¡Disfruta de tu landing page personalizada!** 🎉

*Última actualización: Marzo 2026*