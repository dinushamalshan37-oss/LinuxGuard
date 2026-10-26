 <div align="center">

# 🛡️ LinuxGuard

### Intelligent Linux Security & Performance Monitoring System

**A modern, real-time Linux monitoring and security dashboard.**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Linux](https://img.shields.io/badge/Linux-Supported-orange?logo=linux)
![JavaScript](https://img.shields.io/badge/JavaScript-Frontend-yellow?logo=javascript)
![SQLite](https://img.shields.io/badge/SQLite-Database-blue?logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-success)

**Monitor • Analyze • Detect • Secure**

</div>

---

## 🚀 About the Project

**LinuxGuard** is an open-source Linux system monitoring and security analysis tool developed using Python, HTML, CSS, JavaScript, and SQLite.

It provides real-time system performance insights, resource anomaly detection, and read-only security auditing through an interactive web dashboard.

The goal of this project is to make Linux system monitoring simple, accessible, and visually engaging.

## ✨ Key Features

- 📊 **Real-Time Monitoring** — Track CPU, RAM, disk usage, and network activity.
- 🛡️ **Security Monitoring** — Inspect available SSH login failure logs and listening network ports.
- 🔍 **Process Explorer** — View running processes and their resource usage.
- 🧠 **Anomaly Detection** — Identify unusual resource utilization through statistical thresholds.
- 🚨 **Smart Alerts** — Record resource-related warning events.
- 📈 **Interactive Dashboard** — Responsive dark-themed interface with live charts.
- 💾 **SQLite Integration** — Store system monitoring history locally.
- ⚡ **Lightweight Architecture** — Built with Python and minimal external dependencies.

## 🛠️ Technology Stack

| Component | Technologies |
|---|---|
| Backend | Python |
| Frontend | HTML5, CSS3, JavaScript |
| Database | SQLite |
| System Monitoring | psutil |
| Web Server | Python HTTP Server |
| Operating System | Linux |
| Version Control | Git & GitHub |

## ⚙️ Installation & Setup

**Step 1: Clone the repository**

```bash
git clone https://github.com/YOUR_USERNAME/LinuxGuard.git
cd LinuxGuard
```

**Step 2: Create a virtual environment**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Step 3: Install dependencies**

```bash
pip install -r requirements.txt
```

**Step 4: Start the application**

```bash
python3 app.py
```

**Step 5: Open the dashboard**

Visit:

`http://127.0.0.1:8088`

## 📁 Project Structure

```text
LinuxGuard/
├── app.py
├── monitor.py
├── security.py
├── storage.py
├── index.html
├── static/
│   ├── styles.css
│   └── app.js
├── tests/
├── requirements.txt
├── LICENSE
└── README.md
```

## 🔐 Security & Privacy

LinuxGuard is designed as a local monitoring and educational security tool.

- Runs on localhost by default.
- Does not require external cloud services.
- Stores monitoring information locally.
- Performs read-only security checks.
- Does not modify firewall settings or terminate processes.

**Note:** LinuxGuard is not a replacement for professional antivirus or intrusion detection software.

## 🧪 Testing

Run automated tests with:

```bash
python3 -m unittest discover -s tests -v
```

## 🔮 Future Enhancements

- AI-assisted anomaly analysis
- Telegram and email notifications
- Custom monitoring thresholds
- Advanced security reports
- Historical monitoring analytics
- Remote monitoring with authentication

## 🎯 Project Objectives

The main objectives of LinuxGuard are to improve Linux system visibility, help users recognize resource abnormalities, and provide a foundation for defensive system administration.

## 📜 License

This project is distributed under the MIT License.

---

<div align="center">

### Made with ❤️ for Linux & Open-Source Enthusiasts

**LinuxGuard — Monitor Smarter. Stay Informed.**

⭐ Star this repository if you find it useful!

</div>
