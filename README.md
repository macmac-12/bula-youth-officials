# Bula Youth Officials Portal (Information Management Final Project)

A Flask web application for managing youth officials and organization records with MySQL integration. Developed for Information Management 1 (2nd Semester 2024–2025).

## Features

- **Authentication & Roles**: Admin and visitor roles with route protection and session management.
- **Officials Directory**: Create, read, update, and manage official profiles and positions.
- **Dynamic Frontend**: Modern UI with theme switcher (`theme.js`), custom stylesheet (`style.css`), and Jinja2 templates.
- **MySQL Integration**: Persistent relational data management via `mysql-connector-python`.

## Tech Stack

- **Backend**: Python, Flask
- **Database**: MySQL (`bula_youth_officials`)
- **Frontend**: HTML5, CSS3, JavaScript

## Getting Started

### Prerequisites

- Python 3.10+
- MySQL Server running locally
- Git

### Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd Finals
   ```

2. **Create and activate a virtual environment (optional):**
   ```bash
   python -m venv venv
   # On Windows (PowerShell)
   .\venv\Scripts\Activate.ps1
   # On Linux/macOS
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure MySQL database:**
   Ensure MySQL is running and configure connection settings in `db_config.py` (default host: `localhost`, user: `root`, database: `bula_youth_officials`).

5. **Run the application:**
   ```bash
   python app.py
   ```
   Open your browser at [http://127.0.0.1:5000](http://127.0.0.1:5000).
