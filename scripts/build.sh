#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
app_path="build/Claude Limit Bar.app"
mkdir -p "$app_path/Contents/MacOS"
xcrun swiftc -O -framework AppKit Sources/Limits.swift Sources/main.swift -o "$app_path/Contents/MacOS/ClaudeLimitBar"
cat > "$app_path/Contents/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>CFBundleIdentifier</key><string>org.community.claudelimitbar</string>
<key>CFBundleName</key><string>Claude Limit Bar</string>
<key>CFBundleExecutable</key><string>ClaudeLimitBar</string>
<key>CFBundlePackageType</key><string>APPL</string>
<key>CFBundleShortVersionString</key><string>1.0.0</string>
<key>LSMinimumSystemVersion</key><string>13.0</string>
<key>LSUIElement</key><true/>
</dict></plist>
PLIST
codesign --force --sign - "$app_path"
echo "Built: $app_path"
