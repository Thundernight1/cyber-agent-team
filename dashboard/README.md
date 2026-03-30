# Cyber Agent Dashboard

A simple Flask-based dashboard to view and analyze cybersecurity reports.

## Features
- List and view JSON reports from the `reports/` directory.
- Real-time filtering and sorting by timestamp.
- Syntax-highlighted (monospaced) report detail view.

## Security
- **Environment Variables**: Uses `.env` for `DASHBOARD_SECRET_KEY` and `DASHBOARD_PORT`.
- **XSS Protection**: All data injected into the DOM is escaped to prevent Cross-Site Scripting.
- **Path Traversal Protection**: API endpoints validate filenames to prevent unauthorized file access.

## Usage
1. Ensure dependencies are installed: `pip install flask python-dotenv`
2. Run the dashboard: `python app.py`
3. Access at `http://localhost:5001` (default port)