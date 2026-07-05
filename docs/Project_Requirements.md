# The Bike Inn / Helmwind Cycles

# Bicycle Stock, PDI and Compliance Management System

## Project Overview

### Project Name

Bicycle Stock, PDI and Compliance Management System (BSPCMS)

### Purpose

Develop a cloud-based multi-user web application to manage bicycle and adaptive vehicle inventory throughout its lifecycle:

* Acquisition
* Inspection
* Preparation
* PDI
* Sale
* Compliance record retention

The system must support both:

* The Bike Inn
* Helmwind Cycles

using a single application and shared codebase.

This system will initially operate independently of Bike Book Workshop.

Future integration with Bike Book Workshop APIs may be developed but is explicitly outside the scope of Version 1.

---

# Primary Objectives

The system shall:

1. Manage stock records for all vehicles.
2. Store associated documents and images.
3. Record purchase information.
4. Manage Pre-Delivery Inspections (PDI).
5. Create dynamic inspection checklists based on vehicle type.
6. Support e-bike manufacturer-specific inspection procedures.
7. Maintain full audit trails.
8. Support multiple companies.
9. Support multiple users.
10. Operate entirely via modern web browsers.

---

# Core Design Principles

## Cloud First

The application shall be:

* Browser based
* Mobile friendly
* Tablet friendly
* Hosted in the cloud

No desktop installation required.

---

## Multi Company

The system must support multiple organisations.

Initial organisations:

```
The Bike Inn
Helmwind Cycles
```

Every record must belong to a company.

---

## Auditability

All significant actions shall be recorded:

* Record creation
* Record modification
* PDI completion
* User sign-off
* Status changes

Audit records must not be editable.

---

## Extensibility

The system shall be designed so that future additions can include:

* Bike Book Workshop API
* CRM integration
* Website stock feeds
* Accounting integration
* Training fleet management
* Workshop management

---

# Recommended Technology Stack

## Backend

Python 3.12+

Framework: Django

---

## Database

PostgreSQL

---

## Front End

```
Django Templates
Bootstrap 5
HTMX
```

Avoid React for Version 1.

Simplicity and rapid development are priorities.

---

## Authentication

Django Authentication System.

Support:

```
Email Login
Password Reset
Role Based Access
```

Future:

```
Microsoft Entra ID
Single Sign-On
```

---

## File Storage

Abstraction layer required.

Version 1: Azure Blob Storage

Alternative future option: Microsoft SharePoint

Must not store files directly in PostgreSQL.

---

# User Roles

## Administrator

Full system configuration.

Permissions:

* Manage users
* Manage templates
* Manage companies
* All records

---

## Manager

Permissions:

* Approve PDIs
* Manage stock
* View reports

---

## Technician

Permissions:

* Perform inspections
* Upload documents
* Complete PDIs

---

## Sales User

Permissions:

* View stock
* Manage sales data

---

## Read Only

Permissions:

* Reporting only

---

# Vehicle Categories

## Primary Vehicle Types

Supported categories:

```
Child's Bike
BMX
Hybrid
Road Bike
Gravel Bike
Mountain Bike - Hardtail
Mountain Bike - Full Suspension
Tricycle
Adaptive Light Vehicle
```

---

# Drive Types

Supported drive systems:

```
Conventional
Electrically Assisted
```

---

# Vehicle Record Specification

Every vehicle shall have:

```
Internal Stock Number
Company
Vehicle Type
Drive Type
Manufacturer
Model
Model Year
Colour
Frame Size
Frame Material
Serial Number
Supplier
Purchase Date
Purchase Cost
Recommended Retail Price
Minimum Sale Price
Actual Sale Price
Status
Condition
Notes
```

---

# Vehicle Statuses

```
Acquired
Awaiting Inspection
PDI In Progress
Preparation Required
Ready For Sale
Reserved
Sold
Archived
```

---

# Vehicle Condition Categories

```
New
Used
Ex-Demo
Test Bike
```

---

# Stock Number Format

Format: `PREFIX-YYYY-NNNN`

Examples:

```
TBI-2026-0001
TBI-2026-0002
HWC-2026-0001
```

Stock numbers generated automatically.

---

# Document Management

Each vehicle shall support unlimited attached documents.

Supported formats:

```
PDF
JPG
JPEG
PNG
HEIC
DOCX
XLSX
```

---

# Document Categories

```
Purchase Invoice
Supplier Documentation
PDI Record
Warranty Documentation
Service Documentation
Diagnostic Report
Battery Report
Photos
Sale Documentation
Other
```

---

# PDI System Architecture

The PDI engine is template driven.

A vehicle receives inspection items based upon:

```
Vehicle Type + Drive Type + Drive Manufacturer
```

---

# PDI Structure

## Layer 1 - Universal PDI

Applied to every vehicle.

## Layer 2 - Vehicle Type PDI

Applied according to category.

## Layer 3 - Electric Vehicle PDI

Applied when Drive Type = Electrically Assisted.

## Layer 4 - Manufacturer Specific PDI

Examples: Bosch, Shimano Steps, Mahle, Fazua, Yamaha, TQ, SRAM, Specialized

---

# Digital Sign-Off

All inspections require:

```
Technician Name
Date
Time
Digital Signature
Pass / Fail Result
```

---

# Dashboard Requirements

Users shall see:

```
Vehicles Awaiting PDI
PDI In Progress
Ready For Sale
Sold This Month
Stock Value
Potential Retail Value
Margin Forecast
```

---

# Reporting Requirements

Required reports:

### Inventory Report

Current stock.

### PDI Status Report

Inspection progress.

### Valuation Report

Total stock value.

### Margin Report

Purchase cost versus sales value.

### eBike Report

Battery and diagnostic records.

---

# API Design Requirements

All application functions shall expose REST endpoints.

Use: Django REST Framework

Future integrations must be possible without redesign.

---

# Phase 1 Deliverables

Version 1 shall deliver:

- [x] Authentication
- [x] Multi-company support
- [x] Stock management
- [x] Vehicle records
- [x] Document management
- [x] Image uploads
- [x] User management
- [x] Dashboard
- [x] Reporting

---

# Phase 2 Deliverables

- [x] Dynamic PDI engine
- [x] Template system
- [x] Digital sign-off
- [x] Audit trail

---

# Phase 3 Deliverables

- [x] eBike diagnostics
- [x] Battery records
- [x] Manufacturer-specific modules (template-driven)

---

# Phase 4 Deliverables

- [x] Reporting engine
- [x] KPI dashboards
- [x] Margin analysis

---

# Phase 5 Deliverables

- [ ] Bike Book integration
- [ ] CRM integration
- [ ] Website stock feeds
- [ ] Accounting integrations

---

# Development Standards

Code shall:

* Follow PEP 8
* Use type hints
* Use Django Class Based Views
* Use Django ORM
* Include unit tests
* Include integration tests
* Include migration scripts
* Include comprehensive documentation

Target test coverage: Minimum 80%

---

# Success Criteria

The system shall allow The Bike Inn and Helmwind Cycles to:

1. Manage all bicycle, tricycle, adaptive cycle and electrically assisted vehicle stock.
2. Store all inspection and compliance documentation against a stock item.
3. Produce auditable PDI records.
4. Support multiple companies and users.
5. Operate entirely through the cloud.
6. Provide a foundation for future Bike Book Workshop integration.
