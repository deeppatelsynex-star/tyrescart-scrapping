# TyresCart Scraping — Windows Server Production Deployment Guide

This document provides complete, step-by-step instructions to deploy, configure, and maintain the **TyresCart Scraping** web platform on a **Windows Server** (Windows Server 2019 / 2022 / Windows 10 / 11 Pro).

---

## 1. System Requirements & Prerequisites

### Minimum Hardware
- **CPU:** 4+ Cores (recommended for running multiple concurrent scrapers)
- **RAM:** 8 GB+ (16 GB recommended for high-volume scraping)
- **Disk:** 50 GB+ SSD storage

### Software to Install
1. **Python 3.11+ (64-bit)**
   - Download from [python.org](https://www.python.org/downloads/).
   - **Crucial:** Check the box **"Add Python to PATH"** during installation.
2. **Git for Windows**
   - Download from [git-scm.com](https://git-scm.com/download/win).
3. **MySQL Server 8.0+ or MariaDB 10.6+**
   - Download MySQL Community Server or use an existing database instance.
4. **NSSM (Non-Sucking Service Manager)**
   - Download from [nssm.cc](https://nssm.cc/download) to run the application as a permanent, auto-restarting Windows Background Service.
5. **Caddy or Nginx for Windows (Optional for Reverse Proxy & HTTPS)**
   - [Caddy Server](https://caddyserver.com/download) provides automatic HTTPS/SSL with 0 configuration.

---

## 2. Clone & Setup Repository

Open **PowerShell as Administrator** and run:

```powershell
# Navigate to your deployment directory (e.g. C:\inetpub or C:\Apps)
cd C:\Apps

# Clone the repository
git clone https://github.com/deeppatelsynex-star/tyrescart-scrapping.git
cd tyrescart-scrapping

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\Activate.ps1

# Upgrade pip and install all production dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# Install Waitress (Production WSGI Server for Windows)
pip install waitress
```

---

## 3. Database Configuration (`MySQL`)

### 3.1 Create the Database
Log into MySQL (`mysql -u root -p`) and execute:

```sql
CREATE DATABASE IF NOT EXISTS pitstop_scraper
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'tyrescart_user'@'localhost' IDENTIFIED BY 'YourStrongPassword123!';
GRANT ALL PRIVILEGES ON pitstop_scraper.* TO 'tyrescart_user'@'localhost';
FLUSH PRIVILEGES;
```

### 3.2 Configure `.env` File
Create a `.env` file in the root project folder (`C:\Apps\tyrescart-scrapping\.env`):

```ini
# Flask Security & Session
SECRET_KEY=generate_a_secure_random_64_character_string_here
SESSION_COOKIE_NAME=tyrescart_session
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
PERMANENT_SESSION_LIFETIME=86400

# Production Database Credentials
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=tyrescart_user
DB_PASSWORD=YourStrongPassword123!
DB_NAME=pitstop_scraper

# Email Delivery (Resend API)
RESEND_API_KEY=re_your_resend_api_key_here
MAIL_DEFAULT_SENDER=notifications@yourdomain.com
APP_URL=https://yourdomain.com

# Server Settings
PORT=5000
```

### 3.3 Initialize Database Schema
Run the initialization script inside the virtual environment:

```powershell
python app\init_db.py
```

*This creates the optimized 3-table schema (`userTbl`, `fileTbl`, `logTbl`) and seeds the default SuperAdmin account.*

---

## 4. Production WSGI Server on Windows (`Waitress`)

On Windows, Gunicorn is not supported natively. **Waitress** is the production WSGI server designed for Windows with multi-threaded socket handling.

### Test Running with Waitress Directly:

```powershell
# Inside virtual environment
waitress-serve --port=5000 --threads=16 --channel-timeout=0 wsgi:app
```

Open `http://localhost:5000` in your browser to verify that the app loads properly.

---

## 5. Setup as a Windows Background Service (Auto-Start & 24/7 Uptime)

Using **NSSM**, the server will automatically run on boot, restart instantly if closed, and log all events.

### Step 5.1: Install NSSM
1. Extract `nssm.exe` (from the `win64` folder) into `C:\Windows\System32\` (or `C:\Apps\nssm\`).

### Step 5.2: Register the Service
Open **PowerShell as Administrator** and run:

```powershell
# Create logs directory
mkdir C:\Apps\tyrescart-scrapping\logs -ErrorAction SilentlyContinue

# Install the service via NSSM
nssm install TyresCartScraper "C:\Apps\tyrescart-scrapping\venv\Scripts\waitress-serve.exe" "--port=5000 --threads=16 --channel-timeout=0 wsgi:app"

# Set App Directory
nssm set TyresCartScraper AppDirectory "C:\Apps\tyrescart-scrapping"

# Set Automatic Restart on crash
nssm set TyresCartScraper AppRestartDelay 3000
nssm set TyresCartScraper AppExit Default Restart

# Setup Log Redirection
nssm set TyresCartScraper AppStdout "C:\Apps\tyrescart-scrapping\logs\service_stdout.log"
nssm set TyresCartScraper AppStderr "C:\Apps\tyrescart-scrapping\logs\service_stderr.log"
nssm set TyresCartScraper AppRotateFiles 1
nssm set TyresCartScraper AppRotateOnline 1
nssm set TyresCartScraper AppRotateBytes 10485760

# Set Startup Type to Automatic (starts on Windows boot)
nssm set TyresCartScraper Start SERVICE_AUTO_START
```

### Step 5.3: Start the Service

```powershell
# Start the service
net start TyresCartScraper

# Check service status
nssm status TyresCartScraper
```

---

## 6. Setup HTTPS / SSL Reverse Proxy with Caddy (Recommended)

Caddy automatically obtains and renews free SSL certificates (Let's Encrypt / ZeroSSL) for your domain.

### Step 6.1: Create `Caddyfile`
Create `C:\Apps\Caddyfile`:

```caddy
yourdomain.com {
    reverse_proxy localhost:5000 {
        # Support live SSE webhook streaming
        flush_interval -1
    }
}
```

### Step 6.2: Install Caddy as a Windows Service

```powershell
nssm install CaddyServer "C:\Apps\caddy.exe" "run --config C:\Apps\Caddyfile"
nssm set CaddyServer Start SERVICE_AUTO_START
net start CaddyServer
```

---

## 7. Windows Firewall Configuration

Allow incoming HTTP (80) and HTTPS (443) traffic through Windows Firewall:

```powershell
New-NetFirewallRule -DisplayName "HTTP (80)" -Direction Inbound -LocalPort 80 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "HTTPS (443)" -Direction Inbound -LocalPort 443 -Protocol TCP -Action Allow
```

---

## 8. Common Maintenance & Management Commands

### Managing the Application Service

| Action | Command |
|---|---|
| **Check Status** | `nssm status TyresCartScraper` |
| **Restart Service** | `nssm restart TyresCartScraper` |
| **Stop Service** | `net stop TyresCartScraper` |
| **Start Service** | `net start TyresCartScraper` |
| **Edit Config via GUI** | `nssm edit TyresCartScraper` |
| **View Live Logs** | `Get-Content C:\Apps\tyrescart-scrapping\logs\service_stdout.log -Tail 50 -Wait` |

### Updating the Application (Git Pull)

```powershell
cd C:\Apps\tyrescart-scrapping
git pull origin main
.\venv\Scripts\pip install -r requirements.txt
nssm restart TyresCartScraper
```

### Automated Database Backup (Daily Scheduled Task)

Create a PowerShell backup script `C:\Apps\backup_db.ps1`:

```powershell
$Date = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupDir = "C:\Apps\db_backups"
if (!(Test-Path $BackupDir)) { New-Item -ItemType Directory -Path $BackupDir }
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe" -u tyrescart_user -pYourStrongPassword123! pitstop_scraper | Out-File -Encoding utf8 "$BackupDir\pitstop_backup_$Date.sql"
```

Register as a Daily Scheduled Task in Windows:
```powershell
$Action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-ExecutionPolicy Bypass -File C:\Apps\backup_db.ps1"
$Trigger = New-ScheduledTaskTrigger -Daily -At 3:00AM
Register-ScheduledTask -Action $Action -Trigger $Trigger -TaskName "TyresCart_DB_DailyBackup" -Description "Daily MySQL backup for TyresCart"
```
