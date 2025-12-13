# Manual Testing Instructions

## Prerequisites

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python -m netdoctor.main
   ```

## Testing Ping View

1. Navigate to "Dashboard" or "Network Tools" in the left navigation
2. Enter a host (e.g., "127.0.0.1" or "google.com")
3. Set ping count (default: 4)
4. Click "Start" button
5. Verify:
   - Results appear in the table with columns: seq, host, rtt_ms, ttl, status
   - Latency chart updates with RTT values
   - Start button is disabled during scan
   - Stop button is enabled and can cancel the operation
6. Click "Export CSV" to save results
7. Verify CSV file contains all ping results

## Testing System View

1. Navigate to "System" in the left navigation
2. Verify:
   - KPI cards display: CPU Usage, Memory Usage, Disk Usage, Uptime
   - Network interfaces table is populated with interface information
3. Click "Start Monitoring" button
4. Verify:
   - CPU and Memory charts update every second
   - KPI cards update with current values
   - Stop button is enabled
5. Click "Stop Monitoring" to halt updates

## Testing Port Scan View

1. Navigate to "Network Tools" (currently shows Ping view - Port Scan can be added to navigation later)
2. Or programmatically test by importing PortScanView
3. Enter a host (e.g., "127.0.0.1")
4. Enter port range (e.g., "80,443,8080" or "8000-8010")
5. Set thread count (default: 50)
6. Optionally check "Banner Grab" checkbox
7. Click "Start Scan" button
8. Verify:
   - Results appear in table with columns: port, state, service, banner
   - Open ports show "open" state
   - Closed ports show "closed" state
   - Service names are guessed from port numbers
   - Banner column shows "View" for ports with banners
9. Right-click on a row with a banner and verify banner dialog appears
10. Verify Start/Stop button states work correctly

## Expected Behavior

- All views should load without errors
- Worker operations should not freeze the UI
- Buttons should enable/disable appropriately
- Results should update in real-time
- Charts should display data correctly
- Export functionality should work

## Known Issues

- Port Scan view is not yet accessible via navigation (can be added to Network Tools as a tabbed view)
- Some runtime warnings about signal sources may appear during testing (does not affect functionality)

