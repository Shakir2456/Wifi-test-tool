#!/bin/bash
# WiFi Security Tool - Build Tools Installer
# Developer: SHAKIR HOSSAIN
# Website: https://shakir.com.bd

set -e

echo "============================================================"
echo "WiFi Security Tool - Build Tools Installer"
echo "Developer: SHAKIR HOSSAIN"
echo "Website: https://shakir.com.bd"
echo "============================================================"

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "❌ Error: This script requires Linux"
    exit 1
fi

# Check if running as root for system packages
if [[ $EUID -eq 0 ]]; then
    echo "❌ Please don't run this script as root"
    echo "It will ask for sudo permissions when needed"
    exit 1
fi

echo "📦 Installing system dependencies for Android APK building..."

# Update package lists
echo "Updating package lists..."
sudo apt-get update

# Install essential build tools
echo "Installing build essentials..."
sudo apt-get install -y \
    build-essential \
    git \
    python3-dev \
    python3-pip \
    python3-venv \
    curl \
    wget \
    unzip \
    zip \
    openjdk-8-jdk \
    openjdk-8-jre \
    zlib1g-dev \
    libncurses5-dev \
    libncursesw5-dev \
    libtinfo5 \
    cmake \
    libffi-dev \
    libssl-dev \
    automake \
    autoconf \
    libtool \
    pkg-config \
    libltdl-dev \
    ccache \
    ninja-build

# Set JAVA_HOME
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
echo "export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64" >> ~/.bashrc

echo "✅ System dependencies installed"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install --user --upgrade pip
pip3 install --user \
    buildozer \
    cython \
    kivy \
    flask \
    wcwidth \
    requests \
    pexpect

echo "✅ Python dependencies installed"

# Install Android SDK tools (optional)
read -p "Do you want to install Android SDK tools for device testing? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📱 Installing Android SDK tools..."
    
    # Create Android directory
    mkdir -p ~/Android
    cd ~/Android
    
    # Download and install Android command line tools
    if [[ ! -d "cmdline-tools" ]]; then
        echo "Downloading Android command line tools..."
        wget -q https://dl.google.com/android/repository/commandlinetools-linux-8512546_latest.zip
        unzip -q commandlinetools-linux-8512546_latest.zip
        mkdir -p cmdline-tools/latest
        mv cmdline-tools/* cmdline-tools/latest/ 2>/dev/null || true
        rm commandlinetools-linux-8512546_latest.zip
    fi
    
    # Set up Android environment
    export ANDROID_HOME=~/Android
    export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools
    
    echo "export ANDROID_HOME=~/Android" >> ~/.bashrc
    echo "export PATH=\$PATH:\$ANDROID_HOME/cmdline-tools/latest/bin:\$ANDROID_HOME/platform-tools" >> ~/.bashrc
    
    # Accept licenses and install platform tools
    yes | $ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager --licenses 2>/dev/null || true
    $ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager "platform-tools"
    
    echo "✅ Android SDK tools installed"
fi

echo ""
echo "🎉 Installation completed!"
echo ""
echo "Next steps:"
echo "1. Reload your shell or run: source ~/.bashrc"
echo "2. Run: python3 build_apk.py"
echo "3. Choose option 5 for full setup and build"
echo ""
echo "For rooted Android devices:"
echo "- The APK will work best on rooted devices"
echo "- Enable USB debugging in Developer Options"
echo "- Connect device and run: adb devices"
echo ""
echo "============================================================"
echo "Developer: SHAKIR HOSSAIN | Website: https://shakir.com.bd"
echo "============================================================"