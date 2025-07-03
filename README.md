# Grafana Runner 🚀

A digital signage solution that displays Grafana dashboard panels in full-screen kiosk mode, automatically rotating through configured panels at specified intervals.

## Features

- **True Kiosk Mode**: Full-screen browser display with no UI elements, cursor hiding, and keyboard shortcut blocking
- **Automatic Rotation**: Switches between panels based on configurable timing
- **JSON Configuration**: Easy setup with URL and timing configuration
- **Startup Integration**: Can run automatically on system startup
- **Browser Support**: Chrome (recommended) and Firefox support with optimized configurations
- **SSL Certificate Handling**: Built-in support for self-signed and internal certificates
- **CERN SSO Authentication**: Automatic login handling with CERN Single Sign-On and TOTP support
- **Logging**: Comprehensive logging for monitoring and debugging
- **Memory Management**: Automatic browser refresh to prevent memory leaks
- **Graceful Shutdown**: Handles interruption signals properly
- **Modular Architecture**: Clean, maintainable code structure with separate modules
- **Enhanced Security**: Configurable web security and SSL options for internal deployments

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
    "disable_web_security": false,
    "ignore_ssl_errors": true,
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
- `fullscreen`: Enable full-screen kiosk mode with OS-level fullscreen
- `disable_extensions`: Disable browser extensions
- `disable_web_security`: Allow cross-origin requests (use carefully)
- `ignore_ssl_errors`: Bypass SSL certificate validation (useful for internal/self-signed certificates)
- `incognito`: Use private/incognito mode
- `page_load_timeout`: Page load timeout in seconds

### Advanced Settings

- `log_level`: "DEBUG", "INFO", "WARNING", "ERROR"
- `refresh_browser_after_cycles`: Restart browser every N cycles (0 to disable)

### SSL Certificate Handling

For internal deployments with self-signed certificates, set:

```json
{
  "browser_settings": {
    "ignore_ssl_errors": true,
    "disable_web_security": true
  }
}
```

**Security Note**: Only use these settings in trusted internal environments.

## Enhanced Kiosk Features

The application provides a true kiosk experience with:

- **App Mode**: Chrome runs in app mode removing all browser UI
- **OS Fullscreen**: Native fullscreen mode for true digital signage
- **Grafana Native Kiosk**: Automatically enables Grafana's built-in kiosk mode
- **Cursor Hiding**: JavaScript-based cursor removal for clean display
- **Keyboard Blocking**: Disables F11, F12, Ctrl+Shift+I, and other shortcuts
- **Right-click Blocking**: Prevents context menus
- **Text Selection Blocking**: Prevents highlighting and selection
- **Scrollbar Hiding**: Removes all scrollbars for clean appearance

## CERN SSO Authentication

The application supports automatic authentication with CERN Single Sign-On (SSO) when accessing protected Grafana instances. When a login redirect is detected, the application automatically handles the authentication flow.

### Authentication Setup

1. **Create Environment File**

   Copy the example environment file:
   ```bash
   cp env.example .env.local
   ```

2. **Configure Credentials**

   Edit `.env.local` with your CERN credentials:
   ```env
   # CERN SSO Username
   CERN_USERNAME=your_cern_username

   # CERN SSO Password
   CERN_PASSWORD=your_cern_password

   # CERN TOTP Secret (from your authenticator app)
   CERN_TOTP_SECRET=your_totp_secret_key
   ```

3. **TOTP Secret Setup**

   To get your TOTP secret:
   - Go to CERN Account Settings
   - Enable two-factor authentication
   - When setting up your authenticator app, save the secret key (usually shown as a QR code alternative)
   - Use this secret key in the `CERN_TOTP_SECRET` variable

### Authentication Flow

The application automatically handles the complete authentication process:

1. **Detection**: Monitors for redirects to CERN login pages
2. **SSO Login**: Clicks the "Sign in with CERN SSO" button
3. **Credentials**: Fills in username and password automatically
4. **TOTP**: Generates and enters the current TOTP code
5. **Redirect**: Waits for successful authentication and return to Grafana

### Optional Authentication

Authentication is optional and gracefully handled:

- **With Credentials**: Full automatic authentication when login is required
- **Without Credentials**: Application continues normally but logs warnings when login pages are encountered
- **Partial Credentials**: Application warns about missing credentials and disables authentication

### Security Notes

- Store credentials securely in `.env.local` (not committed to version control)
- The `.env.local` file is automatically ignored by git
- Use environment variables for production deployments
- Consider using service accounts or API keys for unattended operation

### Troubleshooting Authentication

1. **Login page detected but authentication disabled**
   - Check that all required environment variables are set
   - Verify the `.env.local` file is in the correct location
   - Ensure credentials are correct

2. **TOTP code rejection**
   - Verify the TOTP secret is correct
   - Check system time synchronization
   - Ensure the secret is the base32 encoded key, not a 6-digit code

3. **Authentication timeout**
   - Check network connectivity to CERN authentication servers
   - Verify credentials are valid and account is not locked
   - Monitor logs for specific error messages

### Dependencies

The authentication feature requires additional Python packages:

```bash
# Install authentication dependencies
pip install pyotp python-dotenv
```

These are automatically installed when using the provided installation scripts.

## Grafana Native Kiosk Mode

The application automatically enables Grafana's built-in kiosk mode by appending the `&kiosk` parameter to panel URLs, providing the cleanest possible display experience.

### Automatic Kiosk Parameter

The application automatically:

1. **URL Modification**: Adds `&kiosk` parameter to panel URLs when enabled
2. **Smart Detection**: Checks if kiosk parameter already exists to avoid duplication
3. **Per-Panel Application**: Applies kiosk mode to each panel URL
4. **Instant Activation**: No additional loading time or button clicking required
5. **Configuration Controlled**: Easily enabled/disabled via `grafana_kiosk_mode` setting

### Configuration

Enable or disable Grafana kiosk mode in your `config.json`:

```json
{
  "grafana_kiosk_mode": true,
  "panels": [
    {
      "name": "Dashboard 1",
      "url": "http://grafana.example.com/d/dashboard1?orgId=1&refresh=5s",
      "duration": 15
    }
  ]
}
```

When enabled, URLs are automatically modified:
- `http://grafana.example.com/d/dashboard1?orgId=1` → `http://grafana.example.com/d/dashboard1?orgId=1&kiosk`
- URLs already containing `&kiosk` or `?kiosk` remain unchanged

### Benefits of Native Kiosk Mode

- **Cleaner Interface**: Removes Grafana's top navigation and sidebar
- **More Dashboard Space**: Maximizes area available for dashboard content
- **Professional Appearance**: Provides a clean, distraction-free display
- **Reliable Activation**: URL-based approach works across all Grafana versions
- **Zero Latency**: No additional loading time or element detection required

### Configuration Options

- **`grafana_kiosk_mode: true`** - Enables automatic kiosk parameter addition (default)
- **`grafana_kiosk_mode: false`** - Disables kiosk parameter addition
- **Not specified** - Defaults to `true` for backward compatibility

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

3. **SSL Certificate errors**
   - Set `ignore_ssl_errors: true` for self-signed certificates
   - Verify certificate validity for external sites
   - Check network firewall settings

4. **Memory issues**
   - Reduce `refresh_browser_after_cycles` value
   - Monitor system resources
   - Consider using Firefox instead of Chrome

5. **Fullscreen not working**
   - Ensure `fullscreen: true` in browser settings
   - Check OS permissions for application fullscreen
   - Try different browsers

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
- **Memory**: 2GB+ RAM recommended for stable operation
- **Display**: Any resolution, optimized for 1920x1080+

## Security Considerations

- The application runs a browser in kiosk mode with some security restrictions disabled
- `disable_web_security` and `ignore_ssl_errors` should only be used in trusted environments
- Use HTTPS for Grafana connections when possible
- Consider running in a sandboxed environment for production deployments
- The application blocks most user interactions, but physical access should still be restricted

## Architecture

### Modular Design

The application is built with a clean modular architecture:

- **`grafana_runner.py`**: Main orchestrator and entry point
- **`config.py`**: Configuration loading, validation, and default creation
- **`browser_setup.py`**: Browser initialization and kiosk mode configuration
- **`panel_navigator.py`**: Panel navigation and JavaScript-based enhancements
- **`auth_handler.py`**: CERN SSO authentication and TOTP handling

### Key Components

1. **ConfigManager**: Handles all configuration operations
2. **BrowserSetup**: Manages browser lifecycle and kiosk configuration
3. **PanelNavigator**: Handles panel loading and kiosk enhancements
4. **AuthHandler**: Manages CERN SSO authentication and TOTP codes
5. **GrafanaRunner**: Orchestrates the main execution loop

## Development

### Project Structure

```
GrafanaRunner/
├── grafana_runner.py    # Main application orchestrator
├── config.py            # Configuration management
├── browser_setup.py     # Browser setup and kiosk mode
├── panel_navigator.py   # Panel navigation and enhancements
├── auth_handler.py      # CERN SSO authentication and TOTP
├── config.json          # Configuration file
├── env.example          # Example environment configuration
├── requirements.txt     # Python dependencies
├── install.sh          # Installation script (macOS/Linux)
├── install.bat         # Installation script (Windows)
├── run.sh              # Run script (macOS/Linux)
├── run.bat             # Run script (Windows)
├── tests/              # Comprehensive test suite
│   ├── test_auth_handler.py
│   ├── test_browser_setup.py
│   ├── test_config.py
│   ├── test_config_validation.py
│   ├── test_fullscreen_mode.py
│   └── test_utils.py
└── README.md           # Documentation
```

### Testing

The project includes a comprehensive test suite:

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html

# Run specific test module
python -m pytest tests/test_browser_setup.py -v
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run the test suite to ensure nothing breaks
5. Update documentation if needed
6. Submit a pull request

### Code Quality

The project maintains high code quality with:
- Modular, single-responsibility design
- Comprehensive error handling
- Extensive logging
- Full test coverage
- Clear documentation
- Type hints where appropriate

## License

This project is open source. Feel free to modify and distribute according to your needs.
