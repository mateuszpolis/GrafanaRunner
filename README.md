# Grafana Runner 🚀

A digital signage solution that displays Grafana dashboard panels in full-screen kiosk mode, automatically rotating through configured panels at specified intervals.

## Features

- **Kiosk Mode**: Full-screen browser display with no UI elements
- **Automatic Rotation**: Switches between panels based on configurable timing
- **JSON Configuration**: Easy setup with URL and timing configuration
- **Startup Integration**: Can run automatically on system startup
- **Browser Support**: Chrome (recommended) and Firefox support
- **Logging**: Comprehensive logging for monitoring and debugging
- **Memory Management**: Automatic browser refresh to prevent memory leaks
- **Graceful Shutdown**: Handles interruption signals properly

## Quick Start

### 1. Installation

#### macOS/Linux
```bash
# Clone or download the project
# Navigate to the project directory

# Install dependencies
chmod +x install.sh
./install.sh
```

#### Windows
```cmd
# Clone or download the project
# Navigate to the project directory

# Install dependencies
install.bat
```

### 2. Configuration

Edit `config.json` with your Grafana panel URLs:

```json
{
  "panels": [
    {
      "name": "Dashboard 1",
      "url": "http://your-grafana:3000/d/dashboard-id?orgId=1&refresh=5s&kiosk",
      "duration": 15
    },
    {
      "name": "Dashboard 2", 
      "url": "http://your-grafana:3000/d/another-dashboard?orgId=1&refresh=5s&kiosk",
      "duration": 20
    }
  ],
  "browser_settings": {
    "browser": "chrome",
    "fullscreen": true,
    "disable_extensions": true,
    "incognito": true,
    "page_load_timeout": 30
  },
  "log_level": "INFO",
  "refresh_browser_after_cycles": 10
}
```

### 3. Running

#### macOS/Linux
```bash
# Test run
python3 grafana_runner.py

# Or use the run script
./run.sh

# Run with custom config
python3 grafana_runner.py my-config.json
```

#### Windows
```cmd
# Test run
python grafana_runner.py

# Or use the run script
run.bat

# Run with custom config
python grafana_runner.py my-config.json
```

### 4. Startup Integration

#### macOS
```bash
# Enable automatic startup
launchctl load ~/Library/LaunchAgents/com.grafanarunner.plist

# Disable automatic startup
launchctl unload ~/Library/LaunchAgents/com.grafanarunner.plist

# Check status
launchctl list | grep grafanarunner
```

#### Windows
```cmd
# Startup task is created automatically during installation

# Check task status
schtasks /query /tn "GrafanaRunner"

# Disable startup
schtasks /change /tn "GrafanaRunner" /disable

# Enable startup
schtasks /change /tn "GrafanaRunner" /enable

# Delete startup task
schtasks /delete /tn "GrafanaRunner" /f
```

## Configuration Reference

### Panel Configuration

Each panel in the `panels` array supports:

- `name` (string): Display name for logging
- `url` (string): Full Grafana panel URL
- `duration` (number): Display time in seconds

### Browser Settings

- `browser`: "chrome" or "firefox" (chrome recommended)
- `fullscreen`: Enable full-screen kiosk mode
- `disable_extensions`: Disable browser extensions
- `disable_web_security`: Allow cross-origin requests (use carefully)
- `incognito`: Use private/incognito mode
- `page_load_timeout`: Page load timeout in seconds

### Advanced Settings

- `log_level`: "DEBUG", "INFO", "WARNING", "ERROR"
- `refresh_browser_after_cycles`: Restart browser every N cycles (0 to disable)

## Grafana URL Tips

For best kiosk display, add these parameters to your Grafana URLs:

- `&kiosk`: Enables kiosk mode (removes Grafana UI)
- `&refresh=5s`: Auto-refresh every 5 seconds
- `&orgId=1`: Specify organization ID
- `&from=now-1h&to=now`: Set time range

Example URL:
```
http://grafana.example.com:3000/d/dashboard123?orgId=1&refresh=5s&kiosk&from=now-1h&to=now
```

## Troubleshooting

### Common Issues

1. **Browser doesn't start**
   - Ensure Chrome or Firefox is installed
   - Check that webdriver-manager can download ChromeDriver
   - Try running with `log_level: "DEBUG"`

2. **Panels don't load**
   - Verify Grafana URLs are accessible
   - Check network connectivity
   - Ensure Grafana authentication is handled (use API keys or public dashboards)

3. **Memory issues**
   - Reduce `refresh_browser_after_cycles` value
   - Monitor system resources
   - Consider using Firefox instead of Chrome

### Logs

Check logs for debugging:
- `grafana_runner.log` - Application logs
- `grafana_runner_error.log` - Error logs (when run as startup service)

### Manual Testing

#### macOS/Linux
```bash
# Test with debug logging
python3 -c "
import json
config = json.load(open('config.json'))
config['log_level'] = 'DEBUG'
json.dump(config, open('debug-config.json', 'w'), indent=2)
"
python3 grafana_runner.py debug-config.json
```

#### Windows
```cmd
# Test with debug logging
python -c "import json; config = json.load(open('config.json')); config['log_level'] = 'DEBUG'; json.dump(config, open('debug-config.json', 'w'), indent=2)"
python grafana_runner.py debug-config.json
```

## System Requirements

- **Operating System**: macOS (tested), Linux, Windows
- **Python**: 3.7+
- **Browser**: Chrome (recommended) or Firefox
- **Network**: Access to Grafana instance

## Security Considerations

- The application runs a browser in kiosk mode with some security restrictions disabled
- Consider network security when allowing cross-origin requests
- Use HTTPS for Grafana connections when possible
- Consider running in a sandboxed environment for production deployments

## Development

### Project Structure

```
GrafanaRunner/
├── grafana_runner.py    # Main application
├── config.json          # Configuration file
├── requirements.txt     # Python dependencies
├── install.sh          # Installation script (macOS/Linux)
├── install.bat         # Installation script (Windows)
├── run.sh              # Run script (macOS/Linux)
├── run.bat             # Run script (Windows)
└── README.md           # Documentation
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source. Feel free to modify and distribute according to your needs. 