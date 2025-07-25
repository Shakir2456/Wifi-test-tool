# WiFi Security Testing Tool - Android APK

**Developer:** SHAKIR HOSSAIN  
**Website:** https://shakir.com.bd

## Overview

This document explains how to convert the WiFi Security Testing Tool into an Android APK for use on rooted Android devices. The APK provides a mobile interface for WiFi security testing with the same functionality as the desktop version.

## Key Features

### Mobile Interface
- **Native Android UI** using Kivy framework
- **Touch-optimized controls** for mobile devices
- **Tabbed interface** with Control, Networks, and Results panels
- **Real-time status updates** with visual indicators
- **Portrait orientation** optimized for phones

### Core Functionality
- **System dependency installation** for rooted devices
- **One-click monitor mode** toggle for WiFi adapters
- **Fast network scanning** with WPS pin detection
- **Network attack interface** with PIN suggestions
- **Real-time operation monitoring** and progress tracking

### Technical Features
- **WPS PIN generation** for 40+ router brands and algorithms
- **Network address manipulation** and MAC processing
- **Wireless interface management** via system calls
- **Background task processing** with threading support
- **Error handling and logging** throughout the application

## Requirements

### Development Environment
- **Linux operating system** (Ubuntu/Debian recommended)
- **Python 3.8+** with pip package manager
- **Java 8 JDK** for Android compilation
- **Android SDK** and NDK (automatically downloaded)
- **Git** and essential build tools

### Target Android Device
- **Rooted Android device** (Android 5.0+ / API 21+)
- **WiFi adapter** capable of monitor mode
- **USB debugging enabled** for installation
- **Sufficient storage** (50MB+ for APK and dependencies)

## Installation Guide

### 1. Quick Setup (Automated)

```bash
# Clone the project
git clone https://github.com/Shakir2456/Wifi-test-tool
cd wifi-security-tool

# Run automated installer
./install_build_tools.sh

# Build APK
python3 build_apk.py
# Choose option 5: "Full setup and build"
```

### 2. Manual Setup

#### System Dependencies
```bash
# Update package lists
sudo apt-get update

# Install build essentials
sudo apt-get install -y build-essential git python3-dev python3-pip \
    openjdk-8-jdk unzip zlib1g-dev libncurses5-dev libncursesw5-dev \
    libtinfo5 cmake libffi-dev libssl-dev automake autoconf libtool \
    pkg-config libltdl-dev

# Set Java environment
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
echo "export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64" >> ~/.bashrc
```

#### Python Dependencies
```bash
# Install Python packages
pip3 install --user --upgrade pip
pip3 install --user buildozer cython kivy flask wcwidth requests pexpect
```

#### Android SDK (Optional)
```bash
# Create Android directory
mkdir -p ~/Android
cd ~/Android

# Download Android command line tools
wget https://dl.google.com/android/repository/commandlinetools-linux-8512546_latest.zip
unzip commandlinetools-linux-8512546_latest.zip
mkdir -p cmdline-tools/latest
mv cmdline-tools/* cmdline-tools/latest/

# Set environment
export ANDROID_HOME=~/Android
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools

# Install platform tools
yes | sdkmanager --licenses
sdkmanager "platform-tools"
```

### 3. Building the APK

#### Using Build Script
```bash
# Run the interactive build script
python3 build_apk.py

# Options available:
# 1. Install dependencies only
# 2. Build debug APK
# 3. Build release APK
# 4. Clean build
# 5. Full setup and build
```

#### Manual Buildozer Commands
```bash
# Initialize buildozer (first time only)
buildozer init

# Build debug APK (faster, for testing)
buildozer android debug

# Build release APK (optimized, for distribution)
buildozer android release

# Clean build artifacts
buildozer android clean
```

## Project Structure

```
wifi-security-tool/
├── main.py                 # APK entry point
├── mobile_app.py          # Kivy mobile interface
├── buildozer.spec         # APK build configuration
├── build_apk.py           # Automated build script
├── install_build_tools.sh # System setup script
├── app.py                 # Flask web server
├── wifi_manager.py        # WiFi operations
├── system_utils.py        # System utilities
├── oneshot.py             # WPS PIN algorithms
├── setup.py               # Desktop setup script
└── bin/                   # Generated APK files
    └── wifisecurity-1.0-debug.apk
```

## Configuration

### Buildozer Specification
The `buildozer.spec` file configures the APK build process:

```ini
[app]
title = WiFi Security Tool
package.name = wifisecurity
package.domain = com.shakir.wifisecurity
version = 1.0
requirements = python3,kivy,flask,wcwidth,requests,pexpect

[android]
permissions = INTERNET,ACCESS_NETWORK_STATE,ACCESS_WIFI_STATE,
              CHANGE_WIFI_STATE,ACCESS_COARSE_LOCATION,
              ACCESS_FINE_LOCATION,WRITE_EXTERNAL_STORAGE,
              READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.archs = arm64-v8a, armeabi-v7a
```

### Android Permissions
The APK requests essential permissions:
- **INTERNET** - Network communication
- **ACCESS_WIFI_STATE** - WiFi adapter access
- **CHANGE_WIFI_STATE** - Monitor mode control
- **ACCESS_LOCATION** - Required for WiFi scanning
- **EXTERNAL_STORAGE** - File operations

## Usage Instructions

### 1. APK Installation
```bash
# Enable USB debugging on Android device
# Connect device via USB
adb devices

# Install APK
adb install -r bin/wifisecurity-1.0-debug.apk

# Or use the build script option to auto-install
```

### 2. Using the Mobile App

#### First Launch
1. **Grant permissions** when prompted
2. **Check root access** status in top bar
3. **Install dependencies** using Control tab
4. **Enable monitor mode** for WiFi adapter

#### Network Scanning
1. **Navigate to Networks tab**
2. **Click "Scan Networks"** in Control panel
3. **View discovered networks** with WPS pins
4. **Select target** for security testing

#### Attack Operations
1. **Choose target network** from list
2. **Review WPS pins** in attack dialog
3. **Confirm attack** with warning acknowledgment
4. **Monitor progress** in Results tab

### 3. Device Requirements

#### Rooted Android Setup
```bash
# Verify root access
su -c "id"

# Install wireless tools (if not present)
# This varies by device and Android version
# Some tools may need manual compilation
```

#### WiFi Adapter Requirements
- **Monitor mode capability** (not all adapters support this)
- **Compatible chipset** (Ralink, Atheros, Intel recommended)
- **External USB adapter** may be needed for some devices

## Troubleshooting

### Build Issues

#### Java Version Problems
```bash
# Check Java version
java -version
javac -version

# Should show Java 8 (1.8.x)
# If not, install OpenJDK 8
sudo apt-get install openjdk-8-jdk
sudo update-alternatives --config java
```

#### Buildozer Errors
```bash
# Clear buildozer cache
rm -rf ~/.buildozer
rm -rf .buildozer

# Rebuild from scratch
buildozer android clean
buildozer android debug
```

#### NDK/SDK Issues
```bash
# Force SDK update
buildozer android update

# Manual SDK setup
export ANDROID_HOME=~/.buildozer/android/platform/android-sdk
export ANDROID_NDK_HOME=~/.buildozer/android/platform/android-ndk-r25b
```

### Runtime Issues

#### Permission Denied
- **Ensure device is rooted** with working su binary
- **Grant all requested permissions** in Android settings
- **Enable USB debugging** and allow computer access

#### WiFi Adapter Issues
- **Check monitor mode support**: `iw list | grep monitor`
- **Try external USB adapter** if internal WiFi unsupported
- **Verify wireless tools installation** on device

#### Network Scanning Problems
- **Check location services** are enabled
- **Ensure WiFi is enabled** but not connected
- **Verify aircrack-ng suite** is properly installed

## Development Notes

### Code Architecture
- **main.py** - APK entry point, imports mobile_app
- **mobile_app.py** - Kivy GUI with three tabs
- **StatusBar** - Real-time system status display
- **NetworkItem** - Individual network display widget
- **WiFiSecurityApp** - Main application class

### Build Process
1. **Buildozer initialization** - Download SDK/NDK
2. **Python-for-Android compilation** - Create ARM binaries
3. **APK packaging** - Bundle resources and dependencies
4. **Signing process** - Debug or release signing
5. **Installation** - Deploy to connected device

### Customization Options
- **App icon and splash** - Add icon.png and presplash.png
- **Permissions** - Modify android.permissions in buildozer.spec
- **Requirements** - Add Python packages to requirements line
- **Orientation** - Change orientation setting for landscape mode

## Security Considerations

### Ethical Usage
- **Educational purposes only** - For learning WiFi security
- **Authorized testing only** - Only test networks you own
- **Legal compliance** - Follow local laws and regulations
- **Responsible disclosure** - Report vulnerabilities properly

### Device Security
- **Root access risks** - Rooting voids warranty and creates security risks
- **Malware protection** - Only install from trusted sources
- **Network isolation** - Use dedicated testing environment
- **Data protection** - Clear sensitive data after testing

## Support and Contributions

### Getting Help
- **Check logs** for detailed error messages
- **Review permissions** if functionality is limited
- **Test on different devices** to isolate hardware issues
- **Update Android version** if compatibility problems occur

### Contributing
- **Bug reports** - Create detailed issue reports
- **Feature requests** - Suggest improvements
- **Code contributions** - Follow project coding standards
- **Documentation** - Help improve guides and tutorials

## License and Disclaimer

This tool is provided for educational and authorized security testing purposes only. Users are responsible for ensuring legal compliance and ethical usage. The developer assumes no responsibility for misuse or damages.

---

**Developer:** SHAKIR HOSSAIN  
**Website:** https://shakir.com.bd  
**Project Repository:** [https://github.com/Shakir2456/Wifi-test-tool/tree/main]
