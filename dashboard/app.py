import json
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template
from flask_wtf.csrf import CSRFProtect  # type: ignore[import-untyped]

# Load environment variables
_ = load_dotenv()

app = Flask(__name__)
# Use environment variable for secret key, fallback to a default only in dev
app.secret_key = os.getenv("DASHBOARD_SECRET_KEY", "dev-secret-key-change-me")
csrf = CSRFProtect(app)

# Path to the reports directory — resolved to absolute canonical path
REPORTS_DIR = str(Path(__file__).resolve().parent.parent / "reports")


def _safe_report_path(filename: str) -> str | None:
    """Validate and return a safe absolute path within REPORTS_DIR.

    Returns None if the resolved path escapes the reports directory.
    """
    if not filename or ".." in filename or "/" in filename or os.path.sep in filename:
        return None

    # Resolve to canonical absolute path and verify it stays inside REPORTS_DIR
    candidate = os.path.realpath(os.path.join(REPORTS_DIR, filename))
    if not candidate.startswith(os.path.realpath(REPORTS_DIR) + os.sep):
        return None

    if not candidate.endswith(".json"):
        return None

    return candidate


@app.route("/", methods=["GET"])
def index():
    """Serve the dashboard index page."""
    return render_template("index.html")


@app.route("/api/reports", methods=["GET"])
def get_reports():
    """Return a JSON list of report summaries."""
    reports: list[dict[str, str]] = []
    if os.path.exists(REPORTS_DIR):
        for entry in os.listdir(REPORTS_DIR):
            safe_path = _safe_report_path(entry)
            if safe_path is None:
                continue
            with open(safe_path, "r") as f:
                try:
                    data: dict[str, str] = json.load(f)
                    reports.append(
                        {
                            "id": entry,
                            "timestamp": data.get(
                                "timestamp", datetime.now().isoformat()
                            ),
                            "type": data.get("type", "unknown"),
                            "summary": data.get("summary", "No summary available"),
                        }
                    )
                except json.JSONDecodeError:
                    continue
    # Sort reports by timestamp descending
    reports.sort(key=lambda x: x["timestamp"], reverse=True)
    return jsonify(reports)


@app.route("/api/report/<filename>", methods=["GET"])
def get_report_detail(filename: str):
    """Return the full JSON content of a single report."""
    safe_path = _safe_report_path(filename)
    if safe_path is None:
        return jsonify({"error": "Invalid filename"}), 400

    if os.path.exists(safe_path):
        with open(safe_path, "r") as f:
            try:
                data: dict[str, str] = json.load(f)
                return jsonify(data)
            except json.JSONDecodeError:
                return jsonify({"error": "Invalid report format"}), 400
    return jsonify({"error": "Report not found"}), 404


if __name__ == "__main__":
    port = int(os.getenv("DASHBOARD_PORT", "5001"))
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug_mode, port=port)
