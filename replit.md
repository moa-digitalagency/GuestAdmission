# Système de Gestion de Réservations - Maison d'Hôte

## Overview

This project is a comprehensive reservation management system designed for tourist accommodations like guesthouses and riads. It features an authentication system, multi-person booking capabilities, automatic stay duration calculation, and a modern, responsive interface with a sidebar navigation. The system aims to streamline booking operations, manage client data, and provide real-time insights for business owners.

## User Preferences

I want iterative development. Please ask before making major changes. I prefer detailed explanations for complex features.

## System Architecture

The application is built with a Flask backend and a Jinja2/HTML5/CSS3/Vanilla JS frontend, following a modular project structure.

### UI/UX Decisions
- **Design System:** MOA Design System is applied consistently, featuring dotted borders (3px), a primary blue color palette, modern buttons with shadows, compact `system-ui` typography, and responsive mobile-first design.
- **Navigation:** A professional sidebar with a blue dotted border, fixed menu with icons, and hover effects.
- **Theming:** A modern login page with a violet gradient background.
- **Components:** Responsive grid forms, colored status badges, animated modals, and confirmation alerts.

### Technical Implementations
- **Backend Framework:** Flask (Python 3.11)
- **Frontend Technologies:** HTML5, Jinja2, CSS3 (MOA Design System), Vanilla JavaScript.
- **Database:** PostgreSQL (Replit Managed) managed with psycopg2-binary.
- **CORS:** Handled by Flask-CORS.
- **Authentication:** Secured with Flask-Login, including a default admin account (`admin`/`admin123`).
- **Multi-Establishment Support (NEW):**
    - Dedicated `etablissements` table for managing multiple properties.
    - Each establishment has its own configuration (ID, name, contact info, taxes, branding).
    - Custom reservation numbering format per establishment.
    - All chambres and reservations are linked to specific establishments via foreign keys.
- **Reservation Management:**
    - Automatic calculation of stay duration.
    - Multi-person booking support, identifying a primary contact.
    - Customizable automatic reservation numbering per establishment (e.g., `RES-{YYYY}{MM}{DD}-{NUM}`).
    - **Nouveau:** Field "Numéro de réservation" (replaces "Numéro de séjour").
    - **Nouveau:** Observations field for additional notes and special requests.
    - **Nouveau:** Ville (city) tracking for each guest.
- **Client Database:** Centralized management of all registered individuals, including identity and contact details.
- **Room Management:** 
    - CRUD operations for rooms with establishment assignment.
    - Each room has name, description, capacity, price, and status.
    - **Nouveau:** Room assignment per person using foreign key (chambre_id) instead of text field.
    - Room availability checks per establishment.
- **System Settings:** Comprehensive configuration for establishments (ID, logo URL, contact info, taxes, customizable reservation number format).
- **Dashboard:** Real-time statistics on active reservations, total clients, daily arrivals, and monthly revenue.

### Feature Specifications
- **Authentication:** Secure login, session management, and logout.
- **Establishment Management (NEW):**
    - Create and manage multiple establishments.
    - Each establishment has independent configuration and resources.
    - Automatic establishment initialization on first run.
- **Reservation Creation:** 
    - **First step:** Establishment selection (required).
    - Automatic reservation number generation based on establishment format.
    - Capture arrival/departure dates, financial details (accommodation, platform charge, tourist tax).
    - **Nouveau:** Observations/additional notes field.
    - Multiple guest details (name, email, phone, country, city, ID type/number, date of birth).
    - **Nouveau:** Room assignment dropdown per person (replaces text field).
- **Reservation View/Edit:** List, view detailed modals, and delete reservations.
- **Client Management:** Overview of all guests, their details, and primary contact status.
- **Room Management:** Creation, listing, and updating of room details per establishment.
- **System Parameters:** Configuration of establishment details, contact information, branding, and financial settings (synced with etablissements table).
- **API REST:** A comprehensive API covers authentication, CRUD for reservations, persons, rooms, establishments, and utilities like automatic reservation number generation per establishment.

### System Design Choices
- **Modular Structure:** Codebase organized into `backend` (config, models, routes, app) and `frontend` (static, templates) for maintainability.
- **Database Schema (Updated for Multi-Establishment):**
    - **etablissements:** Main table for establishment data (nom, contact, taxes, format_numero_reservation, etc.)
    - **users:** Authentication and user management
    - **reservations:** Booking records with `etablissement_id` (FK), `numero_reservation`, `observations`, `ville`
    - **personnes:** Guest details with `chambre_id` (FK to chambres), `ville` tracking
    - **chambres:** Room inventory with `etablissement_id` (FK)
    - **reservations_chambres:** Many-to-many relationship between reservations and rooms
    - **parametres_systeme:** System-wide settings (deprecated in favor of etablissements)
- **Automatic DB Initialization:** `init_database.py` script ensures idempotent database setup with default admin user and establishment on deployment.
- **Security:** SQL injection protection via parameterized queries, client/server-side validation, secure PostgreSQL connections, and CORS configuration.

## Recent Changes (November 3, 2025)

### Multi-Establishment Architecture Implementation
- Created `etablissements` table with comprehensive establishment configuration
- Updated all models (Reservation, Personne, Chambre) to support establishment foreign keys
- Migrated from text-based room assignment to proper FK relationship (chambre_id)
- Added automatic reservation number generation per establishment
- Replaced "Numéro de séjour" with "Numéro de réservation" throughout the system

### Enhanced Reservation Form
- Establishment selection as the first required field
- Automatic reservation number generation with manual override option
- Added observations/notes field for special requests
- Room assignment via dropdown for each person (replacing text input)
- Added ville (city) field to person details

### API Enhancements
- `/api/etablissements` - CRUD operations for establishments
- `/api/etablissements/<id>/generer-numero` - Generate reservation numbers per establishment
- Updated `/api/chambres` to filter by establishment
- Updated `/api/reservations` to include establishment context

## External Dependencies

- **PostgreSQL:** For all data storage.
- **Flask-Login:** User session management and authentication.
- **Flask-CORS:** Handling Cross-Origin Resource Sharing.
- **psycopg2-binary:** PostgreSQL adapter for Python.
- **Gunicorn:** WSGI HTTP Server for deploying Flask.