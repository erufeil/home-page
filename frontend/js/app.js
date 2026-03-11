/**
 * Aplicación principal para landing page de dólar y clima.
 * Vanilla JavaScript puro, sin frameworks.
 */

// Configuración
const API_URL = '/api/data';
let updateInterval = 300000; // 5 minutos por defecto (en ms)
let currentTheme = localStorage.getItem('theme') || 'light';
let refreshTimer = null;

// Formateadores
const numberFormatter = new Intl.NumberFormat('es-AR', {
    style: 'currency',
    currency: 'ARS',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
});

const dateFormatter = new Intl.DateTimeFormat('es-AR', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
});

// Elementos del DOM
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

// Inicialización
function init() {
    applyTheme();
    setupEventListeners();
    loadData();
    startAutoRefresh();
}

// Aplicar tema (claro/oscuro)
function applyTheme() {
    document.documentElement.setAttribute('data-theme', currentTheme);
    
    const icon = elements.themeToggle.querySelector('i');
    const text = elements.themeToggle.querySelector('span');
    
    if (currentTheme === 'dark') {
        icon.className = 'fas fa-sun';
        text.textContent = 'Modo claro';
    } else {
        icon.className = 'fas fa-moon';
        text.textContent = 'Modo oscuro';
    }
}

// Configurar event listeners
function setupEventListeners() {
    // Toggle tema
    elements.themeToggle.addEventListener('click', function() {
        currentTheme = currentTheme === 'light' ? 'dark' : 'light';
        localStorage.setItem('theme', currentTheme);
        applyTheme();
    });
    
    // Botón refrescar manual
    elements.refreshBtn.addEventListener('click', function() {
        loadData(true);
    });
    
    // Botón agregar favorito
    elements.addFavoriteBtn.addEventListener('click', addFavorite);
    
    // Enter en el input de URL
    elements.urlInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            addFavorite();
        }
    });
}

// Cargar datos desde API
function loadData(manualRefresh = false) {
    if (manualRefresh) {
        elements.refreshBtn.classList.add('refreshing');
    }
    
    fetch(API_URL)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            updateUI(data);
            if (manualRefresh) {
                elements.refreshBtn.classList.remove('refreshing');
            }
            hideError();
        })
        .catch(error => {
            console.error('Error al cargar datos:', error);
            showError('No se pudieron cargar los datos. Verifica que el servidor esté corriendo.');
            if (manualRefresh) {
                elements.refreshBtn.classList.remove('refreshing');
            }
        });
}

// Actualizar interfaz con datos recibidos
function updateUI(data) {
    // Actualizar intervalo de actualización
    updateInterval = (data.update_interval || 300) * 1000;
    elements.updateInterval.textContent = Math.floor(updateInterval / 60000);
    
    // Actualizar divisas
    const dolar = data.dolar;
    if (dolar) {
        elements.euroCompra.textContent = numberFormatter.format(dolar.euro_oficial.compra);
        elements.euroVenta.textContent = numberFormatter.format(dolar.euro_oficial.venta);
        
        elements.oficialCompra.textContent = numberFormatter.format(dolar.dolar_oficial.compra);
        elements.oficialVenta.textContent = numberFormatter.format(dolar.dolar_oficial.venta);
        
        elements.blueCompra.textContent = numberFormatter.format(dolar.dolar_blue.compra);
        elements.blueVenta.textContent = numberFormatter.format(dolar.dolar_blue.venta);
        
        elements.brecha.textContent = `${dolar.brecha.toFixed(2)} %`;
        
        // Color de brecha
        if (dolar.brecha > 10) {
            elements.brecha.style.color = 'var(--danger-color)';
        } else if (dolar.brecha > 5) {
            elements.brecha.style.color = 'var(--warning-color)';
        } else {
            elements.brecha.style.color = 'var(--accent-color)';
        }
        
        // Formatear fecha de actualización
        if (dolar.ultima_actualizacion) {
            const date = new Date(dolar.ultima_actualizacion);
            elements.dolarUpdateTime.textContent = dateFormatter.format(date);
        } else {
            elements.dolarUpdateTime.textContent = '--:--:--';
        }
    }
    
    // Actualizar clima
    const clima = data.clima;
    if (clima) {
        elements.ciudadClima.textContent = clima.ciudad;
        elements.temperatura.textContent = clima.temperatura.toFixed(1);
        elements.sensacion.textContent = clima.sensacion.toFixed(1);
        elements.humedad.textContent = clima.humedad;
        elements.descripcionClima.textContent = clima.descripcion;
        
        // Icono del clima (usando FontAwesome)
        updateWeatherIcon(clima.icono);
    }
    
    // Actualizar timestamp completo
    const timestamp = new Date(data.timestamp);
    elements.fullUpdateTime.textContent = dateFormatter.format(timestamp);
}

// Actualizar icono del clima según código de OpenWeatherMap
function updateWeatherIcon(iconCode) {
    const iconMap = {
        '01d': 'fas fa-sun',           // clear sky day
        '01n': 'fas fa-moon',          // clear sky night
        '02d': 'fas fa-cloud-sun',     // few clouds day
        '02n': 'fas fa-cloud-moon',    // few clouds night
        '03d': 'fas fa-cloud',         // scattered clouds
        '03n': 'fas fa-cloud',
        '04d': 'fas fa-cloud',         // broken clouds
        '04n': 'fas fa-cloud',
        '09d': 'fas fa-cloud-rain',    // shower rain
        '09n': 'fas fa-cloud-rain',
        '10d': 'fas fa-cloud-sun-rain',// rain day
        '10n': 'fas fa-cloud-moon-rain',// rain night
        '11d': 'fas fa-bolt',          // thunderstorm
        '11n': 'fas fa-bolt',
        '13d': 'fas fa-snowflake',     // snow
        '13n': 'fas fa-snowflake',
        '50d': 'fas fa-smog',          // mist
        '50n': 'fas fa-smog'
    };
    
    const iconClass = iconMap[iconCode] || 'fas fa-question';
    elements.weatherIcon.innerHTML = `<i class="${iconClass}"></i>`;
    
    // Color según clima
    if (iconCode.includes('01') || iconCode.includes('02')) {
        elements.weatherIcon.style.color = 'var(--warning-color)';
    } else if (iconCode.includes('09') || iconCode.includes('10') || iconCode.includes('11')) {
        elements.weatherIcon.style.color = 'var(--primary-color)';
    } else {
        elements.weatherIcon.style.color = 'var(--text-secondary)';
    }
}

// Mostrar mensaje de error
function showError(message) {
    if (elements.errorMessage) {
        elements.errorMessage.textContent = message;
        elements.errorMessage.classList.add('show');
    }
}

// Ocultar mensaje de error
function hideError() {
    if (elements.errorMessage) {
        elements.errorMessage.classList.remove('show');
    }
}

// Iniciar auto-refresh
function startAutoRefresh() {
    if (refreshTimer) {
        clearInterval(refreshTimer);
    }
    
    refreshTimer = setInterval(() => {
        loadData();
    }, updateInterval);
    
    console.log(`Auto-refresh configurado cada ${updateInterval / 1000} segundos`);
}

// Funciones para favoritos
function addFavorite() {
    const url = elements.urlInput.value.trim();
    const title = elements.titleInput.value.trim();
    const tipo = elements.typeInput.value;
    
    if (!url) {
        showFavoriteStatus('Por favor ingresa una URL', 'error');
        return;
    }
    
    // Validar URL
    try {
        new URL(url);
    } catch {
        showFavoriteStatus('URL inválida', 'error');
        return;
    }
    
    // Deshabilitar botón mientras se procesa
    elements.addFavoriteBtn.disabled = true;
    elements.addFavoriteBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Procesando...';
    
    // Enviar al backend
    fetch('/api/favorites', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url, title: title || null, tipo })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error del servidor');
        }
        return response.json();
    })
    .then(favorite => {
        showFavoriteStatus('¡Sitio guardado!', 'success');
        elements.urlInput.value = '';
        elements.titleInput.value = '';
        loadFavorites();
    })
    .catch(error => {
        console.error('Error agregando favorito:', error);
        showFavoriteStatus('Error al agregar favorito', 'error');
    })
    .finally(() => {
        elements.addFavoriteBtn.disabled = false;
        elements.addFavoriteBtn.innerHTML = '<i class="fas fa-bookmark"></i> Agregar a Favoritos';
    });
}

function showFavoriteStatus(message, type) {
    elements.favoriteStatus.textContent = message;
    elements.favoriteStatus.className = 'favorite-status ' + type;
    
    // Ocultar después de 5 segundos
    setTimeout(() => {
        elements.favoriteStatus.textContent = '';
        elements.favoriteStatus.className = 'favorite-status';
    }, 5000);
}

function loadFavorites() {
    fetch('/api/favorites')
        .then(response => response.json())
        .then(favorites => {
            updateFavoritesCount(favorites.length);
            renderFavorites(favorites);
        })
        .catch(error => {
            console.error('Error cargando favoritos:', error);
        });
}

function updateFavoritesCount(count) {
    elements.favoritesCount.textContent = count;
    
    // Actualizar también en el panel de información
    const infoCount = document.querySelector('#favoritesCount');
    if (infoCount) {
        infoCount.textContent = count;
    }
}

function renderFavorites(favorites) {
    if (favorites.length === 0) {
        elements.favoritesPlaceholder.style.display = 'flex';
        elements.favoritesContainer.innerHTML = '';
        return;
    }
    
    elements.favoritesPlaceholder.style.display = 'none';
    
    const favoritesGrid = document.createElement('div');
    favoritesGrid.className = 'favorites-grid';
    
    favorites.forEach(favorite => {
        const favoriteCard = createFavoriteCard(favorite);
        favoritesGrid.appendChild(favoriteCard);
    });
    
    elements.favoritesContainer.innerHTML = '';
    elements.favoritesContainer.appendChild(favoritesGrid);
}

function createFavoriteCard(favorite) {
    const card = document.createElement('div');
    card.className = 'favorite-card';
    card.dataset.id = favorite.id;
    card.setAttribute('role', 'button');
    card.setAttribute('tabindex', '0');
    card.setAttribute('aria-label', `Visitar ${favorite.title}`);
    
    // Logo
    if (favorite.logo) {
        const logo = document.createElement('img');
        logo.className = 'favorite-logo';
        logo.src = `/favorites/logos/${favorite.logo}`;
        logo.alt = `${favorite.title} logo`;
        logo.onerror = function() {
            this.style.display = 'none';
            const placeholder = document.createElement('div');
            placeholder.className = 'favorite-logo-placeholder';
            placeholder.innerHTML = '<i class="fas fa-globe"></i>';
            card.insertBefore(placeholder, card.firstChild);
        };
        card.appendChild(logo);
    } else {
        const placeholder = document.createElement('div');
        placeholder.className = 'favorite-logo-placeholder';
        placeholder.innerHTML = '<i class="fas fa-globe"></i>';
        card.appendChild(placeholder);
    }
    
    // Título
    const title = document.createElement('div');
    title.className = 'favorite-title';
    title.textContent = favorite.title;
    card.appendChild(title);
    
    // Dominio y botón eliminar en misma línea
    const domainRow = document.createElement('div');
    domainRow.className = 'favorite-domain-row';
    
    const domain = document.createElement('div');
    domain.className = 'favorite-domain';
    domain.textContent = favorite.domain;
    domainRow.appendChild(domain);
    
    const deleteBtn = document.createElement('button');
    deleteBtn.className = 'btn-delete-favorite';
    deleteBtn.title = 'Eliminar favorito';
    deleteBtn.innerHTML = '<i class="fas fa-trash"></i>';
    deleteBtn.onclick = function(e) {
        e.preventDefault();
        e.stopPropagation();
        deleteFavorite(favorite.id);
    };
    domainRow.appendChild(deleteBtn);
    
    card.appendChild(domainRow);
    
    // Hacer toda la tarjeta clicable (excepto el botón basurero)
    card.addEventListener('click', function(e) {
        // Evitar que el click en el botón basurero active este evento
        if (e.target.closest('.btn-delete-favorite')) {
            return;
        }
        window.open(favorite.url, '_blank', 'noopener,noreferrer');
    });
    
    // Soporte para teclado (Enter/Space)
    card.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            window.open(favorite.url, '_blank', 'noopener,noreferrer');
        }
    });
    
    return card;
}

function deleteFavorite(favoriteId) {
    if (!confirm('¿Estás seguro de que quieres eliminar este favorito?')) {
        return;
    }
    
    fetch(`/api/favorites/${favoriteId}`, {
        method: 'DELETE'
    })
    .then(response => {
        if (response.ok) {
            loadFavorites();
            showFavoriteStatus('Favorito eliminado', 'success');
        } else {
            throw new Error('Error eliminando favorito');
        }
    })
    .catch(error => {
        console.error('Error eliminando favorito:', error);
        showFavoriteStatus('Error al eliminar favorito', 'error');
    });
}

// Inicialización
function init() {
    applyTheme();
    setupEventListeners();
    loadData();
    loadFavorites();
    startAutoRefresh();
}

// Iniciar aplicación cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}