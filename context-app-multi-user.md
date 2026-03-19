# Plan: Transformar Flask App a Multi-Usuario con Docker, Autenticación y Categorías

## TL;DR

> **Quick Summary**: Transformar la aplicación Flask monolítica (divisas, clima, favoritos) en una aplicación multi-usuario con Docker, autenticación, sesiones de 7 días, MariaDB externa, categorías editables y drag-and-drop.
> 
> **Deliverables**: 
> - Docker multi-stage build + docker-compose
> - Sistema de autenticación con registro/login (Flask-Login + Flask-Session)
> - Base de datos MariaDB con esquema para usuarios, categorías, favoritos
> - Panel de administración root (CRUD usuarios + reset contraseñas)
> - Categorías editables (lista default + personalización por usuario)
> - Drag-and-drop con Sortable.js para reordenar/mover tarjetas
> - Sitios por defecto para nuevos usuarios (Google, GitHub, etc.)
> - Pruebas automatizadas (TDD) + Agent-Executed QA Scenarios
> 
> **Estimated Effort**: Large (≈ 25-30 tasks)
> **Parallel Execution**: YES - 4 waves (max 8 tasks parallel)
> **Critical Path**: Docker setup → DB schema → Auth → Categories → Frontend integration → Tests

---

## Context

### Original Request
Transformar landing page Flask actual (panel de divisas, clima y sistema de favoritos/tareas) en aplicación multi-usuario con Docker, autenticación, sesiones de 7 días, base de datos MariaDB, y categorías editables para tarjetas.

### Interview Summary
**Key Discussions**:
- Mantener funcionalidad existente (divisas, clima, favoritos/tareas)
- Sistema de registro de usuarios (no solo login predefinido)
- Categorías default editables por cada usuario (persistencia en SQL)
- Panel de administración root con acceso mediante variable `ADMIN_PASSWORD`
- Framework de autenticación "más fácil de usar" → Flask-Login + Flask-Session
- Persistencia de sesiones en base de datos (7 días desde último acceso)
- No migrar datos existentes de favorites.json
- Logos en carpeta `/logos` con volumen Docker para persistencia
- Docker multi-stage build con imagen base python:3.12-alpine
- MariaDB externa (ya funcionando en otro servidor)
- Pruebas automatizadas incluidas (TDD)

**Research Findings**:
- **Aplicación actual**: Flask backend con servicios separados (dolar.py, weather.py, favorites.py)
- **Frontend**: HTML/CSS/JS vanilla con dos secciones: "Tareas Pendientes" y "Favoritos"
- **Almacenamiento**: JSON file (`favorites/favorites.json`)
- **No hay categorías** actualmente, solo campo `tipo` (favorito/tarea_pendiente)
- **No hay drag-and-drop** ni reordenamiento
- **Estructura de archivos**: 
  ```
  backend/
    app.py
    config.py
    services/
      dolar.py
      weather.py
      favorites.py
  frontend/
    index.html
    css/styles.css
    js/app.js
  favorites/
    favorites.json
    logos/
  ```

### Metis Review
*Consulta completada (timeout) - Self-review realizado para compensar.*

---

## Work Objectives

### Core Objective
Transformar la aplicación Flask existente en una plataforma multi-usuario con autenticación, base de datos relacional, categorías personalizables y capacidad de reordenamiento, manteniendo todas las funcionalidades actuales (divisas, clima, favoritos/tareas).

### Concrete Deliverables
1. **Docker setup**: Dockerfile multi-stage + docker-compose.yml con variables de entorno
2. **Database schema**: Scripts SQL para crear tablas (user, category, favorite, session) en MariaDB
3. **Authentication**: Endpoints de registro/login/logout, middleware de sesiones, password hashing (bcrypt)
4. **User management**: Panel de administración root (CRUD usuarios + reset contraseñas)
5. **Categories**: Backend CRUD, frontend selector en "Agregar Sitio", etiquetas en tarjetas
6. **Drag-and-drop**: Integración de Sortable.js, persistencia de orden en backend
7. **Default data**: Carga inicial de categorías default y sitios por defecto para nuevos usuarios
8. **Testing**: Suite de pruebas pytest con cobertura de endpoints críticos
9. **Documentation**: Instrucciones de despliegue y configuración

### Definition of Done
- [ ] `docker-compose up` levanta la aplicación sin errores
- [ ] Usuario puede registrarse, iniciar sesión y mantener sesión por 7 días
- [ ] Panel de administración root accesible con `ADMIN_PASSWORD`
- [ ] Categorías default presentes y editables por usuario
- [ ] Drag-and-drop funciona y persiste el orden
- [ ] Todas las funcionalidades existentes (divisas, clima, favoritos) siguen operativas
- [ ] `pytest` pasa todos los tests (cobertura >80%)
- [ ] Agent-Executed QA Scenarios completados y evidencias guardadas

### Must Have
- Mantener compatibilidad con funcionalidades existentes
- Autenticación con usuario/contraseña y sesiones de 7 días
- Categorías editables por usuario (lista default + personalización)
- Reordenamiento drag-and-drop dentro de categorías y entre categorías
- Docker + docker-compose para despliegue
- Conexión a MariaDB externa mediante variables de entorno
- Panel de administración root con CRUD usuarios + reset contraseñas
- Logos persistentes en volumen Docker (`/logos`)
- Pruebas automatizadas (TDD)

### Must NOT Have (Guardrails)
- No migrar datos existentes de favorites.json (usuarios nuevos comienzan con sitios por defecto)
- No implementar verificación de email
- No notificaciones push o sistema de mensajería
- No compartir favoritos entre usuarios
- No búsqueda avanzada o filtros complejos
- No soporte para múltiples idiomas
- No integración con redes sociales para login (solo usuario/contraseña)

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.
> Acceptance criteria requiring "user manually tests/confirms" are FORBIDDEN.

### Test Decision
- **Infrastructure exists**: NO (need to set up)
- **Automated tests**: TDD (tests before implementation)
- **Framework**: pytest + Flask-Testing
- **If TDD**: Each task follows RED (failing test) → GREEN (minimal impl) → REFACTOR

### QA Policy
Every task MUST include agent-executed QA scenarios (see TODO template below).
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Frontend/UI**: Use Playwright (playwright skill) — Navigate, interact, assert DOM, screenshot
- **TUI/CLI**: Use interactive_bash (tmux) — Run command, send keystrokes, validate output
- **API/Backend**: Use Bash (curl) — Send requests, assert status + response fields
- **Library/Module**: Use Bash (bun/node REPL) — Import, call functions, compare output

---

## Execution Strategy

### Parallel Execution Waves

> Maximize throughput by grouping independent tasks into parallel waves.
> Each wave completes before the next begins.
> Target: 5-8 tasks per wave. Fewer than 3 per wave (except final) = under-splitting.

```
Wave 1 (Start Immediately — foundation + scaffolding):
├── Task 1: Docker multi-stage build + docker-compose [quick]
├── Task 2: Database schema design + SQL scripts [quick]
├── Task 3: Basic Flask app restructuring (config, blueprints) [quick]
├── Task 4: Authentication models (User, Session) [quick]
├── Task 5: Category & Favorite models (SQLAlchemy) [quick]
├── Task 6: Logos volume setup + default logos download [unspecified-high]
└── Task 7: Test infrastructure setup (pytest, fixtures) [quick]

Wave 2 (After Wave 1 — core authentication):
├── Task 8: User registration endpoint (TDD) [deep]
├── Task 9: Login/logout endpoints (TDD) [deep]
├── Task 10: Session middleware (Flask-Session + MariaDB) [unspecified-high]
├── Task 11: Password hashing (bcrypt) + security utilities [quick]
├── Task 12: Admin panel backend (CRUD users) [unspecified-high]
├── Task 13: Admin panel frontend (basic UI) [visual-engineering]
└── Task 14: Authentication integration tests [deep]

Wave 3 (After Wave 2 — categories + favorites):
├── Task 15: Category CRUD endpoints (TDD) [deep]
├── Task 16: Favorite CRUD with category association (TDD) [deep]
├── Task 17: Default categories & sites seeding [quick]
├── Task 18: Frontend category selector in "Agregar Sitio" panel [visual-engineering]
├── Task 19: Display category tags on cards [visual-engineering]
├── Task 20: Drag-and-drop backend (order persistence) [unspecified-high]
└── Task 21: Sortable.js integration + UI drag handlers [visual-engineering]

Wave 4 (After Wave 3 — integration + existing features):
├── Task 22: Integrate authentication with existing favorites endpoints [deep]
├── Task 23: Update currency/weather services to work with new structure [quick]
├── Task 24: Frontend auth state management (login/logout UI) [visual-engineering]
├── Task 25: Session expiration handling (frontend + backend) [unspecified-high]
├── Task 26: Admin panel password reset functionality [deep]
└── Task 27: Comprehensive integration tests [deep]

Wave 5 (After Wave 4 — final verification):
├── Task 28: End-to-end tests with Playwright [unspecified-high]
├── Task 29: Performance & security audit [deep]
├── Task 30: Docker production readiness (health checks, logging) [quick]
└── Task 31: Documentation & deployment instructions [writing]

Wave FINAL (After ALL tasks — independent review, 4 parallel):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
├── Task F3: Real manual QA (unspecified-high)
└── Task F4: Scope fidelity check (deep)

Critical Path: Task 1 → Task 3 → Task 8 → Task 10 → Task 22 → Task 28 → F1-F4
Parallel Speedup: ~75% faster than sequential
Max Concurrent: 7 (Wave 1)
```

### Dependency Matrix (abbreviated — show ALL tasks in your generated plan)

> To be filled after task generation

### Agent Dispatch Summary

- **Wave 1**: **7** tasks — mix of quick, unspecified-high
- **Wave 2**: **7** tasks — deep, unspecified-high, visual-engineering
- **Wave 3**: **7** tasks — deep, visual-engineering, unspecified-high
- **Wave 4**: **6** tasks — deep, quick, visual-engineering, unspecified-high
- **Wave 5**: **4** tasks — unspecified-high, deep, quick, writing
- **FINAL**: **4** tasks — oracle, unspecified-high, deep

> This is abbreviated for reference. YOUR generated plan must include the FULL matrix for ALL tasks.

---

## TODOs

> Implementation + Test = ONE Task. Never separate.
> EVERY task MUST have: Recommended Agent Profile + Parallelization info + QA Scenarios.
> **A task WITHOUT QA Scenarios is INCOMPLETE. No exceptions.**

- [ ] 1. **Docker multi-stage build + docker-compose**

  **What to do**:
  - Create `Dockerfile` with multi-stage build: builder stage (install dependencies), runtime stage (copy app, use python:3.12-alpine)
  - Create `docker-compose.yml` with service definition, environment variables, volume mount for `/logos`
  - Add `.env.example` with required variables (DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, ADMIN_PASSWORD, WEATHER_API_KEY, etc.)
  - Test build: `docker build -t context-app .` and `docker-compose up --build`

  **Must NOT do**:
  - No need to set up MariaDB container (external DB)
  - No complex orchestration (single service only)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Dockerfile and docker-compose are straightforward configuration tasks
  - **Skills**: None needed for basic Docker setup
  - **Skills Evaluated but Omitted**:
    - `playwright`: No browser interaction needed
    - `git-master`: Version control not required for this task

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2-7)
  - **Blocks**: Task 3 (app restructuring), Task 6 (logos volume)
  - **Blocked By**: None (can start immediately)

  **References** (CRITICAL - Be Exhaustive):

  **Pattern References** (existing code to follow):
  - No existing Dockerfile in project — create from scratch following Python/Flask best practices
  - Reference: Official Python Docker images documentation (`python:3.12-alpine`)

  **API/Type References** (contracts to implement against):
  - `backend/config.py`: Environment variable names (DB_HOST, WEATHER_API_KEY, etc.)
  - `backend/app.py`: Flask app configuration loading

  **Test References** (testing patterns to follow):
  - No existing tests for Docker — create simple smoke test: container starts, health endpoint responds

  **External References** (libraries and frameworks):
  - Docker multi-stage build examples: https://docs.docker.com/develop/develop-images/multistage-build/
  - Flask Docker deployment guides

  **WHY Each Reference Matters**:
  - `backend/config.py`: To know which environment variables the app expects
  - `backend/app.py`: To understand app entry point and configuration loading

  **Acceptance Criteria**:

  **If TDD (tests enabled):**
  - [ ] Test file created: `tests/test_docker.py` with basic container smoke test
  - [ ] `pytest tests/test_docker.py -v` → PASS (container builds and starts)

  **QA Scenarios (MANDATORY — task is INCOMPLETE without these):**

  ```
  Scenario: Docker build succeeds
    Tool: Bash (docker)
    Preconditions: Docker daemon running, project directory clean
    Steps:
      1. Run `docker build -t context-app:test -f Dockerfile .`
      2. Wait for build to complete (timeout: 120s)
      3. Verify exit code is 0
      4. Verify image created: `docker image inspect context-app:test`
    Expected Result: Build succeeds without errors, image exists
    Failure Indicators: Build fails, missing dependencies, syntax errors
    Evidence: .sisyphus/evidence/task-1-docker-build.log

  Scenario: Docker-compose up starts service
    Tool: Bash (docker-compose)
    Preconditions: Docker build completed, .env file with minimal config (mock DB vars)
    Steps:
      1. Copy .env.example to .env.test and fill dummy values
      2. Run `docker-compose -f docker-compose.yml --env-file .env.test up -d`
      3. Wait 15 seconds for startup
      4. Run `docker-compose ps` → verify service status "Up"
      5. Run `curl -f http://localhost:5000/api/health || echo "Health endpoint not yet implemented"` (allow 404)
    Expected Result: Container starts, service runs, health endpoint responds (200 or 404)
    Failure Indicators: Container exits with error, ports not exposed
    Evidence: .sisyphus/evidence/task-1-docker-compose.log
  ```

  **Evidence to Capture**:
  - [ ] `task-1-docker-build.log` — full build output
  - [ ] `task-1-docker-compose.log` — compose logs and curl output

  **Commit**: YES (group with Wave 1)
  - Message: `feat(infra): Docker multi-stage build + docker-compose`
  - Files: `Dockerfile`, `docker-compose.yml`, `.env.example`
  - Pre-commit: `docker build .` (dry run)

- [ ] 2. **Database schema design + SQL scripts**

  **What to do**:
  - Design MariaDB schema: tables `user`, `category`, `favorite`, `session`
  - Create SQL migration script `schema.sql` with CREATE TABLE statements
  - Include indexes, foreign keys, constraints (unique usernames/emails)
  - Document schema decisions in `DATABASE_SCHEMA.md`

  **Must NOT do**:
  - No ORM code yet (SQLAlchemy models in separate task)
  - No data migration from JSON

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: SQL schema design is straightforward, no complex logic
  - **Skills**: None
  - **Skills Evaluated but Omitted**:
    - `git-master`: Not needed for schema design

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1,3-7)
  - **Blocks**: Task 4 (authentication models), Task 5 (category/favorite models)
  - **Blocked By**: None

  **References**:

  **Pattern References**:
  - No existing database schema — design from requirements
  - Reference: Flask-SQLAlchemy model patterns (to be created in later tasks)

  **API/Type References**:
  - Draft decisions: User fields (id, username, email, password_hash, created_at, is_admin)
  - Draft decisions: Category fields (id, user_id, name, color, display_order)
  - Draft decisions: Favorite fields (id, user_id, category_id, url, title, domain, logo_filename, tipo, display_order, created_at)
  - Draft decisions: Session fields (Flask-Session will manage)

  **Test References**:
  - No existing tests — will be tested via SQLAlchemy models later

  **External References**:
  - MariaDB/MySQL CREATE TABLE syntax
  - Flask-SQLAlchemy documentation for model definitions

  **WHY Each Reference Matters**:
  - Draft decisions: To ensure schema matches agreed-upon structure

  **Acceptance Criteria**:

  **If TDD (tests enabled):**
  - [ ] Test file: `tests/test_schema.sql` (validation via connection test)
  - [ ] `pytest tests/test_schema.py -v` → PASS (schema can be applied)

  **QA Scenarios**:

  ```
  Scenario: SQL schema validates
    Tool: Bash (mysql client)
    Preconditions: MariaDB accessible via test credentials
    Steps:
      1. Connect to test database: `mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD $DB_NAME`
      2. Execute `schema.sql` 
      3. Verify no syntax errors
      4. Run `SHOW TABLES;` → expect user, category, favorite, session tables
      5. Describe each table structure
    Expected Result: Tables created with correct columns and constraints
    Failure Indicators: Syntax errors, missing tables, constraint failures
    Evidence: .sisyphus/evidence/task-2-schema-output.log

  Scenario: Foreign key constraints work
    Tool: Bash (mysql client)
    Preconditions: Schema applied, test database empty
    Steps:
      1. Insert test user
      2. Insert category with user_id reference
      3. Insert favorite with user_id and category_id references
      4. Verify constraints allow valid inserts
      5. Attempt invalid insert (non-existent user_id) → expect failure
    Expected Result: Constraints enforce referential integrity
    Failure Indicators: Invalid inserts succeed
    Evidence: .sisyphus/evidence/task-2-constraints.log
  ```

  **Evidence to Capture**:
  - [ ] `task-2-schema-output.log` — schema application output
  - [ ] `task-2-constraints.log` — constraint validation

  **Commit**: YES (group with Wave 1)
  - Message: `feat(db): MariaDB schema design + SQL scripts`
  - Files: `schema.sql`, `DATABASE_SCHEMA.md`
  - Pre-commit: `mysql --execute="SOURCE schema.sql"` (dry run on test DB)

- [ ] 3. **Basic Flask app restructuring (config, blueprints)**

  **What to do**:
  - Restructure `backend/app.py` into blueprints: `auth`, `api`, `admin`
  - Update config loading to use environment variables consistently
  - Create `backend/__init__.py` factory pattern: `create_app()`
  - Ensure existing endpoints (`/api/data`, `/api/favorites`) still work

  **Must NOT do**:
  - No authentication logic yet (just structure)
  - No breaking changes to existing API responses

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Code restructuring is mechanical, following Flask patterns
  - **Skills**: None
  - **Skills Evaluated but Omitted**:
    - `playwright`: No UI changes

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: Task 8 (auth endpoints), Task 12 (admin panel), Task 22 (integration)
  - **Blocked By**: Task 1 (Docker) optional, but can start

  **References**:

  **Pattern References**:
  - `backend/app.py:1-50` — current Flask app structure
  - `backend/config.py` — current config loading
  - Flask blueprint examples: https://flask.palletsprojects.com/en/2.3.x/blueprints/

  **API/Type References**:
  - Existing endpoints: `/api/data` (GET), `/api/favorites` (GET, POST, DELETE)
  - Need to maintain same response formats

  **Test References**:
  - No existing tests — create basic blueprint structure tests

  **External References**:
  - Flask application factory pattern

  **WHY Each Reference Matters**:
  - `backend/app.py`: To understand current monolithic structure before refactoring
  - `backend/config.py`: To preserve config variable names

  **Acceptance Criteria**:

  **If TDD (tests enabled):**
  - [ ] Test file: `tests/test_app_structure.py`
  - [ ] `pytest tests/test_app_structure.py -v` → PASS (blueprints register correctly)

  **QA Scenarios**:

  ```
  Scenario: Existing endpoints still work after refactor
    Tool: Bash (curl)
    Preconditions: Flask app running locally (development server)
    Steps:
      1. Start app: `cd backend && python app.py` (or use refactored version)
      2. Wait for startup
      3. `curl http://localhost:5000/api/data` → expect JSON with dolar/weather data
      4. `curl http://localhost:5000/api/favorites` → expect JSON array (empty or existing favorites)
      5. Verify response status codes are 200
    Expected Result: All existing endpoints return same data format as before
    Failure Indicators: 404 errors, changed response structure
    Evidence: .sisyphus/evidence/task-3-endpoints.log

  Scenario: Blueprints are registered
    Tool: Bash (curl)
    Preconditions: App running
    Steps:
      1. `curl http://localhost:5000/api/` → 404 (no root API endpoint)
      2. Check app routes via Flask debug if available
    Expected Result: App starts without errors, blueprints exist
    Failure Indicators: Import errors, missing routes
    Evidence: .sisyphus/evidence/task-3-blueprints.log
  ```

  **Evidence to Capture**:
  - [ ] `task-3-endpoints.log` — curl outputs
  - [ ] `task-3-blueprints.log` — app startup logs

  **Commit**: YES (group with Wave 1)
  - Message: `refactor(app): Flask blueprints + application factory`
  - Files: `backend/__init__.py`, `backend/app.py`, `backend/auth/__init__.py`, `backend/api/__init__.py`, `backend/admin/__init__.py`
  - Pre-commit: `pytest tests/test_app_structure.py`

- [ ] 4. **Authentication models (User, Session)**

  **What to do**:
  - Create SQLAlchemy models in `backend/models.py` or `backend/models/` directory
  - Models: `User`, `Session` (for Flask-Session)
  - Define relationships: User ↔ Category, User ↔ Favorite
  - Add password hashing utility using bcrypt

  **Must NOT do**:
  - No authentication endpoints yet (just models)
  - No login/logout logic

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: SQLAlchemy model definition is straightforward
  - **Skills**: None
  - **Skills Evaluated but Omitted**:
    - `playwright`: No UI

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: Task 8 (registration), Task 9 (login), Task 10 (session middleware)
  - **Blocked By**: Task 2 (schema) — needs table definitions

  **References**:

  **Pattern References**:
  - `schema.sql` (Task 2) — table structures to mirror
  - SQLAlchemy model examples from Flask documentation

  **API/Type References**:
  - Flask-SQLAlchemy field types: String, Integer, DateTime, Boolean, etc.
  - Flask-Bcrypt for password hashing

  **Test References**:
  - No existing tests — create model unit tests

  **External References**:
  - Flask-SQLAlchemy quickstart: https://flask-sqlalchemy.palletsprojects.com/en/3.1.x/quickstart/
  - Flask-Bcrypt documentation

  **WHY Each Reference Matters**:
  - `schema.sql`: Ensures models match database schema exactly

  **Acceptance Criteria**:

  **If TDD (tests enabled):**
  - [ ] Test file: `tests/test_models.py`
  - [ ] `pytest tests/test_models.py -v` → PASS (models can be created, relationships work)

  **QA Scenarios**:

  ```
  Scenario: User model creation and password hashing
    Tool: Bash (python REPL)
    Preconditions: Database accessible, models imported
    Steps:
      1. Create User instance: `user = User(username='test', email='test@example.com')`
      2. Set password: `user.set_password('TestPass123')`
      3. Verify password hash is not plaintext
      4. Verify `user.check_password('TestPass123')` returns True
      5. Verify `user.check_password('Wrong')` returns False
    Expected Result: Password hashing works, verification functions correctly
    Failure Indicators: Plaintext storage, verification fails
    Evidence: .sisyphus/evidence/task-4-model-test.log

  Scenario: Database persistence
    Tool: Bash (python REPL)
    Preconditions: Test database empty
    Steps:
      1. Create and add user to session
      2. Commit
      3. Query user back
      4. Verify attributes match
    Expected Result: Models can be persisted and retrieved
    Failure Indicators: SQL errors, missing columns
    Evidence: .sisyphus/evidence/task-4-persistence.log
  ```

  **Evidence to Capture**:
  - [ ] `task-4-model-test.log` — REPL session output
  - [ ] `task-4-persistence.log` — database interaction logs

  **Commit**: YES (group with Wave 1)
  - Message: `feat(models): SQLAlchemy User, Session models + password hashing`
  - Files: `backend/models.py` or `backend/models/` directory
  - Pre-commit: `pytest tests/test_models.py`

- [ ] 5. **Category & Favorite models (SQLAlchemy)**

  **What to do**:
  - Create SQLAlchemy models for `Category` and `Favorite` in `backend/models.py`
  - Define relationships: Category ↔ Favorite (one-to-many), Category ↔ User (many-to-one), Favorite ↔ User (many-to-one)
  - Add utility methods: `Category.reorder_favorites()`, `Favorite.move_to_category()`
  - Ensure fields match schema (Task 2): display_order, tipo, logo_filename, etc.

  **Must NOT do**:
  - No CRUD endpoints yet
  - No frontend integration

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Model definitions follow patterns from Task 4
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: Task 15 (category CRUD), Task 16 (favorite CRUD), Task 20 (drag‑and‑drop backend)
  - **Blocked By**: Task 2 (schema), Task 4 (User model)

  **References**:
  - `schema.sql` (Task 2) — column definitions
  - `backend/models.py` (Task 4) — pattern for SQLAlchemy models
  - Flask‑SQLAlchemy relationship documentation

  **Acceptance Criteria**:
  - [ ] Test file: `tests/test_category_favorite_models.py`
  - [ ] `pytest tests/test_category_favorite_models.py -v` → PASS

  **QA Scenarios**:

  ```
  Scenario: Category‑Favorite relationships
    Tool: Bash (python REPL)
    Preconditions: Database with User, Category, Favorite tables
    Steps:
      1. Create user, category, favorite
      2. Associate favorite with category and user
      3. Verify `category.favorites` list includes favorite
      4. Verify `favorite.category` returns category
      5. Verify `user.categories` and `user.favorites` relationships
    Expected Result: Relationships work bidirectionally
    Evidence: .sisyphus/evidence/task-5-relationships.log

  Scenario: Display order handling
    Tool: Bash (python REPL)
    Preconditions: Category with several favorites
    Steps:
      1. Set `display_order` values (1,2,3)
      2. Query favorites ordered by display_order
      3. Verify order matches assignment
      4. Update order and verify persistence
    Expected Result: Ordering persists and can be changed
    Evidence: .sisyphus/evidence/task-5-ordering.log
  ```

  **Evidence to Capture**:
  - [ ] `task-5-relationships.log`
  - [ ] `task-5-ordering.log`

  **Commit**: YES (group with Wave 1)
  - Message: `feat(models): Category & Favorite SQLAlchemy models`
  - Files: `backend/models.py` (extended)
  - Pre‑commit: `pytest tests/test_category_favorite_models.py`

- [ ] 6. **Logos volume setup + default logos download**

  **What to do**:
  - Create directory `/logos` at project root (if not exists)
  - Configure Docker volume in `docker‑compose.yml` to mount `/logos` inside container
  - Write script `scripts/download_default_logos.py` to fetch logos for default sites (Google, GitHub, etc.)
  - Store logos as `{domain}.ico` or `{domain}.png` in `/logos`
  - Document logo naming convention: domain‑based, reusable across users

  **Must NOT do**:
  - No per‑user logo storage — all logos shared
  - No real‑time logo scraping in this task (keep existing scraping in favorites service)

  **Recommended Agent Profile**:
  - **Category**: `unspecified‑high`
    - Reason: Requires external HTTP requests, error handling, file I/O
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: Task 17 (default data seeding)
  - **Blocked By**: Task 1 (Docker volume definition)

  **References**:
  - `favorites/logos/` current location (if exists) — examine naming pattern
  - `backend/services/favorites.py` — existing logo scraping logic
  - Default sites list: Google, GitHub, YouTube, Twitter, Facebook, Gmail, Outlook

  **Acceptance Criteria**:
  - [ ] Logos directory exists and is writable
  - [ ] Docker volume mounts correctly (`docker‑compose up` shows logos inside container)
  - [ ] Script downloads logos for all 7 default sites (success or graceful failure)

  **QA Scenarios**:

  ```
  Scenario: Logos directory accessible
    Tool: Bash (ls, docker run)
    Preconditions: Docker volume configured
    Steps:
      1. Run `docker‑compose up -d`
      2. Execute `docker‑compose exec app ls /logos`
      3. Verify directory exists and contains expected logo files
    Expected Result: Logos directory mounted, files present
    Evidence: .sisyphus/evidence/task-6-logos-dir.log

  Scenario: Default logos downloaded
    Tool: Bash (python script)
    Preconditions: Script `download_default_logos.py` ready
    Steps:
      1. Run script with `python scripts/download_default_logos.py`
      2. Check exit code is 0
      3. Verify each default site has a logo file in `/logos`
    Expected Result: Logos downloaded (or skipped with appropriate warning)
    Evidence: .sisyphus/evidence/task-6-download.log
  ```

  **Evidence to Capture**:
  - [ ] `task‑6‑logos‑dir.log`
  - [ ] `task‑6‑download.log`

  **Commit**: YES (group with Wave 1)
  - Message: `feat(logos): volume setup + default logos download`
  - Files: `scripts/download_default_logos.py`, `docker‑compose.yml` (volume), `/logos/` (logo files)
  - Pre‑commit: `python scripts/download_default_logos.py --dry‑run`

- [ ] 7. **Test infrastructure setup (pytest, fixtures)**

  **What to do**:
  - Install pytest, Flask‑Testing, pytest‑cov, pytest‑mock (add to `requirements.txt`)
  - Create `tests/` directory with `conftest.py` defining fixtures: `app`, `db`, `client`, `test_user`
  - Set up test database (SQLite in‑memory or separate MariaDB test instance)
  - Configure pytest coverage reporting (`pytest.ini` or `pyproject.toml`)
  - Write basic smoke test to verify test environment works

  **Must NOT do**:
  - No feature tests yet (only infrastructure)
  - No production database modifications

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Standard pytest configuration
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: All TDD tasks (8‑31) depend on test infrastructure
  - **Blocked By**: None

  **References**:
  - Existing `requirements.txt` (if any) — add test dependencies
  - Flask testing guide: https://flask.palletsprojects.com/en/2.3.x/testing/
  - pytest fixture patterns

  **Acceptance Criteria**:
  - [ ] `pytest --version` runs without error
  - [ ] `pytest tests/` runs existing tests (if any) or passes empty suite
  - [ ] Coverage configured (can generate report)

  **QA Scenarios**:

  ```
  Scenario: Pytest runs basic test
    Tool: Bash (pytest)
    Preconditions: Test infrastructure installed
    Steps:
      1. Create minimal test `tests/test_smoke.py` with `def test_smoke(): assert True`
      2. Run `pytest tests/test_smoke.py -v`
      3. Verify exit code 0, test passes
    Expected Result: Pytest environment functional
    Evidence: .sisyphus/evidence/task-7-pytest.log

  Scenario: Flask app fixture works
    Tool: Bash (pytest)
    Preconditions: `conftest.py` with `app` fixture
    Steps:
      1. Write test that uses `app` fixture
      2. Run test with `pytest -v`
      3. Verify app instance is Flask app, config loaded
    Expected Result: Fixtures provide working app instance
    Evidence: .sisyphus/evidence/task-7-fixtures.log
  ```

  **Evidence to Capture**:
  - [ ] `task‑7‑pytest.log`
  - [ ] `task‑7‑fixtures.log`

  **Commit**: YES (group with Wave 1)
  - Message: `feat(tests): pytest infrastructure + fixtures`
  - Files: `requirements.txt`, `tests/conftest.py`, `pytest.ini`, `tests/test_smoke.py`
  - Pre‑commit: `pytest tests/`

- [ ] 8. **User registration endpoint (TDD)**

  **What to do**:
  - Create `/api/auth/register` POST endpoint (auth blueprint)
  - Accept JSON: `username`, `email`, `password`
  - Validate input (unique username/email, password strength)
  - Hash password with bcrypt, create User record
  - Return JSON: `{ "user_id": ..., "username": ..., "token": ... }` (or session cookie)
  - Write tests first (TDD): test validation, duplicate users, success case

  **Must NOT do**:
  - No email verification
  - No CAPTCHA or rate limiting (basic implementation)

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Requires careful validation, error handling, security considerations
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on Task 3,4,7)
  - **Parallel Group**: Wave 2 (sequential within wave)
  - **Blocks**: Task 9 (login), Task 14 (auth integration tests)
  - **Blocked By**: Task 3 (blueprints), Task 4 (User model), Task 7 (test infra)

  **References**:
  - `backend/auth/__init__.py` blueprint structure (Task 3)
  - `backend/models.py` User model (Task 4)
  - Flask‑Login registration patterns
  - Existing `/api/favorites` POST endpoint for request handling example

  **Acceptance Criteria**:
  - [ ] Test file: `tests/test_auth_register.py` with 5+ tests
  - [ ] `pytest tests/test_auth_register.py -v` → PASS
  - [ ] Endpoint returns 201 on success, 400 on invalid input, 409 on duplicate

  **QA Scenarios**:

  ```
  Scenario: Successful registration
    Tool: Bash (curl)
    Preconditions: Flask app running, database empty
    Steps:
      1. `curl -X POST http://localhost:5000/api/auth/register -H "Content-Type: application/json" -d '{"username":"newuser","email":"new@example.com","password":"SecurePass123"}'`
      2. Verify status code 201
      3. Verify response contains user_id and username
      4. Verify user exists in database (SELECT * FROM user)
    Expected Result: User created, password hashed, appropriate response
    Evidence: .sisyphus/evidence/task-8-register-success.log

  Scenario: Duplicate username rejected
    Tool: Bash (curl)
    Preconditions: User "testuser" already exists
    Steps:
      1. Attempt registration with same username
      2. Verify status code 409 (or 400)
      3. Verify error message indicates conflict
    Expected Result: Registration rejected, no duplicate created
    Evidence: .sisyphus/evidence/task-8-duplicate.log
  ```

  **Evidence to Capture**:
  - [ ] `task‑8‑register‑success.log`
  - [ ] `task‑8‑duplicate.log`

  **Commit**: YES (group with Wave 2)
  - Message: `feat(auth): user registration endpoint`
  - Files: `backend/auth/routes.py`, `tests/test_auth_register.py`
  - Pre‑commit: `pytest tests/test_auth_register.py`

- [ ] 9. **Login/logout endpoints (TDD)**

  **What to do**:
  - Create `/api/auth/login` POST endpoint (auth blueprint)
  - Accept JSON: `username`, `password`
  - Verify credentials, create session (Flask‑Login)
  - Return session token or set cookie
  - Create `/api/auth/logout` POST endpoint to invalidate session
  - TDD: test invalid credentials, successful login, logout

  **Must NOT do**:
  - No OAuth or social login
  - No "remember me" functionality beyond 7‑day session

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Security‑sensitive, session management
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on Task 8)
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 10 (session middleware), Task 14 (auth integration)
  - **Blocked By**: Task 8 (registration)

  **References**:
  - `backend/auth/routes.py` (Task 8) — pattern for endpoint
  - Flask‑Login `login_user()`, `logout_user()` methods
  - Existing authentication patterns (if any)

  **Acceptance Criteria**:
  - [ ] Test file: `tests/test_auth_login.py` with 5+ tests
  - [ ] `pytest tests/test_auth_login.py -v` → PASS
  - [ ] Login returns 200 + token/cookie, invalid credentials return 401
  - [ ] Logout invalidates session

  **QA Scenarios**:

  ```
  Scenario: Valid login
    Tool: Bash (curl)
    Preconditions: User "testuser" with password "TestPass123" exists
    Steps:
      1. `curl -X POST http://localhost:5000/api/auth/login -H "Content-Type: application/json" -d '{"username":"testuser","password":"TestPass123"}'`
      2. Verify status 200, response contains token/session identifier
      3. Verify session cookie set (if using cookies)
    Expected Result: Successful login, session established
    Evidence: .sisyphus/evidence/task-9-login-success.log

  Scenario: Invalid password rejected
    Tool: Bash (curl)
    Preconditions: User "testuser" exists
    Steps:
      1. Attempt login with wrong password
      2. Verify status 401, no session created
    Expected Result: Login fails with appropriate error
    Evidence: .sisyphus/evidence/task-9-login-fail.log
  ```

  **Evidence to Capture**:
  - [ ] `task‑9‑login‑success.log`
  - [ ] `task‑9‑login‑fail.log`

  **Commit**: YES (group with Wave 2)
  - Message: `feat(auth): login/logout endpoints`
  - Files: `backend/auth/routes.py` (extended), `tests/test_auth_login.py`
  - Pre‑commit: `pytest tests/test_auth_login.py`

- [ ] 10. **Session middleware (Flask‑Session + MariaDB)**

  **What to do**:
  - Configure Flask‑Session with SQLAlchemy backend (store sessions in MariaDB)
  - Set session lifetime to 7 days (refresh on activity)
  - Integrate with Flask‑Login for session management
  - Ensure session persistence across server restarts
  - Write tests for session expiry and renewal

  **Must NOT do**:
  - No client‑side session storage (cookies only for session ID)
  - No custom session serialization (use default)

  **Recommended Agent Profile**:
  - **Category**: `unspecified‑high`
    - Reason: Configuration‑heavy, integration of multiple libraries
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on Task 9)
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 14 (auth integration), Task 25 (session expiration handling)
  - **Blocked By**: Task 9 (login), Task 4 (Session model)

  **References**:
  - Flask‑Session documentation: https://flask-session.readthedocs.io/
  - Session table schema (Task 2)
  - Flask‑Login session integration guide

  **Acceptance Criteria**:
  - [ ] Session stored in database (check `session` table)
  - [ ] Session persists after server restart
  - [ ] Automatic expiry after 7 days inactivity
  - [ ] Tests: `tests/test_session.py`

  **QA Scenarios**:

  ```
  Scenario: Session created on login
    Tool: Bash (curl + mysql)
    Preconditions: User logged in (Task 9)
    Steps:
      1. Query `session` table — should contain entry for user
      2. Verify session data includes user_id, expiry timestamp
    Expected Result: Session record exists in DB
    Evidence: .sisyphus/evidence/task-10-session-db.log

  Scenario: Session expires after inactivity
    Tool: Bash (curl + manual time adjustment or mocking)
    Preconditions: Session created
    Steps:
      1. Wait/mock 7 days + 1 minute
      2. Attempt authenticated request with session
      3. Verify 401/redirect to login
    Expected Result: Session invalidated after expiry
    Evidence: .sisyphus/evidence/task-10-expiry.log
  ```

  **Evidence to Capture**:
  - [ ] `task‑10‑session‑db.log`
  - [ ] `task‑10‑expiry.log`

  **Commit**: YES (group with Wave 2)
  - Message: `feat(auth): Flask‑Session with MariaDB backend`
  - Files: `backend/config.py` (session config), `tests/test_session.py`
  - Pre‑commit: `pytest tests/test_session.py`

- [ ] 11. **Password hashing (bcrypt) + security utilities**

  **What to do**:
  - Integrate Flask‑Bcrypt or use `bcrypt` directly
  - Add password strength validation (min length, complexity)
  - Create utility module `backend/auth/security.py` with `hash_password`, `check_password`, `validate_password_strength`
  - Ensure no plaintext passwords in logs or responses
  - Add security headers middleware (optional)

  **Must NOT do**:
  - No custom encryption algorithms
  - No password recovery logic (separate task)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Straightforward integration of bcrypt
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES (depends on Task 4)
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 8 (registration) already uses hashing, but this centralizes
  - **Blocked By**: Task 4 (User model with password hashing)

  **References**:
  - Flask‑Bcrypt documentation
  - OWASP password recommendations

  **Acceptance Criteria**:
  - [ ] Utility functions work (hash/verify)
  - [ ] Password strength validation rejects weak passwords
  - [ ] Tests: `tests/test_security.py`

  **QA Scenarios**:

  ```
  Scenario: Password hashing and verification
    Tool: Bash (python REPL)
    Preconditions: Security utilities imported
    Steps:
      1. Hash password "TestPass123"
      2. Verify hash matches same password
      3. Verify hash does NOT match different password
    Expected Result: Hash/verify functions work correctly
    Evidence: .sisyphus/evidence/task-11-hash-verify.log

  Scenario: Password strength validation
    Tool: Bash (python REPL)
    Preconditions: `validate_password_strength` function
    Steps:
      1. Test "weak" → should fail
      2. Test "StrongPass123" → should pass
    Expected Result: Validation enforces minimum requirements
    Evidence: .sisyphus/evidence/task-11-strength.log
  ```

  **Evidence to Capture**:
  - [ ] `task‑11‑hash‑verify.log`
  - [ ] `task‑11‑strength.log`

  **Commit**: YES (group with Wave 2)
  - Message: `feat(auth): password hashing + security utilities`
  - Files: `backend/auth/security.py`, `tests/test_security.py`
  - Pre‑commit: `pytest tests/test_security.py`

- [ ] 12. **Admin panel backend (CRUD users)**

  **What to do**:
  - Create `/api/admin/users` GET endpoint (admin blueprint) — list users (paginated)
  - Create `/api/admin/users` POST endpoint — create user (admin‑only)
  - Create `/api/admin/users/<id>` DELETE endpoint — delete user
  - Add admin authentication middleware (check `is_admin` flag)
  - Ensure only users with `is_admin=True` can access
  - TDD: test admin access, non‑admin denied

  **Must NOT do**:
  - No frontend UI yet (backend only)
  - No user editing endpoint (just create/delete/list)

  **Recommended Agent Profile**:
  - **Category**: `unspecified‑high`
    - Reason: Requires authorization logic, careful permission checks
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on Task 3,8,9)
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 13 (admin frontend), Task 26 (password reset)
  - **Blocked By**: Task 3 (admin blueprint), Task 8/9 (auth)

  **References**:
  - `backend/admin/__init__.py` blueprint (Task 3)
  - Existing CRUD patterns from `/api/favorites`
  - Flask‑Login `current_user.is_authenticated` and `current_user.is_admin`

  **Acceptance Criteria**:
  - [ ] Test file: `tests/test_admin_users.py` with 5+ tests
  - [ ] `pytest tests/test_admin_users.py -v` → PASS
  - [ ] Non‑admin users get 403, admin can list/create/delete

  **QA Scenarios**:

  ```
  Scenario: Admin user list
    Tool: Bash (curl)
    Preconditions: Admin user exists (is_admin=True), regular user exists
    Steps:
      1. Login as admin, get token
      2. `curl -H "Authorization: Bearer <token>" http://localhost:5000/api/admin/users`
      3. Verify response includes user list
    Expected Result: Admin can list users
    Evidence: .sisyphus/evidence/task-12-admin-list.log

  Scenario: Non‑admin denied
    Tool: Bash (curl)
    Preconditions: Regular user (is_admin=False) logged in
    Steps:
      1. Attempt to access `/api/admin/users`
      2. Verify status 403
    Expected Result: Access forbidden for non‑admin
    Evidence: .sisyphus/evidence/task-12-nonadmin-denied.log
  ```

  **Evidence to Capture**:
  - [ ] `task‑12‑admin‑list.log`
  - [ ] `task‑12‑nonadmin‑denied.log`

  **Commit**: YES (group with Wave 2)
  - Message: `feat(admin): user CRUD backend`
  - Files: `backend/admin/routes.py`, `tests/test_admin_users.py`
  - Pre‑commit: `pytest tests/test_admin_users.py`

- [ ] 13. **Admin panel frontend (basic UI)**

  **What to do**:
  - Create admin UI page `admin.html` (or section within existing UI)
  - Fetch user list from `/api/admin/users` and display in table
  - Add "Create User" form (username, email, password, admin checkbox)
  - Add delete button next to each user (with confirmation)
  - Style to match existing design (light/dark theme)
  - Ensure UI only accessible to admin users (redirect if not admin)

  **Must NOT do**:
  - No advanced filtering/search
  - No bulk operations

  **Recommended Agent Profile**:
  - **Category**: `visual‑engineering`
    - Reason: UI implementation, styling, integration with existing frontend
  - **Skills**: `playwright` (for QA scenarios)
  - **Skills Evaluated but Omitted**:
    - `git‑master`: Not needed

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on Task 12)
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 26 (password reset UI)
  - **Blocked By**: Task 12 (admin backend)

  **References**:
  - `frontend/index.html` — existing HTML structure
  - `frontend/css/styles.css` — styling patterns
  - `frontend/js/app.js` — JavaScript patterns for API calls

  **Acceptance Criteria**:
  - [ ] Admin page accessible at `/admin` (or via menu)
  - [ ] User table loads and displays data
  - [ ] Create user form works, delete buttons work
  - [ ] Non‑admin users redirected or shown "access denied"

  **QA Scenarios**:

  ```
  Scenario: Admin page loads for admin user
    Tool: Playwright
    Preconditions: Admin user logged in
    Steps:
      1. Navigate to `/admin`
      2. Wait for page load
      3. Assert page contains "User Management" header
      4. Assert user table is visible
    Expected Result: Admin page renders correctly
    Evidence: .sisyphus/evidence/task-13-admin-page.png

  Scenario: Non‑admin cannot access admin page
    Tool: Playwright
    Preconditions: Regular user logged in
    Steps:
      1. Navigate to `/admin`
      2. Assert redirect to login or "access denied" message
    Expected Result: Admin page blocked for non‑admin
    Evidence: .sisyphus/evidence/task-13-nonadmin-blocked.png
  ```

  **Evidence to Capture**:
  - [ ] `task‑13‑admin‑page.png` (screenshot)
  - [ ] `task‑13‑nonadmin‑blocked.png`

  **Commit**: YES (group with Wave 2)
  - Message: `feat(admin): basic admin frontend UI`
  - Files: `frontend/admin.html`, `frontend/js/admin.js`, `frontend/css/admin.css` (or extensions)
  - Pre‑commit: `pytest tests/test_admin_frontend.py` (if frontend tests exist)

- [ ] 14. **Authentication integration tests**

  **What to do**:
  - Write comprehensive integration tests covering full auth flow: register → login → protected endpoint → logout
  - Test edge cases: expired sessions, invalid tokens, concurrent sessions
  - Test admin vs non‑admin access controls
  - Ensure all auth‑related tests pass together

  **Must NOT do**:
  - No new production code — only tests

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Requires deep understanding of authentication flow, edge cases
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on Tasks 8‑13)
  - **Parallel Group**: Wave 2 (final task of wave)
  - **Blocks**: Wave 3 can start after this
  - **Blocked By**: Tasks 8‑13 completed

  **References**:
  - All previous auth task test files
  - Integration testing patterns (Flask‑Testing)

  **Acceptance Criteria**:
  - [ ] Test file: `tests/test_auth_integration.py` with 10+ tests
  - [ ] `pytest tests/test_auth_integration.py -v` → PASS
  - [ ] All auth tests combined pass (no conflicts)

  **QA Scenarios**:

  ```
  Scenario: Full auth flow
    Tool: Bash (curl)
    Preconditions: Clean database
    Steps:
      1. Register new user
      2. Login with credentials
      3. Access protected endpoint (e.g., `/api/favorites`)
      4. Logout
      5. Attempt protected endpoint → should fail
    Expected Result: Complete flow works end‑to‑end
    Evidence: .sisyphus/evidence/task-14-auth-flow.log

  Scenario: Admin middleware integration
    Tool: Bash (curl)
    Preconditions: Admin user and regular user exist
    Steps:
      1. Regular user attempts admin endpoint → 403
      2. Admin user attempts admin endpoint → 200
    Expected Result: Admin middleware correctly restricts access
    Evidence: .sisyphus/evidence/task-14-admin-middleware.log
  ```

  **Evidence to Capture**:
  - [ ] `task‑14‑auth‑flow.log`
  - [ ] `task‑14‑admin‑middleware.log`

  **Commit**: YES (group with Wave 2)
  - Message: `test(auth): comprehensive integration tests`
  - Files: `tests/test_auth_integration.py`
  - Pre‑commit: `pytest tests/test_auth_integration.py`

- [ ] 15. **Category CRUD endpoints (TDD)**
  **What to do**: Endpoints GET/POST/PUT/DELETE for categories, ownership validation, default category handling.
  **Must NOT do**: No color management, no bulk ops.
  **Recommended Agent Profile**: `deep` (business logic). **Parallelization**: Depends on Task 5,9. Wave 3.
  **References**: Category model (Task 5), default categories list.
  **Acceptance Criteria**: Tests pass, endpoints return correct status codes.
  **QA Scenarios**: 
  ```
  Scenario: Create and list categories
    Tool: Bash (curl)
    Steps: POST category, GET verify.
    Evidence: .sisyphus/evidence/task-15-crud.log
  Scenario: Ownership enforcement
    Tool: Bash (curl)
    Steps: User A tries to delete User B's category → 403.
    Evidence: .sisyphus/evidence/task-15-ownership.log
  ```
  **Commit**: YES (Wave 3).

- [ ] 16. **Favorite CRUD with category association (TDD)**
  **What to do**: Update existing `/api/favorites` to accept `category_id`, PUT for updates, validate category ownership.
  **Must NOT do**: No bulk updates.
  **Recommended Agent Profile**: `deep`. **Parallelization**: Depends on Task 15. Wave 3.
  **References**: Favorite model (Task 5), category endpoints (Task 15).
  **Acceptance Criteria**: Tests pass, backward compatibility maintained.
  **QA Scenarios**:
  ```
  Scenario: Create favorite with category
    Tool: Bash (curl)
    Steps: POST with category_id, GET verify.
    Evidence: .sisyphus/evidence/task-16-create.log
  Scenario: Update category
    Tool: Bash (curl)
    Steps: PUT with new category_id, GET verify.
    Evidence: .sisyphus/evidence/task-16-update.log
  ```
  **Commit**: YES (Wave 3).

- [ ] 17. **Default categories & sites seeding**
  **What to do**: Script `seed_defaults.py` creates default categories and favorites for new users, idempotent.
  **Must NOT do**: No seeding for existing users.
  **Recommended Agent Profile**: `quick`. **Parallelization**: Depends on Tasks 5,6,15,16. Wave 3.
  **References**: Default lists, logo naming.
  **Acceptance Criteria**: New user gets defaults, no duplicates.
  **QA Scenarios**:
  ```
  Scenario: New user gets defaults
    Tool: Bash (curl + script)
    Steps: Register user, run script, verify categories/favorites exist.
    Evidence: .sisyphus/evidence/task-17-seed.log
  Scenario: Idempotency
    Tool: Bash (script)
    Steps: Run script twice, verify no duplicates.
    Evidence: .sisyphus/evidence/task-17-idempotent.log
  ```
  **Commit**: YES (Wave 3).

- [ ] 18. **Frontend category selector in "Agregar Sitio" panel**
  **What to do**: Add dropdown to add‑site panel, load categories from API, include category_id in POST.
  **Must NOT do**: No drag‑and‑drop UI yet.
  **Recommended Agent Profile**: `visual‑engineering` (playwright). **Parallelization**: Depends on Task 15. Wave 3.
  **References**: Existing panel HTML/JS.
  **Acceptance Criteria**: Selector appears, populated, works.
  **QA Scenarios**:
  ```
  Scenario: Selector loads categories
    Tool: Playwright
    Steps: Open panel, assert dropdown contains categories.
    Evidence: .sisyphus/evidence/task-18-selector.png
  Scenario: Add favorite with category
    Tool: Playwright
    Steps: Fill form, select category, save, verify.
    Evidence: .sisyphus/evidence/task-18-add.png
  ```
  **Commit**: YES (Wave 3).

- [ ] 19. **Display category tags on cards**
  **What to do**: Modify `createFavoriteCard()` to show category tag, style badges.
  **Must NOT do**: No editing on card.
  **Recommended Agent Profile**: `visual‑engineering` (playwright). **Parallelization**: Depends on Task 18. Wave 3.
  **References**: Existing card CSS/JS.
  **Acceptance Criteria**: All cards show tags, tags styled.
  **QA Scenarios**:
  ```
  Scenario: Cards show tags
    Tool: Playwright
    Steps: Load page, assert each card has tag.
    Evidence: .sisyphus/evidence/task-19-tags.png
  Scenario: Tag matches category
    Tool: Playwright
    Steps: Verify specific card tag text.
    Evidence: .sisyphus/evidence/task-19-tag-text.png
  ```
  **Commit**: YES (Wave 3).

- [ ] 20. **Drag‑and‑drop backend (order persistence)**
  **What to do**: Endpoint `PUT /api/favorites/reorder` updates `display_order` and `category_id`, transactional.
  **Must NOT do**: No real‑time collaboration.
  **Recommended Agent Profile**: `unspecified‑high`. **Parallelization**: Depends on Tasks 5,16. Wave 3.
  **References**: Favorite model with display_order.
  **Acceptance Criteria**: Tests pass, order persists.
  **QA Scenarios**:
  ```
  Scenario: Reorder within category
    Tool: Bash (curl)
    Steps: Send reorder request, GET verify new order.
    Evidence: .sisyphus/evidence/task-20-reorder.log
  Scenario: Move between categories
    Tool: Bash (curl)
    Steps: Send move request, GET verify new category.
    Evidence: .sisyphus/evidence/task-20-move.log
  ```
  **Commit**: YES (Wave 3).

- [ ] 21. **Sortable.js integration + UI drag handlers**
  **What to do**: Include Sortable.js, initialize on grid, send reorder requests on drag end.
  **Must NOT do**: No nested drag, touch optimizations.
  **Recommended Agent Profile**: `visual‑engineering` (playwright). **Parallelization**: Depends on Tasks 19,20. Wave 3.
  **References**: Sortable.js docs, reorder endpoint.
  **Acceptance Criteria**: Drag‑and‑drop works, order persists.
  **QA Scenarios**:
  ```
  Scenario: Drag reorders favorites
    Tool: Playwright
    Steps: Drag card, wait for network request, refresh verify order.
    Evidence: .sisyphus/evidence/task-21-drag.png
  Scenario: Move card to another category
    Tool: Playwright
    Steps: Drag between sections, verify network request, refresh verify category.
    Evidence: .sisyphus/evidence/task-21-move.png
  ```
  **Commit**: YES (Wave 3).

- [ ] 22. **Integrate authentication with existing favorites endpoints**
  **What to do**: Modify existing `/api/favorites` endpoints to require authentication, filter by current user.
  **Must NOT do**: No change to data format.
  **Recommended Agent Profile**: `deep`. **Parallelization**: Depends on Tasks 8,9,16. Wave 4.
  **Acceptance Criteria**: Authenticated users see only their favorites, unauthenticated get 401.
  **QA Scenarios**:
  ```
  Scenario: Authenticated access
    Tool: Bash (curl)
    Steps: Login, GET /api/favorites → see user's favorites.
    Evidence: .sisyphus/evidence/task-22-auth.log
  Scenario: Unauthenticated rejected
    Tool: Bash (curl)
    Steps: GET without token → 401.
    Evidence: .sisyphus/evidence/task-22-unauth.log
  ```
  **Commit**: YES (Wave 4).

- [ ] 23. **Update currency/weather services to work with new structure**
  **What to do**: Ensure `/api/data` endpoint still works with new app structure (blueprints, auth). No authentication required.
  **Must NOT do**: No change to data sources.
  **Recommended Agent Profile**: `quick`. **Parallelization**: Depends on Task 3. Wave 4.
  **Acceptance Criteria**: `/api/data` returns currency/weather data as before.
  **QA Scenarios**:
  ```
  Scenario: Public data accessible
    Tool: Bash (curl)
    Steps: GET /api/data → JSON with dolar and weather keys.
    Evidence: .sisyphus/evidence/task-23-data.log
  ```
  **Commit**: YES (Wave 4).

- [ ] 24. **Frontend auth state management (login/logout UI)**
  **What to do**: Add login/logout buttons, show username, hide/show "Agregar Sitio" panel based on auth.
  **Must NOT do**: No complex state library.
  **Recommended Agent Profile**: `visual‑engineering` (playwright). **Parallelization**: Depends on Tasks 8,9. Wave 4.
  **Acceptance Criteria**: UI reflects login state, buttons work.
  **QA Scenarios**:
  ```
  Scenario: Login UI updates
    Tool: Playwright
    Steps: Login, assert username shown, logout button visible.
    Evidence: .sisyphus/evidence/task-24-ui.png
  Scenario: Logout works
    Tool: Playwright
    Steps: Click logout, assert UI returns to login state.
    Evidence: .sisyphus/evidence/task-24-logout.png
  ```
  **Commit**: YES (Wave 4).

- [ ] 25. **Session expiration handling (frontend + backend)**
  **What to do**: Frontend detects 401, redirects to login. Backend returns 401 for expired sessions.
  **Must NOT do**: No silent refresh.
  **Recommended Agent Profile**: `unspecified‑high`. **Parallelization**: Depends on Task 10. Wave 4.
  **Acceptance Criteria**: Expired session triggers logout UI.
  **QA Scenarios**:
  ```
  Scenario: Expired session redirect
    Tool: Playwright
    Steps: Wait for expiry (or mock), attempt authenticated request, assert redirect to login.
    Evidence: .sisyphus/evidence/task-25-expiry.png
  ```
  **Commit**: YES (Wave 4).

- [ ] 26. **Admin panel password reset functionality**
  **What to do**: Endpoint `/api/admin/users/<id>/reset‑password` allows admin to set new password for user.
  **Must NOT do**: No email notification.
  **Recommended Agent Profile**: `deep`. **Parallelization**: Depends on Tasks 12,13. Wave 4.
  **Acceptance Criteria**: Admin can reset password, user can login with new password.
  **QA Scenarios**:
  ```
  Scenario: Admin resets password
    Tool: Bash (curl)
    Steps: Admin resets user password, user logs in with new password.
    Evidence: .sisyphus/evidence/task-26-reset.log
  ```
  **Commit**: YES (Wave 4).

- [ ] 27. **Comprehensive integration tests**
  **What to do**: Write integration tests covering full multi‑user scenario: two users, categories, favorites, drag‑and‑drop, admin operations.
  **Must NOT do**: No production code.
  **Recommended Agent Profile**: `deep`. **Parallelization**: Depends on all previous tasks. Wave 4 (final).
  **Acceptance Criteria**: Integration test suite passes.
  **QA Scenarios**:
  ```
  Scenario: Multi‑user isolation
    Tool: Bash (curl)
    Steps: User A creates favorite, User B cannot see it.
    Evidence: .sisyphus/evidence/task-27-isolation.log
  Scenario: Full admin flow
    Tool: Bash (curl)
    Steps: Admin creates user, resets password, deletes user.
    Evidence: .sisyphus/evidence/task-27-admin-flow.log
  ```
  **Commit**: YES (Wave 4).

- [ ] 28. **End‑to‑end tests with Playwright**
  **What to do**: Create Playwright tests that simulate real user interactions: register, login, add favorites, categorize, drag‑and‑drop, logout.
  **Must NOT do**: No unit tests.
  **Recommended Agent Profile**: `unspecified‑high` (playwright). **Parallelization**: Depends on all frontend tasks. Wave 5.
  **Acceptance Criteria**: Playwright tests pass.
  **QA Scenarios**:
  ```
  Scenario: Full user journey
    Tool: Playwright
    Steps: Register, login, add favorite, assign category, reorder, logout.
    Evidence: .sisyphus/evidence/task-28-e2e.png
  ```
  **Commit**: YES (Wave 5).

- [ ] 29. **Performance & security audit**
  **What to do**: Run security scan (bandit, safety), check for common vulnerabilities (SQL injection, XSS). Performance: ensure no N+1 queries, optimize where needed.
  **Must NOT do**: No deep penetration testing.
  **Recommended Agent Profile**: `deep`. **Parallelization**: Depends on all backend tasks. Wave 5.
  **Acceptance Criteria**: No critical security issues, performance acceptable.
  **QA Scenarios**:
  ```
  Scenario: Security scan
    Tool: Bash (bandit)
    Steps: Run bandit on backend code, report high‑severity issues.
    Evidence: .sisyphus/evidence/task-29-security.log
  ```
  **Commit**: YES (Wave 5).

- [ ] 30. **Docker production readiness (health checks, logging)**
  **What to do**: Add health check endpoint `/api/health`, configure Docker healthcheck, improve logging (structured JSON), ensure graceful shutdown.
  **Must NOT do**: No orchestration (Kubernetes).
  **Recommended Agent Profile**: `quick`. **Parallelization**: Depends on Task 1. Wave 5.
  **Acceptance Criteria**: Health endpoint returns 200, Docker healthcheck passes.
  **QA Scenarios**:
  ```
  Scenario: Health endpoint
    Tool: Bash (curl)
    Steps: GET /api/health → 200 with status.
    Evidence: .sisyphus/evidence/task-30-health.log
  ```
  **Commit**: YES (Wave 5).

- [ ] 31. **Documentation & deployment instructions**
  **What to do**: Write `DEPLOYMENT.md` with steps: environment variables, database setup, Docker deployment, troubleshooting. Update README.
  **Must NOT do**: No internal API documentation.
  **Recommended Agent Profile**: `writing`. **Parallelization**: Depends on all tasks. Wave 5.
  **Acceptance Criteria**: Documentation exists and is clear.
  **QA Scenarios**:
  ```
  Scenario: Documentation exists
    Tool: Bash (ls)
    Steps: Verify DEPLOYMENT.md and updated README.md exist.
    Evidence: .sisyphus/evidence/task-31-docs.log
  ```
  **Commit**: YES (Wave 5).

---

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> 4 review agents run in PARALLEL. ALL must APPROVE. Rejection → fix → re-run.

- [ ] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists (read file, curl endpoint, run command). For each "Must NOT Have": search codebase for forbidden patterns — reject with file:line if found. Check evidence files exist in .sisyphus/evidence/. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [ ] F2. **Code Quality Review** — `unspecified-high`
  Run `tsc --noEmit` + linter + `bun test`. Review all changed files for: `as any`/`@ts-ignore`, empty catches, console.log in prod, commented-out code, unused imports. Check AI slop: excessive comments, over-abstraction, generic names (data/result/item/temp).
  Output: `Build [PASS/FAIL] | Lint [PASS/FAIL] | Tests [N pass/N fail] | Files [N clean/N issues] | VERDICT`

- [ ] F3. **Real Manual QA** — `unspecified-high` (+ `playwright` skill if UI)
  Start from clean state. Execute EVERY QA scenario from EVERY task — follow exact steps, capture evidence. Test cross-task integration (features working together, not isolation). Test edge cases: empty state, invalid input, rapid actions. Save to `.sisyphus/evidence/final-qa/`.
  Output: `Scenarios [N/N pass] | Integration [N/N] | Edge Cases [N tested] | VERDICT`

- [ ] F4. **Scope Fidelity Check** — `deep`
  For each task: read "What to do", read actual diff (git log/diff). Verify 1:1 — everything in spec was built (no missing), nothing beyond spec was built (no creep). Check "Must NOT do" compliance. Detect cross-task contamination: Task N touching Task M's files. Flag unaccounted changes.
  Output: `Tasks [N/N compliant] | Contamination [CLEAN/N issues] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

- **Commits por wave**: Cada wave se puede commitear como grupo
- **Mensajes**: `feat(auth): user registration endpoint`, `feat(categories): CRUD backend`, etc.
- **Pre-commit**: `pytest` debe pasar antes de commitear código nuevo

---

## Success Criteria

### Verification Commands
```bash
# 1. Docker build and run
docker-compose up --build -d
sleep 10
curl -f http://localhost:5000/api/health

# 2. User registration and login
curl -X POST http://localhost:5000/api/auth/register -H "Content-Type: application/json" -d '{"username":"testuser","password":"TestPass123","email":"test@example.com"}'
curl -X POST http://localhost:5000/api/auth/login -H "Content-Type: application/json" -d '{"username":"testuser","password":"TestPass123"}'

# 3. Categories default present
curl -H "Authorization: Bearer <token>" http://localhost:5000/api/categories

# 4. Drag-and-drop persists order
# (UI test via Playwright - see QA scenarios)

# 5. Existing functionality works
curl http://localhost:5000/api/data | jq '.dolar | has("oficial")'
curl http://localhost:5000/api/data | jq '.weather | has("temperature")'

# 6. Tests pass
pytest --cov=backend --cov-report=term-missing
```

### Final Checklist
- [ ] Docker-compose levanta sin errores
- [ ] Usuario puede registrarse e iniciar sesión
- [ ] Sesión persiste por 7 días (cookie/DB)
- [ ] Categorías default presentes y editables
- [ ] Drag-and-drop funciona y persiste orden
- [ ] Panel admin accesible con ADMIN_PASSWORD
- [ ] Funcionalidades existentes (divisas, clima) operativas
- [ ] Tests pasan con cobertura >80%
- [ ] Agent-Executed QA Scenarios completados (evidencias en `.sisyphus/evidence/`)
