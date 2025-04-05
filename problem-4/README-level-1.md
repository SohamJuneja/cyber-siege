# SSH Brute Force Defender

A security tool that monitors SSH authentication attempts and blocks suspicious IPs to protect your system from brute force attacks.

## Features

- Real-time monitoring of SSH authentication logs
- Automatic blocking of suspicious IPs based on configurable thresholds
- Multiple firewall support (UFW, iptables)
- IP whitelisting to prevent blocking trusted addresses
- Cross-platform log parsing (supports both auth.log and journalctl)

## Requirements

- Python 3.6 or higher
- Root/sudo privileges (required for firewall operations)
- Linux system with UFW or iptables

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/ssh-brute-defender.git
   cd ssh-brute-defender
   ```

2. Make the script executable:
   ```
   chmod +x ssh-brute-defender.py
   ```

## Usage

Basic usage:

```
sudo python3 ssh-brute-defender.py
```

With custom options:

```
sudo python3 ssh-brute-defender.py --threshold 3 --window 120 --whitelist 192.168.1.100 10.0.0.5
```

### Command Line Options

| Option | Description |
|--------|-------------|
| `--threshold N` | Number of failed attempts before blocking (default: 5) |
| `--window N` | Time window in seconds to count failures (default: 60) |
| `--whitelist IP1 IP2...` | IP addresses to never block |
| `--simulate` | Simulate blocking without actually implementing firewall rules |
| `--log-level {DEBUG,INFO,WARNING,ERROR}` | Set the logging verbosity level |

## How It Works

1. The tool monitors either `/var/log/auth.log` or `journalctl` for SSH authentication failures
2. When a failure is detected, it records the source IP and timestamp
3. If an IP exceeds the threshold of failures within the specified time window, it's automatically blocked
4. Blocking is implemented using the available firewall (UFW or iptables)

## Security Considerations

- Ensure your own IP is whitelisted to prevent accidental lockout
- Use this tool alongside other security measures like key-based authentication
- Keep SSH updated to patch known vulnerabilities

## Development

Contributions are welcome! Please feel free to submit a Pull Request.

### Project Structure

- `FirewallController`: Manages firewall rule implementation
- `SSHLogParser`: Parses system logs to detect authentication failures
- `SecurityMonitor`: Tracks failure patterns and determines when to block IPs

## License

This project is licensed under the MIT License - see the LICENSE file for details.