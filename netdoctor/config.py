"""
Global defaults and settings configuration.
"""

# Default timeout values (seconds)
DEFAULT_PING_TIMEOUT = 1.0
DEFAULT_PORT_SCAN_TIMEOUT = 3.0
DEFAULT_DNS_TIMEOUT = 5.0

# Default concurrency settings
DEFAULT_PORT_SCAN_THREADS = 50
DEFAULT_PING_SWEEP_THREADS = 10

# UI defaults
DEFAULT_THEME = "dark"
DEFAULT_REFRESH_RATE = 1000  # milliseconds

# Storage settings
STORAGE_TYPE = "sqlite"  # "sqlite" or "json"
DB_FILENAME = "netdoctor_history.db"
JSON_HISTORY_FILENAME = "history.json"

