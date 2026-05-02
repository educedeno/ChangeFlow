# ChangeFlow

Sistema para gestionar y controlar solicitudes de cambios técnicos internos — configuraciones, integraciones, permisos críticos y despliegues manuales — con flujo de aprobación, trazabilidad y auditoría.

---

## Caso de negocio

Las empresas de tecnología realizan cambios técnicos frecuentes (ajustes de configuración, nuevas integraciones, modificaciones de permisos, despliegues manuales) que hoy se coordinan por Slack, correo o llamadas. Esto genera falta de trazabilidad, cambios sin aprobación formal y dificultad para hacer rollback cuando algo falla.

**ChangeFlow** digitaliza ese proceso: un Engineer propone el cambio con su plan de rollback, un Approver lo revisa y aprueba o rechaza, y el sistema registra cada acción con auditoría completa.

---

## Integrantes

| Nombre | Responsabilidad |
|---|---|
| **Emilio Puga** | Discovery y reglas de negocio |
| **Jorge Marcillo** | Requerimientos y diagramas UML |
| **Pablo Galarza** | Repositorio y GitHub Project |
| **Eduardo Cedeño** | GitHub Actions, Render y documentación |

---

## Stack técnico

| Componente | Tecnología |
|---|---|
| Backend | FastAPI (Python 3.11) |
| Frontend | Streamlit |
| Base de datos | PostgreSQL 15 |
| ORM | SQLAlchemy + Alembic |
| Infra local | Docker Compose |
| CI/CD | GitHub Actions + Docker Hub + Render |
| Arquitectura | Hexagonal (Domain / Application / Infrastructure / API) |

---

## Arquitectura

```
frontend/                          backend/
  app/                               app/
    main.py      ──HTTP──►             api/          ← rutas y dependencias
    pages/                             application/  ← casos de uso y DTOs
      login.py                         domain/       ← entidades, eventos, interfaces
      dashboard.py                     infrastructure/ ← ORM, repos, DB
      create_request.py
      request_detail.py
```

El dominio **no depende** de FastAPI, SQLAlchemy ni Streamlit. Los casos de uso dependen solo de interfaces (repositorios abstractos). La infraestructura implementa esas interfaces con SQLAlchemy.

### Flujo principal

```
Engineer → crea solicitud (DRAFT)
         → envía (SUBMITTED)
Approver → revisa → aprueba (APPROVED) o rechaza (REJECTED)
Sistema  → publica evento → notifica → registra auditoría
```

### Estados de una solicitud

```
DRAFT ──► SUBMITTED ──► IN_REVIEW ──► APPROVED
                                  └──► REJECTED ──► DRAFT (puede reenviarse)
```

---

## Correr localmente

### Prerequisitos

- Docker Desktop instalado y corriendo
- Git

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/educedeno/ChangeFlow.git
cd ChangeFlow

# 2. Levantar todos los servicios
docker compose up --build

# 3. Acceder a la aplicación
#    Frontend:  http://localhost:8501
#    Backend:   http://localhost:8000
#    API docs:  http://localhost:8000/docs
#    DB:        localhost:5432  (user: user / password: password / db: appdb)
```

### Detener los servicios

```bash
docker compose down
```

### Detener y limpiar la base de datos

```bash
docker compose down -v
```

---

## Flujo de CI/CD

El pipeline está definido en `.github/workflows/ci-cd.yml` y tiene tres jobs:

### 1. `lint-test` — se ejecuta en todo evento

Corre en cualquier PR a `dev` y en cualquier push. Instala `ruff` y `pytest`, corre lint sobre `backend/` y `frontend/`, y ejecuta los tests en `backend/app/tests/`. Mientras no haya código real, ambos pasos son best-effort (`|| true`) para que el pipeline no bloquee.

### 2. `build-and-push` — solo en push (no en PR)

Construye y publica las dos imágenes en Docker Hub en paralelo usando matrix strategy:

| Evento | Imágenes publicadas |
|---|---|
| Push a `dev` | `changeflow-backend:dev`, `changeflow-frontend:dev` |
| Push de tag `vX.Y.Z` a `main` | `changeflow-backend:prod`, `changeflow-backend:vX.Y.Z`, `changeflow-frontend:prod`, `changeflow-frontend:vX.Y.Z` |

### 3. `deploy-render` — corre después de `build-and-push`

Dispara los deploy hooks de Render vía `curl` para redeployar los servicios correspondientes:

| Evento | Servicios redeployados |
|---|---|
| Push a `dev` | backend-dev, frontend-dev |
| Push de tag `vX.Y.Z` | backend-prod, frontend-prod |

> Los deploys a producción **solo ocurren con un tag** — nunca desde una rama feature directamente.

### Secrets requeridos en GitHub

| Secret | Descripción |
|---|---|
| `DOCKERHUB_USERNAME` | Usuario de Docker Hub |
| `DOCKERHUB_TOKEN` | Personal Access Token de Docker Hub |
| `RENDER_DEV_BACKEND_HOOK` | Deploy hook del backend en Render dev |
| `RENDER_DEV_FRONTEND_HOOK` | Deploy hook del frontend en Render dev |
| `RENDER_PROD_BACKEND_HOOK` | Deploy hook del backend en Render prod |
| `RENDER_PROD_FRONTEND_HOOK` | Deploy hook del frontend en Render prod |

---

## Ambientes desplegados

| Ambiente | Backend | Frontend |
|---|---|---|
| **Dev** | https://changeflow-backend-dev.onrender.com | https://changeflow-frontend-dev.onrender.com |
| **Prod** | https://changeflow-backend-prod.onrender.com | https://changeflow-frontend-prod.onrender.com |

> Los links se actualizan una vez que los servicios de Render estén activos (Issues 3 y 4).

---

## Documentación adicional

- [`docs/discovery.md`](docs/discovery.md) — Discovery, requerimientos y reglas de negocio
- [`docs/uml/sequence_diagram.puml`](docs/uml/sequence_diagram.puml) — Flujos críticos del sistema
- [`docs/uml/use_case.puml`](docs/uml/use_case.puml) — Casos de uso por actor
- [`docs/uml/class_diagram.puml`](docs/uml/class_diagram.puml) — Entidades y relaciones