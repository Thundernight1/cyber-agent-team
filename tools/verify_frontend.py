import os

# Check for environment variables in app.py
with open("dashboard/app.py", "r") as f:
    content = f.read()
    if "os.getenv" not in content:
        print("FAIL: dashboard/app.py does not seem to use environment variables.")
    else:
        print("PASS: dashboard/app.py uses environment variables.")

# Check for XSS protection in templates
with open("dashboard/templates/index.html", "r") as f:
    content = f.read()
    if "|safe" in content:
        print(
            "WARNING: Found '|safe' filter in index.html. Ensure it's used correctly."
        )
    else:
        print(
            "PASS: No '|safe' filter found in index.html, defaulting to Jinja2 auto-escaping."
        )

# Check for Skill/ directory cleanup
if os.path.exists("Skill/src"):
    print("FAIL: Skill/src still exists.")
else:
    print("PASS: Skill/src removed.")
