# NetDoctor - System & Network Diagnostic Toolkit

Cross-platform (Windows/Linux/macOS) desktop application for sysadmins to run system and network diagnostics with a polished PySide6 GUI, background workers, exportable reports, and optional advanced features (SNMP, ARP, nmap integration).

## Purpose

Provide a single, polished tool that bundles common diagnostics (ping, traceroute, port-scan, DNS/whois, system overview) into an aesthetic, user-friendly desktop app suitable for production troubleshooting and for showcasing on GitHub.

## Features

### MVP Features
- **Ping & Ping Sweep**: ICMP ping with raw sockets or subprocess fallback
- **TCP Port Scanner**: Configurable concurrency and timeout
- **DNS Lookup and WHOIS**: Multiple record types (A, AAAA, CNAME, MX, NS, TXT)
- **System Overview**: CPU, memory, disk, network interface metrics with sparklines
- **Asynchronous Task Runner**: Background workers with progress tracking
- **Export Results**: CSV and JSON export

### Advanced Features (Post-MVP)
- ARP Local Network Discovery
- SNMP Poller
- Nmap Integration
- PDF Report Generator
- Network Diagram Generator
- Live Interface Monitoring

## Installation

### Development Setup

```bash
# Using Poetry (recommended)
poetry install

# Or using pip
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Running

```bash
# Activate virtual environment first (if using venv)
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Run the application
python -m netdoctor.main
```

## Development

### Running the Development App

After installing dependencies, run the application with:

```bash
python -m netdoctor.main
```

The application will launch with a minimal GUI showing:
- Left navigation rail with placeholder buttons (Dashboard, System, Network Tools, Reports, Settings)
- Main content area (currently showing placeholder views)

## Legal & Privacy Notice

**Important**: Network scanning may be illegal without proper authorization. This tool is intended for authorized network diagnostics only. Users are responsible for ensuring they have permission to scan target networks. Always obtain explicit authorization before performing network scans.

