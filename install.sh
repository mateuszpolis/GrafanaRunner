#!/bin/bash

# Grafana Runner Installation Script for macOS

set -e

echo "🚀 Installing Grafana Runner..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    echo "You can install it from: https://www.python.org/downloads/"
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip first."
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Check if Chrome is installed (preferred browser)
if ! command -v /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome &> /dev/null; then
    echo "⚠️  Google Chrome not found. Please install Chrome for best compatibility:"
    echo "   https://www.google.com/chrome/"
    echo ""
    echo "Alternative: You can use Firefox by changing 'browser' to 'firefox' in config.json"
fi

# Install ChromeDriver automatically using webdriver-manager
echo "🔧 ChromeDriver will be automatically managed by webdriver-manager"

# Make the main script executable
chmod +x grafana_runner.py

# Create startup script for macOS
echo "🔧 Creating startup configuration..."

# Create LaunchAgent plist file
PLIST_FILE="$HOME/Library/LaunchAgents/com.grafanarunner.plist"
CURRENT_DIR="$(pwd)"

cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.grafanarunner</string>
    <key>ProgramArguments</key>
    <array>
        <string>python3</string>
        <string>$CURRENT_DIR/grafana_runner.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$CURRENT_DIR</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$CURRENT_DIR/grafana_runner.log</string>
    <key>StandardErrorPath</key>
    <string>$CURRENT_DIR/grafana_runner_error.log</string>
</dict>
</plist>
EOF

echo "✅ Installation complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Edit config.json with your Grafana panel URLs"
echo "2. Test the runner: python3 grafana_runner.py"
echo "3. Enable startup: launchctl load $PLIST_FILE"
echo "4. Disable startup: launchctl unload $PLIST_FILE"
echo ""
echo "📖 For more information, see README.md" 