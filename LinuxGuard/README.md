<div align="center">

# 🛡️ LinuxGuard

### Intelligent Linux Security & Performance Monitoring

**A modern, local-first Linux dashboard built with Python, JavaScript, and SQLite.**

![Python](https://img.shields.io/badge/Python-3.10%2B-3670A0?logo=python&logoColor=white)
![Linux](https://img.shields.io/badge/Platform-Linux-1f2937?logo=linux&logoColor=white)
![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-65e7b5)
![Security](https://img.shields.io/badge/Mode-Read--Only-65e7b5)

*A second-year software engineering portfolio project.*

</div>

---

## ✨ Overview

**LinuxGuard** helps you understand what is happening on your Linux computer. It collects system telemetry, shows live charts, highlights sustained resource problems, and offers an optional **read-only security audit**. Everything runs locally: there is no cloud account, remote collection service, or API key.

> **Scope:** LinuxGuard is a learning and observability tool, **not** an antivirus, intrusion-prevention system, or full vulnerability scanner.

## 🚀 Features

| Category | What you get |
|---|---|
| 📈 Live telemetry | CPU, RAM, root disk usage, network transfer rates, uptime |
| 📊 Interactive dashboard | Responsive dark UI; automatic refresh every 5 seconds |
| 🧠 Explainable anomaly signals | CPU baseline with sustained-spike detection; memory/disk thresholds |
| 🔍 Process explorer | Top visible processes by resource usage, including PID |
| 🔐 SSH audit | Attempts to count failed SSH logins from the last hour via systemd journal |
| 🌐 Listening-port check | Shows locally visible services bound to network interfaces |
| 💡 Recommendations | Practical next steps when utilization is high |
| 🗂️ Event storage | Local SQLite history and deduplicated alert events |
| 🔒 Local-only server | Binds to `127.0.0.1` by default; no login or public exposure |

## 🧰 Technology Stack

- **Backend:** Python 3.10+ and built-in `http.server` (no Flask required)
- **System monitoring:** `psutil`
- **Database:** SQLite 3 (Python standard library)
- **Frontend:** HTML5, CSS3, vanilla JavaScript, SVG charts
- **Security audit:** `journalctl` and local socket information, where permitted
- **Testing:** Python `unittest` and GitHub Actions

## ⚙️ Getting Started (Ubuntu / Debian)

### 1. Install prerequisites

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git
```

### 2. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/LinuxGuard.git
cd LinuxGuard
```

**Before publishing:** replace `YOUR_USERNAME` with your real GitHub username.

### 3. Create the virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Launch LinuxGuard

```bash
python3 app.py
```

Open **http://127.0.0.1:8088** in your browser.

The dashboard starts collecting telemetry automatically. Press **Run scan** to check the available SSH journal and listening ports on demand.

To use another local port:

```bash
LINUXGUARD_PORT=8090 python3 app.py
```

> For Fedora, Arch, and other distributions, install `python3`, `pip`, and `git` using your package manager, then follow steps 2–4.

## 🗂️ Repository Structure

```text
LinuxGuard/
├── app.py                    # Local HTTP server and JSON API
├── monitor.py                # psutil collector and anomaly signals
├── security.py               # Read-only security audit
├── storage.py                # SQLite storage and alert deduplication
├── index.html                # Dashboard HTML
├── static/
│   ├── styles.css            # Responsive dark UI
│   └── app.js                # Live charts, tables, and API calls
├── tests/                    # Automated unit and API tests
├── .github/workflows/ci.yml  # GitHub Actions CI
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md
```

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/status` | Latest metrics, health score, processes, and system info |
| `GET` | `/api/history?limit=60` | Recent stored telemetry samples |
| `GET` | `/api/alerts` | Recent alert events |
| `POST` | `/api/security-scan` | Run local, read-only security checks |

Example:

```bash
curl http://127.0.0.1:8088/api/status
curl -X POST http://127.0.0.1:8088/api/security-scan
```

## 🧠 How Anomaly Detection Works

LinuxGuard uses **explainable statistical thresholds**, rather than claiming to use a trained AI model:

1. Collect a fresh CPU reading every five seconds.
2. After eight normal readings, compute a baseline of `mean + 2 × standard deviation` (bounded from 70% to 95%). Until then, use an 85% threshold.
3. Flag **sustained CPU spikes** after three consecutive high readings.
4. Flag RAM use at or above 90% for two readings, and root disk use at or above 90%.
5. Write alerts to SQLite and suppress duplicate events for five minutes.

These are **resource signals, not proof of malicious activity**. Some measurements can be restricted or unavailable depending on your Linux distribution and account permissions.

## 🔐 Safety & Privacy

- The server is restricted to localhost (`127.0.0.1`); do **not** expose it directly to the internet.
- LinuxGuard performs read-only checks. It does not terminate processes, change firewall settings, or attempt exploitation.
- The security audit may show **N/A** for SSH failures when journald, SSH services, or journal permissions are unavailable. A value of zero is **not** a guarantee that no attack occurred.
- The app doesn't need root privileges. **Avoid running the dashboard with `sudo`** just to read protected logs.
- Runtime history is stored in `data/linuxguard.sqlite3`, a local ignored file. The database is **not committed to Git**.
- Process and host information are not uploaded anywhere by the app.

## ✅ Run Tests

```bash
python3 -m unittest discover -s tests -v
```

On GitHub, tests run automatically for every push and pull request using the supplied workflow.

## 💡 Future Improvements

- Optional alert notifications via email or Telegram
- Exportable reports and longer-term metrics
- Authentication for deliberate multi-user deployments
- Configurable thresholds and an audit history page
- Container deployment for controlled testing

## 📤 Publish to Your GitHub

After extracting the ZIP, make a **new public repository named `LinuxGuard`** on GitHub (do not initialize it with a README), then run:

```bash
cd LinuxGuard
git init
git add .
git commit -m "Initial commit: LinuxGuard monitoring dashboard"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/LinuxGuard.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your own GitHub username. You may also upload the extracted files using **GitHub → Add file → Upload files** (upload the contents of the `LinuxGuard` folder, not the ZIP itself).

## 📜 License

Distributed under the [MIT License](LICENSE). You can use and modify this project for learning and your portfolio.

---

<div align="center">

**Made for exploring Linux observability and defensive system administration.**

⭐ If you find the project useful, give the repository a star!

</div>
