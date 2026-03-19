"""
Servicio para manejar favoritos y scraping de logos.
"""
import os
import json
import requests
from urllib.parse import urlparse
import logging
from datetime import datetime
import re

logger = logging.getLogger(__name__)

from flask_login import current_user
from backend import db
from backend.models import Favorite

FAVORITES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'favorites')
FAVORITES_FILE = os.path.join(FAVORITES_DIR, 'favorites.json')
LOGOS_DIR = os.path.join(FAVORITES_DIR, 'logos')

def _favorite_to_legacy_dict(fav):
    """Convert Favorite SQLAlchemy object to legacy JSON format."""
    return {
        'id': str(fav.id),
        'url': fav.url,
        'title': fav.title,
        'domain': fav.domain,
        'logo': fav.logo_filename,
        'tipo': fav.tipo,
        'created_at': fav.created_at.isoformat() if fav.created_at else None
    }

def ensure_directories():
    """Asegura que existan los directorios necesarios."""
    os.makedirs(LOGOS_DIR, exist_ok=True)
    if not os.path.exists(FAVORITES_FILE):
        with open(FAVORITES_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)

def get_favorites():
    """Obtiene la lista de favoritos."""
    ensure_directories()
    try:
        with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
            favorites = json.load(f)
        
        # Migración: agregar campo 'tipo' si falta (backward compatibility)
        modified = False
        for favorite in favorites:
            if 'tipo' not in favorite:
                favorite['tipo'] = 'favorito'
                modified = True
        
        if modified:
            save_favorites(favorites)
            logger.info("Migración: campo 'tipo' agregado a favoritos existentes")
        
        return favorites
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def get_favorites_db():
    """Obtiene la lista de favoritos del usuario actual desde la base de datos."""
    favorites = db.session.query(Favorite).filter_by(user_id=current_user.id).order_by(Favorite.display_order).all()
    return [_favorite_to_legacy_dict(fav) for fav in favorites]

def save_favorites(favorites):
    """Guarda la lista de favoritos."""
    ensure_directories()
    with open(FAVORITES_FILE, 'w', encoding='utf-8') as f:
        json.dump(favorites, f, indent=2, ensure_ascii=False)

def extract_domain(url):
    """Extrae el dominio de una URL."""
    parsed = urlparse(url)
    return parsed.netloc

def get_pure_domain(url):
    """Retorna el dominio puro: hostname sin TLD, sin www, sin path.

    Ejemplos:
        https://meet.google.com/landing  ->  meet.google
        https://www.github.com/          ->  github
        https://mercadolibre.com.ar/     ->  mercadolibre
    """
    parsed = urlparse(url)
    hostname = parsed.netloc.lower()

    # Remover puerto si hay
    if ':' in hostname:
        hostname = hostname.split(':')[0]

    # Remover www.
    if hostname.startswith('www.'):
        hostname = hostname[4:]

    # TLDs de mayor a menor longitud para evitar matches parciales
    tlds = [
        '.com.ar', '.org.ar', '.net.ar', '.gob.ar',
        '.co.uk', '.org.uk', '.com.au', '.com.br', '.com.mx',
        '.com.es', '.com.fr', '.com.de', '.com.it',
        '.com', '.org', '.net', '.edu', '.gov', '.mil', '.int',
        '.io', '.co', '.app', '.dev', '.ai',
        '.ar', '.uk', '.au', '.br', '.mx', '.es', '.fr', '.de', '.it',
    ]

    for tld in tlds:
        if hostname.endswith(tld):
            return hostname[:-len(tld)]

    # Fallback: quitar último segmento
    parts = hostname.split('.')
    if len(parts) >= 2:
        return '.'.join(parts[:-1])

    return hostname

def clean_domain_name(domain):
    """Limpia un nombre de dominio para mostrar como título."""
    # Remover www. al inicio
    if domain.startswith('www.'):
        domain = domain[4:]
    
    # Remover subdominios comunes (listado., m., mobile., etc.)
    # Mantener solo el dominio principal (segundo nivel)
    parts = domain.split('.')
    
    # Si hay más de 2 partes (ej: listado.mercadolibre.com.ar)
    # Tomar la penúltima parte como nombre principal
    if len(parts) >= 3:
        # Para dominios como .co.uk, .com.ar, etc.
        # Buscar el dominio principal (última parte antes de TLD)
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
        
        domain_parts = parts.copy()
        name_candidate = domain_parts[0]
        found_tld = False
        
        # Buscar TLD conocido
        for i in range(len(domain_parts) - 1):
            test_tld = '.' + '.'.join(domain_parts[i+1:])
            if test_tld in tlds:
                name_candidate = domain_parts[i]
                found_tld = True
                break
        
        # Si no encontramos TLD conocido, usar la penúltima parte
        if not found_tld and len(domain_parts) >= 2:
            name_candidate = domain_parts[-2]
        
        name = name_candidate
    else:
        # Para dominios simples como google.com
        name = parts[0] if parts else domain
    
    # Remover guiones y reemplazar con espacios
    name = name.replace('-', ' ')
    
    # Capitalizar primera letra de cada palabra
    name = ' '.join(word.capitalize() for word in name.split())
    
    return name

def clean_domain(domain):
    """Limpia un dominio removiendo subdominios comunes (www, listado, etc.)."""
    # Convertir a minúsculas
    domain = domain.lower()
    
    # Remover www. al inicio
    if domain.startswith('www.'):
        domain = domain[4:]
    
    parts = domain.split('.')
    
    # Si hay menos de 2 partes, retornar dominio original
    if len(parts) < 2:
        return domain
    
    # Lista de TLDs conocidos (misma que en clean_domain_name)
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
    
    # Buscar el TLD más largo que coincida
    for i in range(len(parts) - 1):
        test_tld = '.' + '.'.join(parts[i+1:])
        if test_tld in tlds:
            main_domain_part = parts[i]
            # Reconstruir dominio con parte principal + TLD
            return main_domain_part + '.' + '.'.join(parts[i+1:])
    
    # Si no encontramos TLD conocido, asumir que la penúltima parte es el dominio principal
    if len(parts) >= 2:
        main_domain_part = parts[-2]
        return main_domain_part + '.' + parts[-1]
    
    # Fallback
    return domain

def generate_filename(url, logo_url=None):
    """Genera el nombre de archivo del logo basado en el dominio puro.

    Usa el dominio puro (sin TLD, sin www, sin path) como nombre base.
    Ejemplo: https://meet.google.com/landing  ->  meet.google.png
    Si el archivo ya existe, lo reutiliza (no duplica descargas).
    """
    pure_domain = get_pure_domain(url)
    safe_name = re.sub(r'[^\w\-\.]', '_', pure_domain)

    extension = '.png'
    if logo_url:
        from urllib.parse import urlparse as _urlparse
        parsed = _urlparse(logo_url)
        _, ext = os.path.splitext(parsed.path)
        if ext and len(ext) <= 5:
            ext_lower = ext.lower()
            if ext_lower in ['.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.webp']:
                extension = ext_lower

    return f"{safe_name}{extension}"

def _make_absolute(logo_url, base_url):
    """Convierte una URL relativa a absoluta."""
    if logo_url.startswith('//'):
        return f"https:{logo_url}"
    if logo_url.startswith('/'):
        parsed = urlparse(base_url)
        return f"{parsed.scheme}://{parsed.netloc}{logo_url}"
    if not logo_url.startswith(('http://', 'https://')):
        return f"{base_url.rstrip('/')}/{logo_url}"
    return logo_url

_VALID_IMG_EXT = re.compile(r'\.(ico|png|jpg|jpeg|svg|webp|gif)(\?.*)?$', re.IGNORECASE)

def _score_logo_url(candidate_url, domain_words, title_words):
    """
    Puntúa una URL candidata de logo según relevancia.

    Reglas:
      +1 si la URL contiene 'ico' O 'logo' (máximo 1 punto por ambas)
      +1 por cada palabra del dominio puro que aparezca en la URL
      +1 por cada palabra del título del usuario que aparezca en la URL
    Solo se consideran URLs con extensión .ico, .png, .jpg o .jpeg.
    """
    if not _VALID_IMG_EXT.search(candidate_url):
        return -1  # descartar

    url_lower = candidate_url.lower()
    score = 0

    # Regla 1: 'ico' o 'logo' → máximo 1 punto
    if 'ico' in url_lower or 'logo' in url_lower:
        score += 1

    # Regla 2: palabras del dominio puro
    for word in domain_words:
        if word and len(word) > 1 and word in url_lower:
            score += 1

    # Regla 3: palabras del título
    for word in title_words:
        if word and len(word) > 1 and word in url_lower:
            score += 1

    return score

def find_logo_url(html_content, base_url, url=None, title=None):
    """
    Recolecta todos los candidatos de imagen del HTML y los devuelve ordenados por score desc.

    Parámetros:
      html_content : texto HTML de la página
      base_url     : URL base para resolver URLs relativas
      url          : URL del sitio (para extraer palabras del dominio puro)
      title        : título ingresado por el usuario (para scoring extra)

    Retorna lista de URLs ordenadas por score (mayor primero).
    """
    source_url = url or base_url
    pure = get_pure_domain(source_url)
    domain_words = [w.lower() for w in pure.split('.') if w]

    title_words = []
    if title:
        title_words = [w.lower() for w in re.split(r'\W+', title) if len(w) > 1]

    patterns = [
        r'<link[^>]*?rel=["\'](?:icon|shortcut\s+icon|apple-touch-icon)["\'][^>]*?href=["\']([^"\']+?)["\']',
        r'<link[^>]*?href=["\']([^"\']+?)["\'][^>]*?rel=["\'](?:icon|shortcut\s+icon|apple-touch-icon)["\']',
        r'<meta[^>]*?property=["\']og:image["\'][^>]*?content=["\']([^"\']+?)["\']',
        r'<meta[^>]*?content=["\']([^"\']+?)["\'][^>]*?property=["\']og:image["\']',
        r'<meta[^>]*?name=["\']twitter:image(?::src)?["\'][^>]*?content=["\']([^"\']+?)["\']',
        r'<meta[^>]*?content=["\']([^"\']+?)["\'][^>]*?name=["\']twitter:image["\']',
        r'<img[^>]*?class=["\'][^"\']*logo[^"\']*["\'][^>]*?src=["\']([^"\']+?)["\']',
        r'<img[^>]*?alt=["\'][^"\']*logo[^"\']*["\'][^>]*?src=["\']([^"\']+?)["\']',
        # Todos los img src (captura amplia para scoring)
        r'<img[^>]*?\bsrc=["\']([^"\']+?)["\']',
        r'<meta[^>]*?itemprop=["\']image["\'][^>]*?content=["\']([^"\']+?)["\']',
    ]

    seen = set()
    scored = []
    for pattern in patterns:
        for match in re.findall(pattern, html_content, re.IGNORECASE | re.DOTALL):
            raw = match.strip()
            if not raw:
                continue
            absolute = _make_absolute(raw, base_url)
            if absolute not in seen:
                seen.add(absolute)
                s = _score_logo_url(absolute, domain_words, title_words)
                if s >= 0:
                    scored.append((s, absolute))

    # Rutas comunes de favicon como candidatos extra
    parsed = urlparse(base_url)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    for path in ['/favicon.png', '/favicon.ico', '/apple-touch-icon.png', '/logo.png']:
        c = f"{origin}{path}"
        if c not in seen:
            seen.add(c)
            s = _score_logo_url(c, domain_words, title_words)
            if s >= 0:
                scored.append((s, c))

    if not scored:
        return [f"{origin}/favicon.ico"]

    # Ordenar: mayor score primero; entre iguales no importa el orden
    scored.sort(key=lambda x: x[0], reverse=True)
    logger.debug(f"Logo candidates ranked: {scored[:5]}")
    return [c for _, c in scored]


def _score_filename(fname, domain_words, title_words):
    """
    Puntúa un filename local basándose SOLO en coincidencia de palabras
    del dominio/título con el nombre de archivo.

    No usa el bonus de keyword 'ico'/'logo' porque en filenames locales
    '.ico' es solo una extensión y causaría falsos positivos.

    Retorna -1 si no es imagen, 0 si no hay coincidencia, >0 según matches.
    """
    if not re.search(r'\.(ico|png|jpg|jpeg|svg|webp|gif)$', fname, re.IGNORECASE):
        return -1

    fname_lower = fname.lower()
    score = 0

    for word in domain_words:
        if word and len(word) > 1 and word in fname_lower:
            score += 1

    for word in title_words:
        if word and len(word) > 1 and word in fname_lower:
            score += 1

    return score


def find_local_logo(url, title=None):
    """
    Busca en LOGOS_DIR archivos existentes que coincidan mejor con la URL/título.
    Solo considera archivos cuyo nombre contenga palabras del dominio o título,
    para evitar falsos positivos (p.ej. todos los .ico recibían score > 0 por
    contener la cadena 'ico').

    Tie-breaking: si hay empate de score, se elige el archivo más pequeño que
    sea >= 2KB; si ninguno supera 2KB, se elige el más grande.

    Retorna el nombre del archivo (filename) o None si no hay candidatos.
    """
    if not os.path.isdir(LOGOS_DIR):
        return None

    pure = get_pure_domain(url)
    domain_words = [w.lower() for w in pure.split('.') if w]

    title_words = []
    if title:
        title_words = [w.lower() for w in re.split(r'\W+', title) if len(w) > 1]

    MIN_SIZE = 2048  # 2 KB

    candidates = []
    for fname in os.listdir(LOGOS_DIR):
        score = _score_filename(fname, domain_words, title_words)
        if score <= 0:
            continue
        fpath = os.path.join(LOGOS_DIR, fname)
        size = os.path.getsize(fpath)
        candidates.append((score, size, fname))

    if not candidates:
        return None

    best_score = max(c[0] for c in candidates)
    tied = [c for c in candidates if c[0] == best_score]

    # Entre empatados: preferir el más pequeño >= 2KB
    big_enough = [c for c in tied if c[1] >= MIN_SIZE]
    if big_enough:
        chosen = min(big_enough, key=lambda c: c[1])
    else:
        chosen = max(tied, key=lambda c: c[1])

    logger.info(f"Logo local encontrado por scoring ({chosen[0]} pts, {chosen[1]}B): {chosen[2]}")
    return chosen[2]

def download_logo(logo_url, filename):
    """Descarga un logo y lo guarda localmente."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'image',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'cross-site',
        }
        response = requests.get(logo_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Check if content is actually an image
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            logger.warning(f"Logo URL {logo_url} returned non-image content-type: {content_type}")
            # Still save if it might be an image with wrong header
        
        logo_path = os.path.join(LOGOS_DIR, filename)
        with open(logo_path, 'wb') as f:
            f.write(response.content)
        
        logger.info(f"Logo descargado: {logo_path}")
        return logo_path
    except Exception as e:
        logger.error(f"Error descargando logo {logo_url}: {e}")
        return None

def add_favorite(url, title=None, tipo='favorito', use_db=False):
    """Agrega un nuevo favorito con scraping de logo."""
    ensure_directories()
    
    try:
        # Obtener HTML del sitio con headers mejorados
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        html_content = response.text
        
        # Buscar logo
        logo_candidates = find_logo_url(html_content, url, url=url, title=title)
        logo_url = logo_candidates[0] if logo_candidates else None
        logo_filename = None

        if logo_url:
            logo_filename = generate_filename(url, logo_url)
            existing_path = os.path.join(LOGOS_DIR, logo_filename)
            if os.path.exists(existing_path):
                logger.info(f"Logo ya existe, reutilizando: {logo_filename}")
            else:
                downloaded_path = download_logo(logo_url, logo_filename)
                if not downloaded_path:
                    logo_filename = None
        
        # Extraer título del sitio si no se proporcionó
        if not title:
            title_match = re.search(r'<title[^>]*>(.*?)</title>', html_content, re.IGNORECASE)
            title = title_match.group(1).strip() if title_match else clean_domain_name(extract_domain(url))
        
        # Crear objeto favorito
        if use_db:
            # Crear objeto Favorite
            domain = clean_domain(extract_domain(url))
            favorite_obj = Favorite(
                user_id=current_user.id,
                url=url,
                title=title,
                domain=domain,
                logo_filename=logo_filename,
                tipo=tipo,
                category_id=None,
                display_order=0
            )
            db.session.add(favorite_obj)
            db.session.commit()
            favorite = _favorite_to_legacy_dict(favorite_obj)
        else:
            favorite = {
                'id': datetime.now().strftime("%Y%m%d%H%M%S"),
                'url': url,
                'title': title,
                'domain': clean_domain(extract_domain(url)),
                'logo': logo_filename,
                'tipo': tipo,
                'created_at': datetime.now().isoformat()
            }
            # Agregar a la lista JSON
            favorites = get_favorites()
            favorites.append(favorite)
            save_favorites(favorites)
        
        logger.info(f"Favorito agregado: {title} ({url})")
        return favorite
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            logger.warning(f"Acceso denegado (403) para {url}. Creando favorito sin logo.")
            # Still create favorite with limited info
            if use_db:
                domain = clean_domain(extract_domain(url))
                favorite_obj = Favorite(
                    user_id=current_user.id,
                    url=url,
                    title=title or clean_domain_name(extract_domain(url)),
                    domain=domain,
                    logo_filename=None,
                    tipo=tipo,
                    category_id=None,
                    display_order=0
                )
                db.session.add(favorite_obj)
                db.session.commit()
                favorite = _favorite_to_legacy_dict(favorite_obj)
            else:
                favorite = {
                    'id': datetime.now().strftime("%Y%m%d%H%M%S"),
                    'url': url,
                    'title': title or clean_domain_name(extract_domain(url)),
                    'domain': clean_domain(extract_domain(url)),
                    'logo': None,
                    'tipo': tipo,
                    'created_at': datetime.now().isoformat()
                }
                favorites = get_favorites()
                favorites.append(favorite)
                save_favorites(favorites)
            logger.info(f"Favorito agregado (sin logo debido a 403): {favorite['title']} ({url})")
            return favorite
        else:
            logger.error(f"Error HTTP {e.response.status_code} agregando favorito {url}: {e}")
            raise
    except Exception as e:
        logger.error(f"Error agregando favorito {url}: {e}")
        raise

def delete_favorite(favorite_id, use_db=False):
    """Elimina un favorito por ID."""
    if use_db:
        favorite = db.session.query(Favorite).filter_by(id=favorite_id, user_id=current_user.id).first()
        if not favorite:
            return False
        
        # Delete associated logo file if exists
        if favorite.logo_filename:
            logo_path = os.path.join(LOGOS_DIR, favorite.logo_filename)
            try:
                if os.path.exists(logo_path):
                    os.remove(logo_path)
                    logger.info(f"Logo file deleted: {logo_path}")
            except Exception as e:
                logger.error(f"Error deleting logo file {logo_path}: {e}")
                # Continue with deletion of favorite even if logo deletion fails
        
        db.session.delete(favorite)
        db.session.commit()
        return True
    else:
        favorites = get_favorites()
        deleted_favorite = None
        updated_favorites = []
        
        for f in favorites:
            if f['id'] != favorite_id:
                updated_favorites.append(f)
            else:
                deleted_favorite = f
        
        if deleted_favorite:
            # Delete associated logo file if exists
            logo = deleted_favorite.get('logo')
            if logo:
                logo_path = os.path.join(LOGOS_DIR, logo)
                try:
                    if os.path.exists(logo_path):
                        os.remove(logo_path)
                        logger.info(f"Logo file deleted: {logo_path}")
                except Exception as e:
                    logger.error(f"Error deleting logo file {logo_path}: {e}")
                    # Continue with deletion of favorite even if logo deletion fails
            
            save_favorites(updated_favorites)
            return True
        
        return False