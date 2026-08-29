# TyresCart Scraping — Plesk Panel (Windows Server) Production Deployment Guide

This guide provides step-by-step instructions to deploy and host the **TyresCart Scraping** platform on a **Windows Server running Plesk Panel** (Plesk Obsidian for Windows with IIS).

---

## 1. Prerequisites on Plesk Windows Server

1. **Plesk Panel (Windows Edition)** with Administrator access.
2. **Python 3.10+ / 3.11+ (x64)** installed on the server (installed via Plesk Updates / Extensions or standard Windows Python installer with PATH enabled).
3. **MySQL / MariaDB** database server enabled in Plesk (**Tools & Settings $\rightarrow$ Database Servers**).
4. **IIS URL Rewrite & HttpPlatformHandler modules** installed on IIS (standard in modern Plesk Windows).

---

## 2. Step-by-Step Plesk Setup

### Step 2.1: Create the Domain or Subdomain in Plesk
1. Log in to Plesk Panel.
2. Go to **Websites & Domains** $\rightarrow$ Click **Add Domain** or **Add Subdomain** (e.g. `scraper.yourdomain.com`).
3. Set **Document root** to `httpdocs`.

---

### Step 2.2: Create the MySQL Database in Plesk
1. In your domain dashboard in Plesk, click **Databases** $\rightarrow$ **Add Database**.
2. Set:
   - **Database name:** `pitstop_scraper`
   - **Database user name:** `tyrescart_user`
   - **Password:** *Enter a strong password*
   - **User has access to all databases within the selected subscription:** Checked
3. Click **OK**.

---

### Step 2.3: Upload Project Files to Plesk
You can upload the project via **Git in Plesk** (Recommended) or **File Manager**:

#### Option A: Using Plesk Git (Recommended)
1. In your domain dashboard, click **Git**.
2. Enter the remote repository URL:
   `https://github.com/deeppatelsynex-star/tyrescart-scrapping.git`
3. Branch: `main`
4. Deployment path: `/httpdocs`
5. Click **OK** $\rightarrow$ **Pull Updates**.

#### Option B: Using File Manager / FTP
1. Upload all project files into `C:\Inetpub\vhosts\yourdomain.com\httpdocs\`.

---

### Step 2.4: Create Virtual Environment & Install Dependencies

Connect to your Windows Server via **RDP (Remote Desktop)** or **Plesk SSH/PowerShell terminal** as Administrator:

```powershell
# Navigate to your domain's httpdocs directory
cd C:\Inetpub\vhosts\yourdomain.com\httpdocs

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Upgrade pip and install all required production packages
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install waitress
```

---

### Step 2.5: Configure Environment Variables (`.env`)

Create or edit the `.env` file in `C:\Inetpub\vhosts\yourdomain.com\httpdocs\.env`:

```ini
# Flask Security Keys
SECRET_KEY=enter_a_strong_64_character_random_secret_key_here
SESSION_COOKIE_NAME=tyrescart_session
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
PERMANENT_SESSION_LIFETIME=86400

# Database Settings (Plesk MySQL)
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=tyrescart_user
DB_PASSWORD=YourPleskDatabasePasswordHere
DB_NAME=pitstop_scraper

# App URL
APP_URL=https://scraper.yourdomain.com

# Server Port (Used by local Waitress WSGI)
PORT=5000
```

### Step 2.6: Initialize the Database Tables
In PowerShell (inside `httpdocs` with virtualenv activated):

```powershell
python app\init_db.py
```
*This creates `userTbl`, `fileTbl`, and `logTbl` and configures the default SuperAdmin user.*

---

## 3. IIS & Plesk Web Integration (`web.config`)

To make IIS automatically route web traffic to Python using `HttpPlatformHandler`, place this `web.config` file inside `C:\Inetpub\vhosts\yourdomain.com\httpdocs\web.config`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="PythonHandler" path="*" verb="*" modules="httpPlatformHandler" resourceType="Unspecified" requireAccess="Script" />
    </handlers>
    <httpPlatform processPath="C:\Inetpub\vhosts\yourdomain.com\httpdocs\venv\Scripts\waitress-serve.exe"
                  arguments="--port=%HTTP_PLATFORM_PORT% --threads=16 --channel-timeout=0 wsgi:app"
                  requestTimeout="00:30:00"
                  startupTimeLimit="120"
                  startupRetryCount="3"
                  stdoutLogEnabled="true"
                  stdoutLogFile="C:\Inetpub\vhosts\yourdomain.com\httpdocs\logs\stdout.log">
      <environmentVariables>
        <environmentVariable name="PYTHONPATH" value="C:\Inetpub\vhosts\yourdomain.com\httpdocs\app;C:\Inetpub\vhosts\yourdomain.com\httpdocs" />
      </environmentVariables>
    </httpPlatform>
    <security>
      <requestFiltering>
        <requestLimits maxAllowedContentLength="52428800" />
      </requestFiltering>
    </security>
  </system.webServer>
</configuration>
```

> **Note:** Create a `logs` folder inside `httpdocs` to enable stdout/stderr logging:
> `mkdir C:\Inetpub\vhosts\yourdomain.com\httpdocs\logs`

---

## 4. Alternative Method: Running as a Windows Service (NSSM) + Plesk Reverse Proxy

If your Plesk IIS does not have `HttpPlatformHandler` installed, you can run the app as a permanent Windows background service and use Plesk's URL Rewrite to proxy requests to `http://localhost:5000`.

### Step 4.1: Register Windows Background Service with NSSM
1. Download `nssm.exe` and open PowerShell as Administrator:
```powershell
nssm install TyresCartPlesk "C:\Inetpub\vhosts\yourdomain.com\httpdocs\venv\Scripts\waitress-serve.exe" "--port=5000 --threads=16 --channel-timeout=0 wsgi:app"
nssm set TyresCartPlesk AppDirectory "C:\Inetpub\vhosts\yourdomain.com\httpdocs"
nssm set TyresCartPlesk AppRestartDelay 3000
nssm set TyresCartPlesk AppExit Default Restart
nssm set TyresCartPlesk AppStdout "C:\Inetpub\vhosts\yourdomain.com\httpdocs\logs\service_stdout.log"
nssm set TyresCartPlesk AppStderr "C:\Inetpub\vhosts\yourdomain.com\httpdocs\logs\service_stderr.log"
nssm set TyresCartPlesk Start SERVICE_AUTO_START

# Start the service
net start TyresCartPlesk
```

### Step 4.2: Add Reverse Proxy Rule in `web.config`
In `httpdocs\web.config`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <system.webServer>
    <rewrite>
      <rules>
        <rule name="ReverseProxyToWaitress" stopProcessing="true">
          <match url=".*" />
          <action type="Rewrite" url="http://127.0.0.1:5000/{R:0}" />
        </rule>
      </rules>
    </rewrite>
    <httpProtocol>
      <customHeaders>
        <add name="X-Forwarded-Proto" value="https" />
      </customHeaders>
    </httpProtocol>
  </system.webServer>
</configuration>
```

---

## 5. Enable Free SSL / HTTPS in Plesk

1. In Plesk Panel, go to **Websites & Domains** $\rightarrow$ Select your domain.
2. Click **SSL/TLS Certificates**.
3. Under **Install a free basic certificate provided by Let's Encrypt**, click **Install**.
4. Check **Secure the domain name** and **Secure the 'www' subdomain**.
5. Click **Get it free**.
6. Turn ON **Redirect from HTTP to HTTPS**.

---

## 6. Plesk Scheduled Tasks (Automated Cron / Maintenance)

In Plesk, click **Scheduled Tasks** $\rightarrow$ **Add Task**:

### Task 1: Daily Database Backup (3:00 AM)
- **Task type:** Run a command
- **Command:**
  ```powershell
  & "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe" -u tyrescart_user -pYourPassword pitstop_scraper > "C:\Inetpub\vhosts\yourdomain.com\backups\db_backup.sql"
  ```
- **Run:** Daily at 03:00

---

## 7. Useful Plesk Management Commands

| Action | Command / Location in Plesk |
|---|---|
| **Pull Git Updates** | In Plesk: **Websites & Domains $\rightarrow$ Git $\rightarrow$ Pull Updates** |
| **Restart Service** | `nssm restart TyresCartPlesk` or `iisreset` |
| **View Live Logs** | `Get-Content C:\Inetpub\vhosts\yourdomain.com\httpdocs\logs\service_stdout.log -Tail 50 -Wait` |
| **Check Port 5000** | `netstat -ano \| findstr :5000` |
