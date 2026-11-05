# CommunityPulse — Community Development Tracker

A browser-based website using Python Flask, HTML templates, CSS, a small JavaScript enhancement for automatic filtering, and SQLite.

## Run in VS Code (Windows)
1. Extract the ZIP and open this folder in VS Code.
2. In Terminal, create a virtual environment:
   `py -m venv .venv`
3. Activate it:
   `.venv\Scripts\Activate.ps1`
4. Install Flask:
   `python -m pip install -r requirements.txt`
5. Create an account with the private command-line account manager:
   `flask --app main create-user you@example.com`
   Enter the password when prompted; it is not shown or included in shell history.
6. Run the app:
   `python main.py`
7. Open `http://127.0.0.1:5000` in your browser and log in.

If `py` is unavailable, try `python` instead. If PowerShell blocks activation, use the terminal's Command Prompt profile and run `.venv\Scripts\activate.bat`.

Registration is disabled on the website. All dashboard and project pages require login, and accounts can only be created from the trusted machine using the command above. Run the command again for each additional authorized user. For deployments beyond local development, set a persistent, private `SECRET_KEY` environment variable before starting the app so sessions stay valid across restarts.

## Files
- `main.py`: app entry point and routes; run only this file.
- `database.py`: SQLite queries and seed data.
- `templates/base.html`: shared layout.
- `templates/index.html`: dashboard, search/filter and add-project form.
- `templates/project.html`: individual project details and delete form.
- `static/css/style.css`: all styling and responsive layout.
- `requirements.txt`: Flask dependency.

## Features
- Project summary dashboard.
- Search by project name, location or description.
- Automatic project filtering as you type or change categories.
- Project-specific images for the sample projects.
- Board and team hierarchy with member portraits, roles and contribution years.
- Add projects with server-side validation.
- Project details page and delete action.
- Private login and logout with securely hashed passwords; account creation is CLI-only.
- SQLite persistence.
- Responsive styling.

Sample project data is illustrative and should not be treated as official reporting.
