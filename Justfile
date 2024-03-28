# Load .env for build variables
set dotenv-load

# Use powershell if on Windows
set windows-shell := ["powershell.exe", "-c"]

# This message
help:
    @just --list

run_cmd := if os_family() == "unix" {
    "PYTHONPATH=src:../psicalc-package/src python src/ps_app/main.py"
} else {
    "$env:PYTHONPATH=\".\\src;..\\psicalc-package\\src\"; python.exe .\\src\\ps_app\\main.py"
}
# Run locally (for development)
run:
    -{{run_cmd}}

# Clean dist and build
[unix]
clean:
    rm -rf dist build

# Clean dist and build
[windows]
clean:
    #!powershell.exe
    if (Test-Path dist) {
        rm -re -fo dist
    }
    if (Test-Path build) {
        rm -re -fo build
    }

# Build the app
build: clean
    pyinstaller "packaging/psicalc-{{os()}}.spec"

resource_cmd := if os_family() == "unix" {
    "pyrcc5 resources/resources.qrc -o src/ps_app/resources.py"
} else {
    "pyrcc5 resources\\resources.qrc -o src\\ps_app\\resources.py"
}
# Build resource file and output to the src directory
build-resources:
    {{resource_cmd}}

### macOS specific ###

# Generate the icon as an icns
[macos]
build-icon:
    cd resources && iconutil -c icns "$PCV_APP".iconset

# Run the compiled app build
[macos]
run-app:
    open dist/"$PCV_APP".app

# Build DMG
[macos]
build-dmg:
    rm -rf dist/image dist/"$PCV_APP".dmg
    mkdir dist/image
    cp -a dist/"$PCV_APP".app dist/image
    create-dmg \
        --volname "$PCV_APP" \
        --volicon resources/"$PCV_APP".icns \
        --window-pos 200 120 \
        --window-size 600 300 \
        --icon-size 100 \
        --icon "$PCV_APP".app 175 120 \
        --hide-extension "$PCV_APP".app \
        --app-drop-link 425 120 \
        dist/"$PCV_APP".dmg \
        dist/image

# Sign the DMG with dev account
[macos]
sign-dmg:
    codesign -s "$PCV_CERT" \
    --entitlements packaging/entitlements.plist \
    --verbose -o runtime \
    --preserve-metadata=identifier,entitlements,requirements,runtime \
    --timestamp ./dist/"$PCV_APP".dmg

# All build steps for release
[macos]
build-release: build build-dmg sign-dmg
    @echo "Don't forget to run 'just notarize'"

# Verify the signature on the app and DMG
[macos]
verify:
    #!/usr/bin/env bash
    if [ -e dist/"$PCV_APP".app ]; then
        codesign --verify --verbose dist/"$PCV_APP".app
    fi
    if [ -e dist/"$PCV_APP".dmg ]; then
        codesign --verify --verbose dist/"$PCV_APP".dmg
    fi

# Notarize the DMG via Apple (not tested)
[macos]
notarize:
    xcrun notarytool submit --apple-id "$PCV_EMAIL" --password "$PCV_APP_SPECIFIC_PASSWORD" --team-id "$PCV_TEAM_ID" --wait dist/"$PCV_APP".dmg
    xcrun stapler staple dist/"$PCV_APP".dmg

# Notary troubleshooting:
#
# Status
#xcrun notarytool info --apple-id "$USER_EMAIL" --password "$APP_SPECIFIC_PASSWORD" \
#--team-id AYX28QCD98 <SubmissionID>
#
# Log
#xcrun notarytool log --apple-id "$USER_EMAIL" --password "$APP_SPECIFIC_PASSWORD" \
#--team-id AYX28QCD98 <SubmissionID>
#
# History
#xcrun notarytool history --apple-id "$USER_EMAIL" --password "$APP_SPECIFIC_PASSWORD" \
#--team-id AYX28QCD98

### Linux specific ###
[linux]
build-appimage:
    #!/usr/bin/env bash
    cd dist
    rm -rf image
    mkdir -p image/usr/bin
    cp -a "PSICalc Viewer"/* image/usr/bin
    linuxdeploy-x86_64.AppImage --appdir image -i ../resources/psicalc-viewer.png -d ../resources/psicalc-viewer.desktop -o appimage
