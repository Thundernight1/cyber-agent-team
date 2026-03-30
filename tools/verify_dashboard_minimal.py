import os
import sys


def verify():
    print("Verifying dashboard configuration...")
    # Check for hardcoded secrets in app.py (mock check)
    if os.path.exists("dashboard/app.py"):
        with open("dashboard/app.py", "r") as f:
            content = f.read()
            if "SECRET_KEY = 'hardcoded'" in content:
                print("FAIL: Hardcoded secret found.")
                return False
    print("Dashboard config verification passed.")
    return True


if __name__ == "__main__":
    if not verify():
        sys.exit(1)
