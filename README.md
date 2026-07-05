# Bicycle Stock, PDI and Compliance Management System (BSPCMS)

A cloud-based multi-user web application for managing bicycle and adaptive vehicle inventory from acquisition through to sale.

Built for **The Bike Inn** and **Helmwind Cycles** on a shared, multi-company codebase.

## Features

- **Multi-company support** — The Bike Inn (TBI) and Helmwind Cycles (HWC) share one application
- **Vehicle stock management** — Full lifecycle tracking from acquisition to sale
- **Automatic stock numbers** — Format `TBI-2026-0001` / `HWC-2026-0001`
- **Document management** — Unlimited attachments per vehicle (PDF, images, spreadsheets)
- **Dynamic PDI engine** — Layered inspection checklists by vehicle type + drive system
- **Electric vehicle module** — Motor, battery, charger serial numbers and diagnostics
- **Digital sign-off** — Technician name + timestamp
- **Audit trail** — Immutable log of all significant actions
- **Role-based access** — Administrator, Manager, Technician, Sales, Read Only
- **Dashboard** — Real-time KPIs including stock values and PDI status
- **Reports** — Inventory, PDI status, valuation, margin, eBike
- **REST API** — Django REST Framework endpoints for all modules

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python 3.12 + Django |
| Database | PostgreSQL (SQLite for development) |
| Frontend | Django Templates + Bootstrap 5 + HTMX |
| File storage | Azure Blob Storage (local media in development) |
| Authentication | Django auth + email login |
| API | Django REST Framework |

## Getting Started

### 1. Clone and install dependencies

```bash
git clone https://github.com/JonColborne/Sale-Bicycle-Management.git
cd Sale-Bicycle-Management
pip install -r requirements-dev.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your settings
```

For local development with SQLite (no PostgreSQL required):

```bash
echo "USE_SQLITE=true" >> .env
```

### 3. Run migrations

```bash
python manage.py migrate
```

### 4. Load initial data

```bash
python manage.py loaddata apps/companies/fixtures/initial_companies.json
python manage.py loaddata apps/pdi/fixtures/initial_pdi_templates.json
```

### 5. Create a superuser

```bash
python manage.py createsuperuser
```

### 6. Run the development server

```bash
python manage.py runserver
```

Open http://localhost:8000 — you will be redirected to the dashboard.

## Project Structure

```
├── apps/
│   ├── accounts/       # Custom user model, roles
│   ├── audit/          # Immutable audit trail
│   ├── companies/      # Multi-company management
│   ├── dashboard/      # KPI dashboard
│   ├── documents/      # Document/image management
│   ├── pdi/            # PDI engine, templates, sign-off
│   ├── reports/        # Reporting views and API
│   └── vehicles/       # Stock management
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── api_urls.py
├── docs/
│   └── Project_Requirements.md
├── templates/          # Bootstrap 5 HTML templates
├── tests/              # Unit and integration tests
├── requirements.txt
├── requirements-dev.txt
└── .env.example
```

## Running Tests

```bash
USE_SQLITE=true python -m pytest tests/ -v
```

With coverage:

```bash
USE_SQLITE=true coverage run -m pytest tests/ && coverage report
```

## User Roles

| Role | Create/Edit Stock | PDI | Documents | Users | Reports |
|------|:-----------------:|:---:|:---------:|:-----:|:-------:|
| Administrator | ✅ | ✅ | ✅ | ✅ | ✅ |
| Manager | ✅ | ✅ | ✅ | ❌ | ✅ |
| Technician | ❌ | ✅ | ✅ | ❌ | ✅ |
| Sales | ❌ | ❌ | ❌ | ❌ | ✅ |
| Read Only | ❌ | ❌ | ❌ | ❌ | ✅ |

## REST API

The API is available at `/api/v1/`. Browse it via the Django REST Framework interface.

Key endpoints:

- `GET /api/v1/vehicles/` — List all vehicles (filtered to company)
- `GET /api/v1/vehicles/{id}/` — Get vehicle detail
- `GET /api/v1/vehicles/statistics/` — Stock statistics
- `GET /api/v1/documents/?vehicle={id}` — Vehicle documents
- `GET /api/v1/pdi/templates/` — PDI templates
- `GET /api/v1/reports/valuation/` — Valuation report
- `GET /api/v1/reports/margin/` — Margin report

## PDI Layers

The PDI engine applies templates in layers:

1. **Universal** — Applied to every vehicle (frame, brakes, safety)
2. **Vehicle Type** — Additional checks for the specific category (e.g. Full Suspension MTB adds shock/sag settings)
3. **Electric Vehicle** — Battery, motor, wiring checks for e-bikes
4. **Manufacturer Specific** — Bosch, Shimano Steps, Mahle, Fazua, Yamaha, TQ, SRAM, Specialized

## Production Deployment

Set the following environment variables for production:

```
SECRET_KEY=<long-random-key>
DEBUG=False
ALLOWED_HOSTS=your-domain.com
DB_NAME=bspcms
DB_USER=postgres
DB_PASSWORD=<password>
DB_HOST=<host>
AZURE_ACCOUNT_NAME=<azure-storage-account>
AZURE_ACCOUNT_KEY=<azure-key>
AZURE_CONTAINER=media
DJANGO_SETTINGS_MODULE=config.settings.production
```

## Documentation

See [docs/Project_Requirements.md](docs/Project_Requirements.md) for the full Software Requirements Specification.
