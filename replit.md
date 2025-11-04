# Maison d'Hôte - Système de Gestion

## Overview
This project is a comprehensive Flask application designed for managing guest houses. It provides full management capabilities for establishments, bookings (referred to as "séjours"), and clients. The application aims to streamline operations with features like multi-establishment support, detailed séjour management, personnel administration, and financial tracking for extras.

## User Preferences
- I prefer simple language.
- I want iterative development.
- Ask before making major changes.
- I prefer detailed explanations.
- Do not make changes to the folder Z.
- Do not make changes to the file Y.

## System Architecture

### UI/UX Decisions
- **Modern Interface**: Utilizes "dotted border" sections for a clean and structured look.
- **Thematic Colors**: Employs a palette of blue, green, purple, and orange for visual distinction.
- **Responsive Design**: Ensures compatibility across various devices.
- **Sidebar Navigation**: Provides intuitive navigation throughout the application.
- **Alerts and Notifications**: Implements a clear system for user feedback.
- **Consistent Styling**: Global CSS (`frontend/static/css/styles.css`) unifies the appearance of inputs, selects, textareas, and buttons across all pages, with consistent focus and hover effects.
- **Modal Improvements**: Enhanced modals with animations, gradient headers, and improved UX.

### Technical Implementations
- **Backend Framework**: Flask 3.1, leveraging SQLAlchemy for ORM and Flask-Login for user authentication.
- **Database**: PostgreSQL, hosted via Neon, for robust data storage.
- **Frontend**: Primarily vanilla HTML, CSS, and JavaScript for a lightweight and flexible interface.
- **Web Server**: Gunicorn is used to serve the Flask application.
- **Environment**: Developed and deployed using Python 3.11.

### Feature Specifications
- **Multi-Establishment Management**: Supports the creation, modification, and deletion of multiple guest house establishments, each with its own logo and activation status.
- **Séjour Management**: Comprehensive handling of bookings (séjours), including creation, room assignment, client management, and automatic numbering. Renamed from "Réservations" to "Séjours" across the application for consistency.
- **Statistics Page**: A dedicated section for real-time statistics, including séjour overview, client metrics, establishment performance, and room occupancy.
- **Room Management**: Full CRUD operations for rooms, including association with establishments, capacity, pricing, and status (available, occupied, maintenance, out of service).
- **Personnel Management**: Complete system for managing staff, including personal and professional information, granular access permissions, account activation/deactivation, and establishment association.
- **System Parameters**: Centralized management of system-wide settings, including multi-establishment configuration, room management, personnel management, user accounts, and data utilities.
- **Extras Management**: A new, fully integrated system for managing additional services ("extras"). This includes a dedicated `extras` table, `sejours_extras` for linking to séjours, comprehensive CRUD API routes, a dedicated frontend page for listing/adding/editing/deleting extras, summatio n by period, customizable unit prices, and automatic calculation of total amounts for invoices.
- **Séjour Detail Page**: A new page (`/sejour/<id>`) providing a complete overview of a specific séjour, including general information, establishment details, assigned rooms, client lists, billed extras with amounts, and a total financial summary. This page also allows direct addition/removal of extras and optimized printing.
- **Activity Logs System**: Comprehensive activity tracking system that automatically records all user actions with IP addresses, timestamps, routes, HTTP methods, and user agents. Includes a dedicated `activity_logs` table with performance indexes, middleware for automatic logging, API endpoints for filtering and exporting logs, and a complete user interface (`/activity-logs`) for viewing and analyzing user activities. The system is production-ready with input validation and security measures.
- **iCal Calendar Integration**: Existing and functional iCal calendar support for platforms like Airbnb and Booking.com.

### System Design Choices
- **Service-Oriented Architecture**: Refactored backend into `backend/services/` for business logic (e.g., `SejourService`, `ExtraService`) and `backend/utils/` for common utilities (e.g., `serializers.py`, `formatters.py`). This promotes clear separation of concerns: Routes → Services → Models.
- **Database Initialization**: The `init_database.py` script, executed via `start.sh` before Gunicorn, ensures automatic creation of all necessary tables (`users`, `etablissements`, `chambres`, `reservations`, `personnes`, `reservations_chambres`, `extras`, `sejours_extras`, `personnels`, `parametres_systeme`, `activity_logs`, `mail_configs`, `emails`, `calendriers_ical`, `reservations_ical`) and initial data (admin user, default establishment) upon application startup.
- **API Endpoints**: Structured API routes for all major entities (establishments, rooms, séjours, extras, personnel, clients, countries) ensuring comprehensive CRUD capabilities.
- **Frontend Templates**: Organized under `frontend/templates/` with a `base_dashboard.html` for consistent layout and navigation. Specific pages for login, dashboard, statistics, parameters, séjour creation, séjour listing, séjour detail, extras management, client lists, activity logs, and messaging.
- **Static Assets**: CSS and JavaScript files are managed in `frontend/static/` for maintainability, including enhanced styles (`styles.css`) and dedicated scripts for features like séjours and extras.

## External Dependencies
- **PostgreSQL**: Used as the primary relational database, hosted via Neon.
- **Gunicorn**: Production-ready WSGI HTTP server used to run the Flask application.
- **iCal**: Integrated for calendar synchronization with external booking platforms like Airbnb and Booking.com.