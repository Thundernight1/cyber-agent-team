import json
import os
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template

# Load environment variables
load_dotenv()

app = Flask(__name__)
# Use environment variable for secret key, fallback to a default only in dev
app.secret_key = os.getenv("DASHBOARD_SECRET_KEY", "dev-secret-key-change-me")

# Path to the reports directory
REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/reports")
def get_reports():
    reports = []
    if os.path.exists(REPORTS_DIR):
        for filename in os.listdir(REPORTS_DIR):
            if filename.endswith(".json"):
                with open(os.path.join(REPORTS_DIR, filename), "r") as f:
                    try:
                        data = json.load(f)
                        reports.append(
                            {
                                "id": filename,
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


@app.route("/api/report/<filename>")
def get_report_detail(filename):
    # Build path inside the reports directory and normalise it
    filepath = os.path.join(REPORTS_DIR, filename)
    safe_base = os.path.realpath(REPORTS_DIR)
    safe_path = os.path.realpath(filepath)

    # Ensure the resolved path is within the reports directory and has the expected extension
    if not safe_path.startswith(safe_base + os.path.sep) or not filename.endswith(".json"):
        return jsonify({"error": "Invalid filename"}), 400

    if os.path.exists(safe_path):
        with open(safe_path, "r") as f:
            try:
                data = json.load(f)
                return jsonify(data)
            except json.JSONDecodeError:
                return jsonify({"error": "Invalid report format"}), 400
    return jsonify({"error": "Report not found"}), 404


if __name__ == "__main__":
    port = int(os.getenv("DASHBOARD_PORT", 5001))
    app.run(debug=True, port=port)
