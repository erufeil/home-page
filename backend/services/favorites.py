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
    """Genera un nombre de archivo único basado en la URL."""
    domain = extract_domain(url)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_domain = re.sub(r'[^\w\-\.]', '_', domain)
    
    # Determine extension from logo URL if available
    extension = '.png'  # default
    if logo_url:
        # Extract file extension from logo URL path
        import os
        from urllib.parse import urlparse
        parsed = urlparse(logo_url)
        path = parsed.path
        if path:
            _, ext = os.path.splitext(path)
            if ext and len(ext) <= 5:  # reasonable extension length
                ext_lower = ext.lower()
                # Only allow known image extensions
                if ext_lower in ['.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.webp']:
                    extension = ext_lower
    
    return f"{safe_domain}_{timestamp}{extension}"

def find_logo_url(html_content, base_url):
    """Busca URLs de logos en el HTML."""
    logo_patterns = [
        # Favicon patterns - improved to capture href value correctly
        r'<link[^>]*?rel=["\'](?:icon|shortcut\s+icon|apple-touch-icon)["\'][^>]*?href=["\']([^"\']+?)["\']',
        # Open Graph image
        r'<meta[^>]*?property=["\']og:image["\'][^>]*?content=["\']([^"\']+?)["\']',
        # Twitter image
        r'<meta[^>]*?name=["\']twitter:image["\'][^>]*?content=["\']([^"\']+?)["\']',
        # Logo in img class
        r'<img[^>]*?class=["\'][^"\']*logo[^"\']*["\'][^>]*?src=["\']([^"\']+?)["\']',
        # Logo in img alt
        r'<img[^>]*?alt=["\'][^"\']*logo[^"\']*["\'][^>]*?src=["\']([^"\']+?)["\']',
        # Logo in img src (contains logo or brand)
        r'<img[^>]*?src=["\']([^"\']*?(?:logo|brand)[^"\']*?)["\'][^>]*?>',
        # Schema.org logo
        r'<meta[^>]*?itemprop=["\']image["\'][^>]*?content=["\']([^"\']+?)["\']',
    ]
    
    for pattern in logo_patterns:
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        if matches:
            logo_url = matches[0]
            
            if logo_url:
                # Convertir URL relativa a absoluta
                if logo_url.startswith('//'):
                    logo_url = f"https:{logo_url}"
                elif logo_url.startswith('/'):
                    parsed = urlparse(base_url)
                    logo_url = f"{parsed.scheme}://{parsed.netloc}{logo_url}"
                elif not logo_url.startswith(('http://', 'https://')):
                    logo_url = f"{base_url}/{logo_url}"
                
                # Ensure URL has proper extension
                if logo_url and not re.search(r'\.(png|jpg|jpeg|gif|ico|svg|webp)$', logo_url, re.IGNORECASE):
                    # Try adding .ico or .png if missing
                    if '/favicon' in logo_url.lower():
                        logo_url += '.ico'
                    elif '/logo' in logo_url.lower():
                        logo_url += '.png'
                
                return logo_url
    
    # Fallback to favicon.ico
    parsed = urlparse(base_url)
    favicon_url = f"{parsed.scheme}://{parsed.netloc}/favicon.ico"
    return favicon_url

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
        logo_url = find_logo_url(html_content, url)
        logo_filename = None
        
        if logo_url:
            logo_filename = generate_filename(url, logo_url)
            downloaded_path = download_logo(logo_url, logo_filename)
            if not downloaded_path:
                logo_filename = None  # Si falla la descarga, no guardar filename
        
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