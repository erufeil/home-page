/**
 * Aplicación principal para landing page de dólar y clima.
 * Vanilla JavaScript puro, sin frameworks.
 */

// Configuración
const API_URL = '/api/data';
let updateInterval = 300000; // 5 minutos por defecto (en ms)
let currentTheme = localStorage.getItem('theme') || 'light';
let refreshTimer = null;
let currentUser = null;

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
    categoryInput: document.getElementById('categoryInput'),
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
    const categoryId = elements.categoryInput.value.trim();

    if (!url) {
        showFavoriteStatus('Por favor ingresa una URL', 'error');
        return;
    }

    try {
        new URL(url);
    } catch {
        showFavoriteStatus('URL inválida', 'error');
        return;
    }

    elements.addFavoriteBtn.disabled = true;
    elements.addFavoriteBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Procesando...';

    fetch('/api/v2/favorites', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            url,
            title: title || null,
            category_id: categoryId || null
        })
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
    fetch('/api/v2/favorites')
        .then(response => {
            if (response.status === 401) {
                showLoginModal();
                return null;
            }
            if (!response.ok) throw new Error('Error cargando favoritos');
            return response.json();
        })
        .then(data => {
            if (!data) return;
            const favorites = data.favorites || [];
            updateFavoritesCount(favorites.length);
            renderFavorites(favorites);
        })
        .catch(error => {
            console.error('Error cargando favoritos:', error);
        });
}

function loadCategories() {
    fetch('/api/categories')
        .then(response => {
            if (response.status === 401) {
                showLoginModal();
                return null;
            }
            if (!response.ok) throw new Error('Error cargando categorías');
            return response.json();
        })
        .then(data => {
            if (!data) return;
            populateCategories(data.categories || []);
        })
        .catch(error => {
            console.error('Error cargando categorías:', error);
        });
}

function initSortableGrids() {
    const grids = document.querySelectorAll('.favorites-grid');
    grids.forEach(grid => {
        new Sortable(grid, {
            group: 'favorites',
            animation: 150,
            ghostClass: 'sortable-ghost',
            onEnd: function(evt) {
                const destGrid = evt.to;
                const categoryId = destGrid.dataset.categoryId
                    ? parseInt(destGrid.dataset.categoryId)
                    : null;
                const favoriteIds = Array.from(destGrid.children).map(c => parseInt(c.dataset.id));
                fetch('/api/v2/favorites/reorder', {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ favorite_ids: favoriteIds, category_id: categoryId })
                }).then(response => {
                    if (!response.ok) console.error('Failed to reorder favorites');
                }).catch(error => console.error('Error:', error));
            }
        });
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
    elements.favoritesContainer.innerHTML = '';

    // Agrupar por categoría (preservando el orden original)
    const grouped = new Map(); // categoryId -> { category, items[] }
    const uncategorized = [];

    favorites.forEach(fav => {
        if (fav.category) {
            const catId = fav.category.id;
            if (!grouped.has(catId)) {
                grouped.set(catId, { category: fav.category, items: [] });
            }
            grouped.get(catId).items.push(fav);
        } else {
            uncategorized.push(fav);
        }
    });

    function buildSection(label, color, items, categoryId) {
        const section = document.createElement('div');
        section.className = 'favorites-section';

        const header = document.createElement('h3');
        header.className = 'favorites-section-header';
        if (color) {
            const dot = document.createElement('span');
            dot.className = 'category-dot';
            dot.style.background = color;
            header.appendChild(dot);
            header.appendChild(document.createTextNode(` ${label} (${items.length})`));
        } else {
            header.textContent = `${label} (${items.length})`;
        }
        section.appendChild(header);

        const grid = document.createElement('div');
        grid.className = 'favorites-grid';
        if (categoryId) grid.dataset.categoryId = categoryId;
        items.forEach(fav => grid.appendChild(createFavoriteCard(fav)));
        section.appendChild(grid);
        return section;
    }

    grouped.forEach(({ category, items }) => {
        elements.favoritesContainer.appendChild(
            buildSection(category.name, category.color, items, category.id)
        );
    });

    if (uncategorized.length > 0) {
        elements.favoritesContainer.appendChild(
            buildSection('Sin categoría', null, uncategorized, null)
        );
    }

    initSortableGrids();
}

function createFavoriteCard(favorite) {
    const card = document.createElement('div');
    card.className = 'favorite-card';
    card.dataset.id = favorite.id;
    card.setAttribute('role', 'button');
    card.setAttribute('tabindex', '0');
    card.setAttribute('aria-label', `Visitar ${favorite.title}`);
    
    // Logo
    const logoFile = favorite.logo_filename || favorite.logo;
    if (logoFile) {
        const logo = document.createElement('img');
        logo.className = 'favorite-logo';
        logo.src = `/favorites/logos/${logoFile}`;
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

    // Categoría (si existe)
    if (favorite.category) {
        const categoryBadge = document.createElement('div');
        categoryBadge.className = 'favorite-category';
        categoryBadge.textContent = favorite.category.name;
        categoryBadge.style.backgroundColor = favorite.category.color;
        // Texto blanco para contraste
        categoryBadge.style.color = '#ffffff';
        categoryBadge.style.padding = '2px 8px';
        categoryBadge.style.borderRadius = '12px';
        categoryBadge.style.fontSize = '0.8em';
        categoryBadge.style.display = 'inline-block';
        categoryBadge.style.marginTop = '4px';
        card.appendChild(categoryBadge);
    }
    
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

// ===== Gestión de Categorías =====

function openCategoriesModal() {
    document.getElementById('categoriesModal').classList.remove('hidden');
    renderCategoriesList();
}

function closeCategoriesModal() {
    document.getElementById('categoriesModal').classList.add('hidden');
    document.getElementById('catStatus').classList.add('hidden');
    document.getElementById('newCatName').value = '';
}

function setCatStatus(msg, isError) {
    const el = document.getElementById('catStatus');
    el.textContent = msg;
    el.classList.remove('hidden');
    el.style.background = isError ? '#fee2e2' : '#d1fae5';
    el.style.color = isError ? 'var(--danger-color)' : 'var(--accent-color)';
    setTimeout(() => el.classList.add('hidden'), 3000);
}

function renderCategoriesList() {
    const list = document.getElementById('categoriesList');
    list.innerHTML = '<li style="color:var(--text-muted);font-size:.85rem">Cargando...</li>';

    fetch('/api/categories')
        .then(r => r.json())
        .then(data => {
            const cats = data.categories || [];
            list.innerHTML = '';
            if (cats.length === 0) {
                list.innerHTML = '<li style="color:var(--text-muted);font-size:.85rem">Sin categorías aún.</li>';
                return;
            }
            cats.forEach(cat => {
                const li = document.createElement('li');
                li.className = 'category-item';
                li.dataset.id = cat.id;

                const dot = document.createElement('span');
                dot.className = 'category-item-dot';
                dot.style.background = cat.color;

                const nameInput = document.createElement('input');
                nameInput.type = 'text';
                nameInput.className = 'category-item-name';
                nameInput.value = cat.name;

                const colorInput = document.createElement('input');
                colorInput.type = 'color';
                colorInput.className = 'category-item-color';
                colorInput.value = cat.color;
                colorInput.addEventListener('input', () => dot.style.background = colorInput.value);

                const saveBtn = document.createElement('button');
                saveBtn.type = 'button';
                saveBtn.className = 'btn-save-category';
                saveBtn.title = 'Guardar';
                saveBtn.innerHTML = '<i class="fas fa-check"></i>';
                saveBtn.onclick = () => updateCategory(cat.id, nameInput.value, colorInput.value);

                const delBtn = document.createElement('button');
                delBtn.type = 'button';
                delBtn.className = 'btn-delete-category';
                delBtn.title = 'Eliminar';
                delBtn.innerHTML = '<i class="fas fa-trash"></i>';
                delBtn.onclick = () => deleteCategory(cat.id);

                li.append(dot, nameInput, colorInput, saveBtn, delBtn);
                list.appendChild(li);
            });
        })
        .catch(() => setCatStatus('Error cargando categorías', true));
}

function addCategory() {
    const name = document.getElementById('newCatName').value.trim();
    const color = document.getElementById('newCatColor').value;
    if (!name) { setCatStatus('Escribí un nombre', true); return; }

    fetch('/api/categories', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, color })
    })
    .then(r => r.json().then(d => ({ status: r.status, data: d })))
    .then(({ status, data }) => {
        if (status === 201) {
            document.getElementById('newCatName').value = '';
            setCatStatus(`"${data.name}" creada`, false);
            renderCategoriesList();
            loadCategories();
        } else {
            setCatStatus(data.error || 'Error al crear', true);
        }
    })
    .catch(() => setCatStatus('Error de conexión', true));
}

function updateCategory(id, name, color) {
    if (!name.trim()) { setCatStatus('El nombre no puede estar vacío', true); return; }
    fetch(`/api/categories/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: name.trim(), color })
    })
    .then(r => r.json().then(d => ({ status: r.status, data: d })))
    .then(({ status, data }) => {
        if (status === 200) {
            setCatStatus('Guardado', false);
            renderCategoriesList();
            loadCategories();
            loadFavorites();
        } else {
            setCatStatus(data.error || 'Error al guardar', true);
        }
    })
    .catch(() => setCatStatus('Error de conexión', true));
}

function deleteCategory(id) {
    if (!confirm('¿Eliminar esta categoría? Los favoritos quedarán sin categoría.')) return;
    fetch(`/api/categories/${id}`, { method: 'DELETE' })
    .then(r => {
        if (r.ok) {
            setCatStatus('Categoría eliminada', false);
            renderCategoriesList();
            loadCategories();
            loadFavorites();
        } else {
            r.json().then(d => setCatStatus(d.error || 'Error al eliminar', true));
        }
    })
    .catch(() => setCatStatus('Error de conexión', true));
}

// ===== Auth =====

function showLoginModal() {
    document.getElementById('loginModal').classList.remove('hidden');
    document.getElementById('loginField').focus();
}

function hideLoginModal() {
    document.getElementById('loginModal').classList.add('hidden');
    document.getElementById('loginError').classList.add('hidden');
    document.getElementById('loginError').textContent = '';
    document.getElementById('loginPassword').value = '';
}

function setAuthUI(user) {
    currentUser = user;
    const loginBtn = document.getElementById('loginBtn');
    const userInfo = document.getElementById('userInfo');
    const usernameDisplay = document.getElementById('usernameDisplay');
    if (user) {
        loginBtn.classList.add('hidden');
        usernameDisplay.textContent = user.username;
        userInfo.classList.remove('hidden');
    } else {
        loginBtn.classList.remove('hidden');
        userInfo.classList.add('hidden');
    }
}

function doLogin() {
    const login = document.getElementById('loginField').value.trim();
    const password = document.getElementById('loginPassword').value;
    const errorEl = document.getElementById('loginError');
    const submitBtn = document.getElementById('loginSubmitBtn');

    if (!login || !password) {
        errorEl.textContent = 'Completá usuario y contraseña.';
        errorEl.classList.remove('hidden');
        return;
    }

    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Entrando...';

    fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ login, password })
    })
    .then(response => response.json().then(data => ({ status: response.status, data })))
    .then(({ status, data }) => {
        if (status === 200) {
            sessionStorage.setItem('username', data.username);
            setAuthUI({ username: data.username });
            hideLoginModal();
            loadFavorites();
            loadCategories();
        } else {
            errorEl.textContent = data.error || 'Credenciales incorrectas.';
            errorEl.classList.remove('hidden');
        }
    })
    .catch(() => {
        errorEl.textContent = 'Error de conexión.';
        errorEl.classList.remove('hidden');
    })
    .finally(() => {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-sign-in-alt"></i> Entrar';
    });
}

function doLogout() {
    fetch('/api/auth/logout', { method: 'POST' })
    .finally(() => {
        sessionStorage.removeItem('username');
        setAuthUI(null);
        renderFavorites([]);
        updateFavoritesCount(0);
        // Limpiar categorías
        const select = elements.categoryInput;
        while (select.options.length > 1) select.remove(1);
    });
}

function checkAuth() {
    fetch('/api/categories')
    .then(response => {
        if (response.status === 401) {
            showLoginModal();
            return null;
        }
        return response.json();
    })
    .then(data => {
        if (!data) return;
        // Autenticado: obtener username desde favoritos o asumir sesión activa
        fetch('/api/v2/favorites')
        .then(r => r.json())
        .then(favData => {
            // No hay endpoint /me, usamos el username guardado en sesión si existe
            const stored = sessionStorage.getItem('username');
            setAuthUI({ username: stored || 'Usuario' });
            populateCategories(data.categories || []);
            loadFavorites();
        });
    })
    .catch(() => showLoginModal());
}

function populateCategories(categories) {
    const select = elements.categoryInput;
    while (select.options.length > 1) select.remove(1);
    categories.forEach(category => {
        const option = document.createElement('option');
        option.value = category.id;
        option.textContent = category.name;
        select.appendChild(option);
    });
}

// Inicialización
function init() {
    applyTheme();
    setupEventListeners();
    setupAuthListeners();
    loadData();
    startAutoRefresh();
    checkAuth();
}

function setupAuthListeners() {
    document.getElementById('loginBtn').addEventListener('click', showLoginModal);
    document.getElementById('logoutBtn').addEventListener('click', doLogout);
    document.getElementById('loginSubmitBtn').addEventListener('click', doLogin);
    document.getElementById('loginPassword').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') doLogin();
    });
    document.getElementById('manageCategoriesBtn').addEventListener('click', openCategoriesModal);
    document.getElementById('closeCategoriesBtn').addEventListener('click', closeCategoriesModal);
    document.getElementById('addCategoryBtn').addEventListener('click', addCategory);
    document.getElementById('newCatName').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') addCategory();
    });
    // Cerrar modal al hacer click en el overlay
    document.getElementById('categoriesModal').addEventListener('click', function(e) {
        if (e.target === this) closeCategoriesModal();
    });
}

// Iniciar aplicación cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}