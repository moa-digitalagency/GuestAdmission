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
- **Reservation Management:**
    - Automatic calculation of stay duration.
    - Multi-person booking support, identifying a primary contact.
    - Customizable automatic reservation numbering (e.g., `RES-{YYYY}{MM}{DD}-{NUM}`).
- **Client Database:** Centralized management of all registered individuals, including identity and contact details.
- **Room Management:** CRUD operations for rooms, including name, description, capacity, price, and status. Rooms can be assigned to reservations with availability checks.
- **System Settings:** Comprehensive configuration for the establishment (ID, logo URL, contact info, taxes, customizable reservation number format).
- **Dashboard:** Real-time statistics on active reservations, total clients, daily arrivals, and monthly revenue.

### Feature Specifications
- **Authentication:** Secure login, session management, and logout.
- **Reservation Creation:** Capture arrival/departure dates, financial details (accommodation, platform charge, tourist tax), and multiple guest details (name, email, phone, country, ID type/number, date of birth).
- **Reservation View/Edit:** List, view detailed modals, and delete reservations.
- **Client Management:** Overview of all guests, their details, and primary contact status.
- **Room Management:** Creation, listing, and updating of room details.
- **System Parameters:** Configuration of establishment details, contact information, branding, and financial settings.
- **API REST:** A comprehensive API covers authentication, CRUD for reservations, persons, and rooms, and utilities like automatic reservation number generation.

### System Design Choices
- **Modular Structure:** Codebase organized into `backend` (config, models, routes, app) and `frontend` (static, templates) for maintainability.
- **Database Schema:** Defined tables for `users`, `reservations`, `personnes` (persons), `parametres_systeme` (system settings), with appropriate relationships and data types.
- **Automatic DB Initialization:** `init_database.py` script ensures idempotent database and default admin user setup on deployment.
- **Security:** SQL injection protection via parameterized queries, client/server-side validation, secure PostgreSQL connections, and CORS configuration.

## External Dependencies

- **PostgreSQL:** For all data storage.
- **Flask-Login:** User session management and authentication.
- **Flask-CORS:** Handling Cross-Origin Resource Sharing.
- **psycopg2-binary:** PostgreSQL adapter for Python.
- **Gunicorn:** WSGI HTTP Server for deploying Flask.