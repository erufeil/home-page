"""
Favorite CRUD endpoints with category association.
"""
import logging
import os
from urllib.parse import urlparse
from flask import jsonify, request, make_response
from flask_login import login_required, current_user
from sqlalchemy import or_, func
from backend.favorites import favorites_bp
from backend import db
from backend.models import Favorite, Category

logger = logging.getLogger(__name__)

def get_user_favorite(favorite_id):
    """
    Retrieve a favorite by ID if it belongs to the current user.
    Returns (favorite, error_response) tuple. If favorite not found or not owned,
    error_response is a Flask response; otherwise error_response is None.
    """
    favorite = db.session.get(Favorite, favorite_id)
    if not favorite:
        return None, make_response(
            jsonify({"error": f"Favorite with ID {favorite_id} not found"}),
            404
        )
    if favorite.user_id != current_user.id:
        return None, make_response(
            jsonify({"error": "Access denied"}),
            403
        )
    return favorite, None

def validate_category_ownership(category_id):
    """
    Validate that category exists and belongs to current user.
    Returns (category, error_response) tuple.
    """
    if category_id is None:
        return None, None  # No category (uncategorized) is allowed
    
    category = db.session.get(Category, category_id)
    if not category:
        return None, make_response(
            jsonify({"error": f"Category with ID {category_id} not found"}),
            404
        )
    if category.user_id != current_user.id:
        return None, make_response(
            jsonify({"error": "Access denied to category"}),
            403
        )
    return category, None

def extract_domain(url):
    """Extract domain from URL."""
    parsed = urlparse(url)
    return parsed.netloc

def clean_domain(domain):
    """
    Clean domain by removing common subdomains (www, listado, etc.).
    Simplified version from backend.services.favorites.
    """
    if not domain:
        return ''
    domain = domain.lower()
    if domain.startswith('www.'):
        domain = domain[4:]
    # Additional cleaning could be added here
    return domain

@favorites_bp.route('', methods=['GET'])
@login_required
def list_favorites():
    """
    List all favorites belonging to the current user.
    
    Query parameters:
    - category_id: filter by category (optional)
    - include_uncategorized: if 'true', include favorites with category_id = NULL (default true)
    
    Returns:
        JSON list of favorites with category info.
    """
    category_id = request.args.get('category_id')
    include_uncategorized = request.args.get('include_uncategorized', 'true').lower() == 'true'
    
    query = db.session.query(Favorite).filter(Favorite.user_id == current_user.id)
    
    if category_id:
        try:
            cat_id = int(category_id)
            query = query.filter(Favorite.category_id == cat_id)
        except ValueError:
            return make_response(
                jsonify({"error": "category_id must be an integer"}),
                400
            )
    elif not include_uncategorized:
        query = query.filter(Favorite.category_id.isnot(None))
    
    # Order by category display_order? For now order by favorite display_order
    favorites = query.order_by(Favorite.display_order.asc()).all()
    
    result = []
    for fav in favorites:
        fav_data = {
            'id': fav.id,
            'url': fav.url,
            'title': fav.title,
            'domain': fav.domain,
            'logo_filename': fav.logo_filename,
            'tipo': fav.tipo,
            'category_id': fav.category_id,
            'display_order': fav.display_order,
            'created_at': fav.created_at.isoformat() if fav.created_at else None,
            'updated_at': fav.updated_at.isoformat() if fav.updated_at else None,
            'category': {
                'id': fav.category.id,
                'name': fav.category.name,
                'color': fav.category.color
            } if fav.category else None
        }
        result.append(fav_data)
    
    return make_response(jsonify({"favorites": result}), 200)

@favorites_bp.route('', methods=['POST'])
@login_required
def create_favorite():
    """
    Create a new favorite for the current user.
    
    Request body (JSON):
    - url (required): website URL
    - title (optional): display title (defaults to domain)
    - category_id (optional): assign to category
    - tipo (optional): 'favorito' or 'tarea_pendiente' (default 'favorito')
    - logo_filename (optional): filename of logo in /logos
    
    Returns:
        JSON of created favorite.
    """
    if not request.is_json:
        return make_response(
            jsonify({"error": "Content-Type must be application/json"}),
            400
        )
    
    data = request.get_json()
    if not data:
        return make_response(
            jsonify({"error": "Invalid or empty JSON payload"}),
            400
        )
    
    url = data.get('url', '').strip()
    if not url:
        return make_response(
            jsonify({"error": "URL is required"}),
            400
        )
    
    # Validate URL format (basic)
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return make_response(
            jsonify({"error": "Invalid URL format"}),
            400
        )
    
    # Extract and clean domain
    domain = extract_domain(url)
    cleaned_domain = clean_domain(domain)
    
    title = (data.get('title') or '').strip()
    if not title:
        title = cleaned_domain.replace('.', ' ').title()
    
    tipo = data.get('tipo', 'favorito')
    if tipo not in ('favorito', 'tarea_pendiente'):
        tipo = 'favorito'
    
    logo_filename = data.get('logo_filename')
    if not logo_filename:
        # Intentar scrapear el logo automáticamente
        try:
            import tempfile, shutil
            from backend.services.favorites import (
                find_logo_url, find_local_logo, generate_filename, ensure_directories, LOGOS_DIR
            )
            import requests as _req
            ensure_directories()
            logger.info(f"[LOGO] Iniciando scraping para: {url}")
            _headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,*/*;q=0.8',
            }
            _resp = _req.get(url, headers=_headers, timeout=10)
            logger.info(f"[LOGO] HTTP {_resp.status_code} al obtener página")
            if _resp.ok:
                _candidates = find_logo_url(_resp.text, url, url=url, title=title)
                logger.info(f"[LOGO] Candidatos encontrados ({len(_candidates)}): {_candidates[:5]}")
                MIN_SIZE = 2048  # 2 KB
                _img_headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                }
                # Descargar top candidatos a archivos temporales y medir tamaño
                _scored_downloads = []  # (score_idx, size, tmp_path, candidate_url, final_name)
                _tmpdir = tempfile.mkdtemp()
                logger.info(f"[LOGO] Directorio temporal: {_tmpdir}")
                logger.info(f"[LOGO] Directorio destino logos: {LOGOS_DIR}")
                try:
                    for _idx, _logo_url in enumerate(_candidates[:10]):
                        _final_name = generate_filename(url, _logo_url)
                        _final_path = os.path.join(LOGOS_DIR, _final_name)
                        # Si ya existe en LOGOS_DIR, usarlo directo sin descargar
                        if os.path.exists(_final_path):
                            _size = os.path.getsize(_final_path)
                            logger.info(f"[LOGO] [{_idx}] Ya existe en disco ({_size}B): {_final_name}")
                            _scored_downloads.append((_idx, _size, None, _logo_url, _final_name))
                            continue
                        try:
                            logger.info(f"[LOGO] [{_idx}] Descargando: {_logo_url}")
                            _r = _req.get(_logo_url, headers=_img_headers, timeout=10)
                            logger.info(f"[LOGO] [{_idx}] HTTP {_r.status_code}, {len(_r.content)}B, content-type={_r.headers.get('content-type','?')}")
                            if not _r.ok:
                                logger.warning(f"[LOGO] [{_idx}] Descarga fallida HTTP {_r.status_code}: {_logo_url}")
                                continue
                            _tmp = os.path.join(_tmpdir, f"candidate_{_idx}")
                            with open(_tmp, 'wb') as _f:
                                _f.write(_r.content)
                            _scored_downloads.append((_idx, len(_r.content), _tmp, _logo_url, _final_name))
                        except Exception as _dl_err:
                            logger.warning(f"[LOGO] [{_idx}] Error descargando {_logo_url}: {_dl_err}")
                            continue

                    logger.info(f"[LOGO] Descargas exitosas: {len(_scored_downloads)}")
                    if _scored_downloads:
                        # Agrupar por score (idx 0 = mejor score; idx más alto = peor score)
                        best_idx = _scored_downloads[0][0]
                        # Todos los que tengan el mismo score que el mejor
                        _tied = [d for d in _scored_downloads if d[0] == best_idx]
                        # Tie-breaking: menor >= MIN_SIZE gana; si ninguno >= MIN_SIZE, el mayor
                        _big = [d for d in _tied if d[1] >= MIN_SIZE]
                        _winner = min(_big, key=lambda d: d[1]) if _big else max(_tied, key=lambda d: d[1])
                        _, _wsize, _wtmp, _wurl, _wname = _winner
                        if _wtmp is None:
                            # Ya existía en LOGOS_DIR
                            logo_filename = _wname
                            logger.info(f"[LOGO] Usando logo ya existente: {_wname}")
                        else:
                            _dest = os.path.join(LOGOS_DIR, _wname)
                            shutil.move(_wtmp, _dest)
                            logo_filename = _wname
                            logger.info(f"[LOGO] Logo guardado ({_wsize}B): {_dest}")
                    else:
                        logger.warning(f"[LOGO] Ningún candidato descargado exitosamente para {url}")
                finally:
                    shutil.rmtree(_tmpdir, ignore_errors=True)
            else:
                logger.warning(f"[LOGO] No se pudo obtener la página HTTP {_resp.status_code}: {url}")
        except Exception as _e:
            logger.warning(f"[LOGO] Scraping falló para {url}: {_e}", exc_info=True)

        # Fallback: buscar en archivos locales ya existentes por scoring
        if not logo_filename:
            from backend.services.favorites import find_local_logo
            logo_filename = find_local_logo(url, title)
            if logo_filename:
                logger.info(f"[LOGO] Fallback local encontró: {logo_filename}")
            else:
                logger.info(f"[LOGO] Sin logo encontrado para: {url}")

    category_id = data.get('category_id')
    if category_id is not None:
        # Validate category ownership
        category, error = validate_category_ownership(category_id)
        if error:
            return error
        # category is either Category object or None (if category_id is null)
    
    # Determine display_order (place at end of category or uncategorized)
    if category_id is None:
        max_order = db.session.query(
            func.max(Favorite.display_order)
        ).filter(
            Favorite.user_id == current_user.id,
            Favorite.category_id.is_(None)
        ).scalar() or -1
    else:
        max_order = db.session.query(
            func.max(Favorite.display_order)
        ).filter(
            Favorite.user_id == current_user.id,
            Favorite.category_id == category_id
        ).scalar() or -1
    display_order = data.get('display_order', max_order + 1)
    
    try:
        favorite = Favorite(
            user_id=current_user.id,
            url=url,
            title=title,
            domain=cleaned_domain,
            logo_filename=logo_filename,
            tipo=tipo,
            category_id=category_id,
            display_order=display_order
        )
        db.session.add(favorite)
        db.session.commit()
        
        favorite_data = {
            'id': favorite.id,
            'url': favorite.url,
            'title': favorite.title,
            'domain': favorite.domain,
            'logo_filename': favorite.logo_filename,
            'tipo': favorite.tipo,
            'category_id': favorite.category_id,
            'display_order': favorite.display_order,
            'created_at': favorite.created_at.isoformat() if favorite.created_at else None,
            'updated_at': favorite.updated_at.isoformat() if favorite.updated_at else None
        }
        return make_response(jsonify(favorite_data), 201)
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating favorite: {e}", exc_info=True)
        return make_response(
            jsonify({"error": "Internal server error"}),
            500
        )

@favorites_bp.route('/<int:favorite_id>', methods=['GET'])
@login_required
def get_favorite(favorite_id):
    """
    Retrieve a specific favorite.
    
    Returns:
        JSON favorite details.
    """
    favorite, error = get_user_favorite(favorite_id)
    if error:
        return error
    
    favorite_data = {
        'id': favorite.id,
        'url': favorite.url,
        'title': favorite.title,
        'domain': favorite.domain,
        'logo_filename': favorite.logo_filename,
        'tipo': favorite.tipo,
        'category_id': favorite.category_id,
        'display_order': favorite.display_order,
        'created_at': favorite.created_at.isoformat() if favorite.created_at else None,
        'updated_at': favorite.updated_at.isoformat() if favorite.updated_at else None
    }
    return make_response(jsonify(favorite_data), 200)

@favorites_bp.route('/<int:favorite_id>', methods=['PUT'])
@login_required
def update_favorite(favorite_id):
    """
    Update a favorite's properties.
    
    Request body (JSON):
    - url (optional): new URL
    - title (optional): new title
    - category_id (optional): change category (null to uncategorize)
    - tipo (optional): change tipo
    - display_order (optional): new position
    - logo_filename (optional): new logo filename
    
    Returns:
        JSON updated favorite.
    """
    if not request.is_json:
        return make_response(
            jsonify({"error": "Content-Type must be application/json"}),
            400
        )
    
    data = request.get_json()
    if not data:
        return make_response(
            jsonify({"error": "Invalid or empty JSON payload"}),
            400
        )
    
    favorite, error = get_user_favorite(favorite_id)
    if error:
        return error
    
    # Update URL and domain if provided
    if 'url' in data:
        url = data['url'].strip()
        if not url:
            return make_response(
                jsonify({"error": "URL cannot be empty"}),
                400
            )
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return make_response(
                jsonify({"error": "Invalid URL format"}),
                400
            )
        favorite.url = url
        favorite.domain = clean_domain(extract_domain(url))
    
    # Update title if provided
    if 'title' in data:
        title = data['title'].strip()
        if not title:
            title = clean_domain(favorite.domain).replace('.', ' ').title()
        favorite.title = title
    
    # Update tipo if provided
    if 'tipo' in data:
        tipo = data['tipo']
        if tipo not in ('favorito', 'tarea_pendiente'):
            return make_response(
                jsonify({"error": "tipo must be 'favorito' or 'tarea_pendiente'"}),
                400
            )
        favorite.tipo = tipo
    
    # Update logo_filename if provided
    if 'logo_filename' in data:
        favorite.logo_filename = data['logo_filename']
    
    # Update category_id if provided
    if 'category_id' in data:
        category_id = data['category_id']
        # If null, uncategorize
        if category_id is None:
            favorite.category_id = None
        else:
            # Validate category ownership
            category, error = validate_category_ownership(category_id)
            if error:
                return error
            favorite.category_id = category_id
    
    # Update display_order if provided
    if 'display_order' in data:
        try:
            display_order = int(data['display_order'])
            favorite.display_order = display_order
        except (ValueError, TypeError):
            return make_response(
                jsonify({"error": "display_order must be an integer"}),
                400
            )
    
    try:
        db.session.commit()
        favorite_data = {
            'id': favorite.id,
            'url': favorite.url,
            'title': favorite.title,
            'domain': favorite.domain,
            'logo_filename': favorite.logo_filename,
            'tipo': favorite.tipo,
            'category_id': favorite.category_id,
            'display_order': favorite.display_order,
            'created_at': favorite.created_at.isoformat() if favorite.created_at else None,
            'updated_at': favorite.updated_at.isoformat() if favorite.updated_at else None
        }
        return make_response(jsonify(favorite_data), 200)
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating favorite {favorite_id}: {e}", exc_info=True)
        return make_response(
            jsonify({"error": "Internal server error"}),
            500
        )
@favorites_bp.route('/reorder', methods=['PUT'])
@login_required
def reorder_favorites():
    """
    Reorder favorites and optionally move them to a different category.
    
    Request body (JSON):
    - favorite_ids (required): list of favorite IDs in desired order
    - category_id (optional): if provided, move all favorites to this category
      (null to uncategorize). If omitted, keep current categories.
    
    Returns:
        Success message.
    """
    if not request.is_json:
        return make_response(
            jsonify({"error": "Content-Type must be application/json"}),
            400
        )
    
    data = request.get_json()
    if not data:
        return make_response(
            jsonify({"error": "Invalid or empty JSON payload"}),
            400
        )
    
    favorite_ids = data.get('favorite_ids')
    if not isinstance(favorite_ids, list):
        return make_response(
            jsonify({"error": "favorite_ids must be a list"}),
            400
        )
    
    if len(favorite_ids) == 0:
        return make_response(
            jsonify({"error": "favorite_ids cannot be empty"}),
            400
        )
    
    # Ensure all IDs are integers
    try:
        favorite_ids = [int(fid) for fid in favorite_ids]
    except (ValueError, TypeError):
        return make_response(
            jsonify({"error": "All favorite_ids must be integers"}),
            400
        )
    
    category_id_provided = 'category_id' in data
    category_id = data.get('category_id')  # could be None (null) or missing -> None
    
    if category_id_provided:
        # category_id may be null (None) or integer
        if category_id is not None:
            try:
                category_id = int(category_id)
            except (ValueError, TypeError):
                return make_response(
                    jsonify({"error": "category_id must be an integer or null"}),
                    400
                )
            # Validate category ownership
            category, error = validate_category_ownership(category_id)
            if error:
                return error
        else:
            # category_id is null (explicit uncategorize)
            category = None
    else:
        # category_id not provided, keep current categories
        category_id = None  # ensure it's None
        category = None
    
    move_to_category = category_id_provided
    
    # Fetch all favorites owned by current user with given IDs
    favorites = db.session.query(Favorite).filter(
        Favorite.id.in_(favorite_ids),
        Favorite.user_id == current_user.id
    ).all()
    
    # Check that we found all favorites
    found_ids = {fav.id for fav in favorites}
    missing_ids = set(favorite_ids) - found_ids
    if missing_ids:
        return make_response(
            jsonify({"error": f"Favorites not found or access denied: {sorted(missing_ids)}"}),
            404
        )
    
    # Ensure no duplicate IDs in request
    if len(favorite_ids) != len(set(favorite_ids)):
        return make_response(
            jsonify({"error": "Duplicate favorite_ids in request"}),
            400
        )
    
    # Map favorite ID to favorite object
    fav_map = {fav.id: fav for fav in favorites}
    
    
    try:
        # Update each favorite
        for position, fav_id in enumerate(favorite_ids):
            fav = fav_map[fav_id]
            
            # Update display order
            fav.display_order = position
            
            # Update category if requested
            if move_to_category:
                fav.category_id = category_id
                # Note: we could use fav.move_to_category(category, position) but that
                # also adjusts display_order which we already set.
        
        db.session.commit()
        
        return make_response(
            jsonify({"message": f"Reordered {len(favorite_ids)} favorites successfully"}),
            200
        )
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error reordering favorites: {e}", exc_info=True)
        return make_response(
            jsonify({"error": "Internal server error"}),
            500
        )


@favorites_bp.route('/<int:favorite_id>', methods=['DELETE'])
@login_required
def delete_favorite(favorite_id):
    """
    Delete a favorite.
    
    Returns:
        Success message.
    """
    favorite, error = get_user_favorite(favorite_id)
    if error:
        return error
    
    try:
        db.session.delete(favorite)
        db.session.commit()
        
        return make_response(
            jsonify({"message": f"Favorite {favorite_id} deleted successfully"}),
            200
        )
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting favorite {favorite_id}: {e}", exc_info=True)
        return make_response(
            jsonify({"error": "Internal server error"}),
            500
        )