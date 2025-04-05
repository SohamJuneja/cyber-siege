# Universal SSH Brute Force Defender

A cross-platform solution for detecting and preventing SSH brute force attacks on Linux, macOS, and Windows systems.

## Features

- **Real-time monitoring** of SSH authentication attempts
- **Cross-platform support** for Linux, macOS, and Windows
- **Intelligent blocking system** with adaptive thresholds
- **Real-time alerts** via Slack and email
- **Geolocation tracking** of attack sources
- **Distributed attack detection** to identify coordinated attempts
- **Automatic cooldown periods** for blocked IPs
- **Whitelisting** to prevent blocking trusted IPs
- **Persistent blocking** that survives system restarts

## Requirements

### All Platforms
- Python 3.6+
- Required Python packages (see `requirements.txt`)
- GeoIP2 database for geolocation features

### Platform-Specific
- **Linux**: `python-iptables` package for iptables manipulation
- **macOS**: `pf` firewall (included in macOS)
- **Windows**: PowerShell and admin privileges for Windows Firewall management

## Installation

### Linux

```bash
# Install dependencies
sudo apt-get install python3-pip python3-iptables
pip3 install -r requirements.txt

# Download GeoIP database (optional but recommended)
mkdir -p /usr/share/GeoIP
wget -O /usr/share/GeoIP/GeoLite2-City.mmdb.gz https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-City&license_key=YOUR_LICENSE_KEY&suffix=tar.gz
gunzip /usr/share/GeoIP/GeoLite2-City.mmdb.gz

# Copy configuration
sudo cp config/ssh-defender.yaml /etc/ssh-defender.yaml

# Create log directory
sudo mkdir -p /var/log/ssh-defender
sudo mkdir -p /var/lib/ssh-defender
```

### macOS

```bash
# Install dependencies
pip3 install -r requirements.txt

# Enable and configure pf firewall if not already active
sudo pfctl -e

# Copy configuration
cp config/ssh-defender.yaml ~/Library/ssh-defender.conf

# Create necessary directories
sudo mkdir -p "/Library/Application Support/ssh-defender"
```

### Windows

```powershell
# Install dependencies (run as Administrator)
pip install -r requirements.txt

# Create necessary directories
mkdir -Force -Path "C:\ssh-defender"

# Copy configuration
Copy-Item config\ssh-defender.ini C:\ssh-defender\config.ini
```

## Configuration

The SSH Defender uses platform-specific configuration files:

- **Linux**: `/etc/ssh-defender.yaml`
- **macOS**: `~/Library/ssh-defender.conf`
- **Windows**: `C:\ssh-defender\config.ini`

### Sample Configuration for Linux/macOS (YAML)

```yaml
monitoring:
  failed_attempts_threshold: 5
  timeframe_seconds: 300
  distributed_threshold: 10
  cooldown_hours: 24

whitelist:
  - 192.168.1.100
  - 10.0.0.5

slack:
  webhook_url: "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
  enabled: true

email:
  enabled: true
  from: "alerts@yourdomain.com"
  to: "admin@yourdomain.com"
  smtp_host: "smtp.yourdomain.com"
  smtp_port: 587
  username: "alerts@yourdomain.com"
  password: "your-smtp-password"
  use_tls: true

geoip:
  database_path: "/usr/share/GeoIP/GeoLite2-City.mmdb"
```

### Sample Configuration for Windows (INI)

```ini
[Monitoring]
failed_attempts_threshold = 5
timeframe_seconds = 300
distributed_threshold = 10
cooldown_hours = 24

[Whitelist]
ips = 192.168.1.100, 10.0.0.5

[Slack]
webhook_url = https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
enabled = true

[Email]
enabled = true
from = alerts@yourdomain.com
to = admin@yourdomain.com
smtp_host = smtp.yourdomain.com
smtp_port = 587
username = alerts@yourdomain.com
password = your-smtp-password
use_tls = true

[GeoIP]
database_path = C:\ssh-defender\GeoLite2-City.mmdb
```

## Usage

### Running the Service

```bash
# Linux/macOS
sudo python3 ssh_defender.py

# Windows (run as Administrator)
python ssh_defender.py
```

### Running as a System Service

#### Linux (systemd)

Create a systemd service file `/etc/systemd/system/ssh-defender.service`:

```ini
[Unit]
Description=SSH Brute Force Defender
After=network.target

[Service]
ExecStart=/usr/bin/python3 /path/to/ssh_defender.py
Restart=always
User=root

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable ssh-defender
sudo systemctl start ssh-defender
```

#### macOS (launchd)

Create a launchd plist file `/Library/LaunchDaemons/com.ssh-defender.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.ssh-defender</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/path/to/ssh_defender.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

Load the service:

```bash
sudo launchctl load /Library/LaunchDaemons/com.ssh-defender.plist
```

#### Windows (Task Scheduler)

1. Open Task Scheduler
2. Create a new task
3. Set to run with highest privileges
4. Configure to run at startup
5. Add action: Start a program
   - Program: `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe`
   - Arguments: `-ExecutionPolicy Bypass -File "C:\path\to\ssh_defender.py"`

## Alert Configuration

### Slack Alerts

1. Create a Slack app at https://api.slack.com/apps
2. Add an Incoming Webhook
3. Copy the webhook URL to your configuration file

### Email Alerts

Configure the email section in your config file with your SMTP server details.

## Monitoring Logs

The SSH Defender logs all activity to:

- **Linux**: `/var/log/ssh_defender_blocks.log`
- **macOS**: Standard output (redirect as needed)
- **Windows**: Standard output (redirect as needed)

## Troubleshooting

### Common Issues

- **Firewall not blocking**: Check that the script is running with appropriate permissions
- **GeoIP database errors**: Ensure the GeoIP database file exists and is accessible
- **Email alerts not working**: Verify SMTP settings and credentials

### Getting Help

If you encounter issues:

1. Check the log file for error messages
2. Ensure all dependencies are installed
3. Verify configuration settings

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [GeoIP2 Python](https://github.com/maxmind/GeoIP2-python) for geolocation features
- [python-iptables](https://github.com/ldx/python-iptables) for Linux firewall management