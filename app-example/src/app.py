#!/usr/bin/env python3
from flask import Flask
from pathlib import Path
import os

app = Flask(__name__)
CREDENTIALS = Path("/secrets/credentials")

def load_secrets():
    s = {"db_con": "mysql.example.com:3306",
         "db_user": "demoUser",
         "db_password": "demoPassword"}
    if CREDENTIALS.exists():
        for line in CREDENTIALS.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            v = v.strip()
            if len(v) >= 2 and v[0] == v[-1] == '"':
                v = v[1:-1]
            s[k.strip()] = v
    return s

SECRETS = load_secrets()

@app.route("/")
def home():
    return f"""<ul>
<li>DB URL: {SECRETS['db_con']}</li>
<li>DB username: {SECRETS['db_user']}</li>
<li>DB password: {SECRETS['db_password']}</li>
</ul>"""

@app.route("/health/live")
def health_live():
    return "up\n"

@app.route("/health/ready")
def health_ready():
    return "yes\n"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)