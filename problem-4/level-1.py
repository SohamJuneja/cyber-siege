#!/usr/bin/env python3
"""
SSH Brute Force Defender
A security tool that monitors SSH authentication attempts and blocks suspicious IPs.
"""

import os
import re
import time
import logging
import argparse
import subprocess
import sys
import threading
import signal
import fcntl
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Optional, Set, Tuple, Union

# Setup logger
def setup_logger():
    """Configure and return a logger for the application."""
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    logging.basicConfig(level=logging.INFO, format=log_format, datefmt=date_format)
    return logging.getLogger('ssh-defender')

logger = setup_logger()

class FirewallController:
    """Manages firewall rules for blocking malicious IPs."""
    
    def __init__(self, simulation_mode=False):
        self.simulation_mode = simulation_mode
        self.firewall_system = self._detect_available_firewall()
        
    def _detect_available_firewall(self) -> str:
        """Detect which firewall system is available on the host."""
        # Try UFW first
        try:
            ufw_result = subprocess.run(
                ['ufw', 'status'], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True
            )
            if ufw_result.returncode == 0 and 'Status: active' in ufw_result.stdout:
                logger.info("Using UFW firewall")
                return 'ufw'
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
        
        # Try iptables
        try:
            iptables_result = subprocess.run(
                ['iptables', '--version'], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True
            )
            if iptables_result.returncode == 0:
                logger.info("Using iptables firewall")
                return 'iptables'
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
        
        logger.error("No supported firewall (ufw/iptables) found")
        return 'none'
    
    def block_ip(self, ip: str) -> bool:
        """Block an IP address using the available firewall."""
        if self.simulation_mode:
            logger.info(f"[SIMULATION] Would block IP: {ip}")
            return True
        
        if self.firewall_system == 'ufw':
            return self._block_with_ufw(ip)
        elif self.firewall_system == 'iptables':
            return self._block_with_iptables(ip)
        else:
            logger.error(f"Cannot block IP {ip} - no firewall available")
            return False
    
    def _block_with_ufw(self, ip: str) -> bool:
        """Block an IP using UFW."""
        try:
            result = subprocess.run(
                ['ufw', 'deny', 'from', ip, 'to', 'any'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            success = result.returncode == 0
            
            if success:
                logger.info(f"Successfully blocked IP {ip} using UFW")
            else:
                logger.error(f"Failed to block IP {ip} using UFW: {result.stderr}")
                
            return success
        except Exception as e:
            logger.error(f"Error blocking IP {ip} with UFW: {e}")
            return False
    
    def _block_with_iptables(self, ip: str) -> bool:
        """Block an IP using iptables."""
        try:
            # Check if rule already exists
            check_cmd = f"iptables -C INPUT -s {ip} -j DROP 2>/dev/null"
            rule_exists = os.system(check_cmd) == 0
            
            if rule_exists:
                logger.info(f"IP {ip} is already blocked in iptables")
                return True
            
            # Add block rule
            result = subprocess.run(
                ['iptables', '-A', 'INPUT', '-s', ip, '-j', 'DROP'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            success = result.returncode == 0
            
            if success:
                logger.info(f"Successfully blocked IP {ip} using iptables")
            else:
                logger.error(f"Failed to block IP {ip} using iptables: {result.stderr}")
                
            return success
        except Exception as e:
            logger.error(f"Error blocking IP {ip} with iptables: {e}")
            return False


class SSHLogParser:
    """Parses system logs to detect SSH login failures."""
    
    # SSH failure patterns for different log formats
    SSH_PATTERNS = {
        'auth_log': re.compile(
            r'(\w{3}\s+\d+\s+\d+:\d+:\d+).*sshd\[\d+\]:\s+(Failed password|Invalid user).*for.*from\s+(\d+\.\d+\.\d+\.\d+)'
        ),
        'journald': re.compile(
            r'(\d+-\d+-\d+\s+\d+:\d+:\d+).*sshd\[\d+\]:\s+(Failed password|Invalid user).*for.*from\s+(\d+\.\d+\.\d+\.\d+)'
        )
    }
    
    # Time formats for different log sources
    TIME_FORMATS = {
        'auth_log': '%Y %b %d %H:%M:%S',   # 2023 Mar 15 21:34:56
        'journald': '%Y-%m-%d %H:%M:%S'    # 2023-03-15 21:34:56
    }
    
    def __init__(self, security_monitor):
        """Initialize the SSH log parser.
        
        Args:
            security_monitor: The security monitor to report failures to
        """
        self.security_monitor = security_monitor
        self.is_active = False
        self.monitor_thread = None
        self.auth_log_path = '/var/log/auth.log'
    
    def determine_log_source(self) -> str:
        """Determine which log source to use."""
        # Try auth.log first
        if os.path.exists(self.auth_log_path) and os.access(self.auth_log_path, os.R_OK):
            return 'auth_log'
        
        # Try journalctl as fallback
        try:
            subprocess.run(
                ['journalctl', '--version'], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                check=True
            )
            return 'journald'
        except (subprocess.SubprocessError, FileNotFoundError):
            logger.error("Could not access auth.log or journalctl")
            sys.exit(1)
    
    def start_monitoring(self):
        """Start monitoring SSH logs."""
        if self.is_active:
            logger.warning("Log parser is already running")
            return
        
        self.is_active = True
        log_source = self.determine_log_source()
        
        logger.info(f"Starting SSH log monitoring using {log_source}")
        
        if log_source == 'auth_log':
            self.monitor_thread = threading.Thread(target=self._monitor_auth_log)
        else:  # journald
            self.monitor_thread = threading.Thread(target=self._monitor_journald)
            
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def _monitor_auth_log(self):
        """Monitor the auth.log file for SSH failures."""
        try:
            with open(self.auth_log_path, 'r') as log_file:
                # Start reading from end of file
                log_file.seek(0, 2)
                
                while self.is_active:
                    line = log_file.readline()
                    if line:
                        self._process_log_entry(line, 'auth_log')
                    else:
                        time.sleep(0.1)
        except Exception as e:
            logger.error(f"Error monitoring auth.log: {e}")
            self.is_active = False
    
    def _monitor_journald(self):
        """Monitor journalctl for SSH failures."""
        try:
            process = subprocess.Popen(
                ['journalctl', '-f', '-u', 'ssh', '-u', 'sshd', '--no-pager'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            while self.is_active:
                line = process.stdout.readline()
                if line:
                    self._process_log_entry(line, 'journald')
                else:
                    time.sleep(0.1)
                    
            process.terminate()
        except Exception as e:
            logger.error(f"Error monitoring journalctl: {e}")
            self.is_active = False
    
    def _process_log_entry(self, log_entry: str, source_type: str):
        """Process a log entry to extract failure information."""
        pattern = self.SSH_PATTERNS[source_type]
        match = pattern.search(log_entry)
        
        if not match:
            return
            
        timestamp_str, failure_type, source_ip = match.groups()
        
        try:
            # Parse the timestamp
            if source_type == 'auth_log':
                # Add current year (not in auth.log)
                current_year = datetime.now().year
                timestamp = datetime.strptime(f"{current_year} {timestamp_str}", self.TIME_FORMATS[source_type])
                
                # Handle year rollover (December logs read in January)
                if timestamp > datetime.now() + timedelta(days=1):
                    timestamp = timestamp.replace(year=current_year - 1)
            else:
                timestamp = datetime.strptime(timestamp_str, self.TIME_FORMATS[source_type])
            
            # Report the failure to the security monitor
            logger.debug(f"Detected login failure from {source_ip}")
            self.security_monitor.record_failure(source_ip, timestamp)
            
        except ValueError as e:
            logger.warning(f"Could not parse timestamp '{timestamp_str}': {e}")
    
    def stop_monitoring(self):
        """Stop monitoring SSH logs."""
        self.is_active = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            try:
                self.monitor_thread.join(timeout=2)
            except Exception:
                pass
        logger.info("SSH log monitoring stopped")


class SecurityMonitor:
    """Detects potential threats based on login failure patterns."""
    
    def __init__(self, failure_threshold: int, time_window: int, safe_ips: List[str]):
        """Initialize the security monitor.
        
        Args:
            failure_threshold: Number of failures before blocking
            time_window: Time window in seconds for counting failures
            safe_ips: List of IPs to never block
        """
        self.failure_threshold = failure_threshold
        self.time_window = time_window
        self.safe_ips = set(safe_ips)
        self.firewall = None  # Set later
        self.failures_by_ip = defaultdict(list)
        self.blocked_ips = set()
    
    def set_firewall(self, firewall: FirewallController):
        """Set the firewall controller to use."""
        self.firewall = firewall
    
    def record_failure(self, ip: str, timestamp: datetime):
        """Record a login failure for an IP address."""
        # Skip whitelisted or already blocked IPs
        if ip in self.safe_ips:
            logger.debug(f"Ignoring whitelisted IP: {ip}")
            return
            
        if ip in self.blocked_ips:
            logger.debug(f"Ignoring already blocked IP: {ip}")
            return
        
        # Add the new failure
        self.failures_by_ip[ip].append(timestamp)
        
        # Clean old failures outside the time window
        cutoff = datetime.now() - timedelta(seconds=self.time_window)
        self.failures_by_ip[ip] = [ts for ts in self.failures_by_ip[ip] if ts > cutoff]
        
        # Check if threshold is exceeded
        failure_count = len(self.failures_by_ip[ip])
        
        if failure_count >= self.failure_threshold:
            logger.warning(
                f"IP {ip} exceeded failure threshold with {failure_count} "
                f"failures in {self.time_window} seconds"
            )
            
            if self.firewall:
                if self.firewall.block_ip(ip):
                    self.blocked_ips.add(ip)
                    # Clear the failures for this IP
                    self.failures_by_ip[ip] = []


def verify_root_privileges() -> bool:
    """Check if the script is running with root privileges."""
    if os.geteuid() != 0:
        logger.error("This script requires root privileges. Please run with sudo.")
        return False
    return True


def parse_cli_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='SSH Brute Force Defender - Monitor and block suspicious login attempts'
    )
    
    parser.add_argument(
        '--threshold', 
        type=int, 
        default=5,
        help='Number of failed attempts before blocking (default: 5)'
    )
    
    parser.add_argument(
        '--window', 
        type=int, 
        default=60,
        help='Time window in seconds to count failures (default: 60)'
    )
    
    parser.add_argument(
        '--whitelist', 
        type=str, 
        nargs='+', 
        default=[],
        help='IP addresses to never block (e.g., --whitelist 192.168.1.100 10.0.0.5)'
    )
    
    parser.add_argument(
        '--simulate', 
        action='store_true',
        help='Simulate actions without actually blocking IPs'
    )
    
    parser.add_argument(
        '--log-level', 
        type=str, 
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Set logging verbosity level'
    )
    
    return parser.parse_args()


def handle_termination(signum, frame):
    """Handle termination signals for clean shutdown."""
    logger.info("Received termination signal. Shutting down gracefully...")
    global ssh_log_parser
    ssh_log_parser.stop_monitoring()
    sys.exit(0)


if __name__ == "__main__":
    # Parse command-line arguments
    args = parse_cli_arguments()
    
    # Set log level
    logger.setLevel(getattr(logging, args.log_level))
    
    # Check root privileges
    if not verify_root_privileges():
        sys.exit(1)
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, handle_termination)
    signal.signal(signal.SIGTERM, handle_termination)
    
    # Display startup information
    logger.info(f"Starting SSH Brute Force Defender with:")
    logger.info(f"- Failure threshold: {args.threshold}")
    logger.info(f"- Time window: {args.window} seconds")
    
    if args.whitelist:
        logger.info(f"- Whitelisted IPs: {', '.join(args.whitelist)}")
    
    if args.simulate:
        logger.info("- SIMULATION MODE: Actions will be logged but not executed")
    
    # Initialize components
    security_monitor = SecurityMonitor(
        failure_threshold=args.threshold,
        time_window=args.window,
        safe_ips=args.whitelist
    )
    
    firewall_controller = FirewallController(simulation_mode=args.simulate)
    security_monitor.set_firewall(firewall_controller)
    
    ssh_log_parser = SSHLogParser(security_monitor)
    
    # Start monitoring
    ssh_log_parser.start_monitoring()
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        ssh_log_parser.stop_monitoring()
        logger.info("SSH Brute Force Defender stopped")