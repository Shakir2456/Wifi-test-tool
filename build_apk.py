#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APK Build Script for WiFi Security Testing Tool
Developer: SHAKIR HOSSAIN
Website: https://shakir.com.bd

This script automates the APK building process using Buildozer.
"""

import os
import sys
import subprocess
import platform
import shutil
import time
from pathlib import Path

class APKBuilder:
    def __init__(self):
        self.project_root = Path.cwd()
        self.buildozer_spec = self.project_root / "buildozer.spec"
        self.main_py = self.project_root / "main.py"
        
    def check_system(self):
        """Check system requirements for APK building"""
        print("=" * 60)
        print("WiFi Security Tool - APK Builder")
        print("Developer: SHAKIR HOSSAIN")
        print("Website: https://shakir.com.bd")
        print("=" * 60)
        
        print(f"System: {platform.system()} {platform.release()}")
        print(f"Python: {sys.version.split()[0]}")
        print(f"Working Directory: {self.project_root}")
        print()
        
        # Check if we're on Linux (required for Android building)
        if platform.system() != "Linux":
            print("❌ Error: Android APK building requires Linux")
            return False
        
        # Check if buildozer.spec exists
        if not self.buildozer_spec.exists():
            print("❌ Error: buildozer.spec not found")
            return False
        
        # Check if main.py exists
        if not self.main_py.exists():
            print("❌ Error: main.py not found")
            return False
        
        print("✅ System check passed")
        return True
    
    def install_dependencies(self):
        """Install required system dependencies for building"""
        print("\n📦 Installing build dependencies...")
        
        dependencies = [
            'build-essential',
            'git',
            'python3-dev',
            'python3-pip',
            'openjdk-8-jdk',
            'unzip',
            'zlib1g-dev',
            'libncurses5-dev',
            'libncursesw5-dev',
            'libtinfo5',
            'cmake',
            'libffi-dev',
            'libssl-dev',
            'automake',
            'autoconf',
            'libtool',
            'pkg-config',
            'libltdl-dev'
        ]
        
        try:
            # Update package lists
            print("Updating package lists...")
            subprocess.run(['sudo', 'apt-get', 'update'], check=True)
            
            # Install dependencies
            for dep in dependencies:
                print(f"Installing {dep}...")
                result = subprocess.run(['sudo', 'apt-get', 'install', '-y', dep], 
                                      capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"Warning: Failed to install {dep}")
            
            print("✅ System dependencies installed")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error installing dependencies: {e}")
            return False
    
    def setup_android_environment(self):
        """Setup Android SDK environment"""
        print("\n🤖 Setting up Android environment...")
        
        # Set JAVA_HOME
        java_home = "/usr/lib/jvm/java-8-openjdk-amd64"
        if os.path.exists(java_home):
            os.environ['JAVA_HOME'] = java_home
            print(f"✅ JAVA_HOME set to {java_home}")
        else:
            print("❌ Warning: Java 8 not found")
        
        # Initialize buildozer (this will download Android SDK/NDK)
        try:
            print("Initializing buildozer (this may take a while)...")
            subprocess.run(['buildozer', 'init'], check=True, cwd=self.project_root)
            print("✅ Buildozer initialized")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error initializing buildozer: {e}")
            return False
    
    def build_debug_apk(self):
        """Build debug APK"""
        print("\n🔨 Building debug APK...")
        print("This process may take 30-60 minutes for first build...")
        
        try:
            # Build debug APK
            process = subprocess.Popen(
                ['buildozer', 'android', 'debug'],
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Show real-time output
            for line in process.stdout:
                print(line.rstrip())
            
            process.wait()
            
            if process.returncode == 0:
                print("✅ Debug APK built successfully!")
                
                # Find the APK file
                bin_dir = self.project_root / "bin"
                if bin_dir.exists():
                    apk_files = list(bin_dir.glob("*.apk"))
                    if apk_files:
                        apk_file = apk_files[0]
                        print(f"📱 APK location: {apk_file}")
                        print(f"📏 APK size: {apk_file.stat().st_size / (1024*1024):.1f} MB")
                        return str(apk_file)
                
                return True
            else:
                print("❌ APK build failed")
                return False
                
        except Exception as e:
            print(f"❌ Build error: {e}")
            return False
    
    def build_release_apk(self):
        """Build release APK"""
        print("\n🔨 Building release APK...")
        
        try:
            process = subprocess.Popen(
                ['buildozer', 'android', 'release'],
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            for line in process.stdout:
                print(line.rstrip())
            
            process.wait()
            
            if process.returncode == 0:
                print("✅ Release APK built successfully!")
                return True
            else:
                print("❌ Release APK build failed")
                return False
                
        except Exception as e:
            print(f"❌ Build error: {e}")
            return False
    
    def clean_build(self):
        """Clean build artifacts"""
        print("\n🧹 Cleaning build artifacts...")
        
        try:
            subprocess.run(['buildozer', 'android', 'clean'], 
                         check=True, cwd=self.project_root)
            print("✅ Build cleaned")
        except subprocess.CalledProcessError as e:
            print(f"❌ Clean failed: {e}")
    
    def install_apk(self, apk_path):
        """Install APK to connected Android device"""
        print(f"\n📱 Installing APK: {apk_path}")
        
        try:
            # Check if adb is available
            subprocess.run(['adb', 'version'], check=True, capture_output=True)
            
            # Check for devices
            result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
            if 'device' not in result.stdout:
                print("❌ No Android device connected")
                print("Connect your device and enable USB debugging")
                return False
            
            # Install APK
            subprocess.run(['adb', 'install', '-r', apk_path], check=True)
            print("✅ APK installed successfully!")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Installation failed: {e}")
            return False
        except FileNotFoundError:
            print("❌ ADB not found. Install Android SDK platform-tools")
            return False

def main():
    builder = APKBuilder()
    
    if not builder.check_system():
        sys.exit(1)
    
    print("\nSelect build option:")
    print("1. Install dependencies only")
    print("2. Build debug APK")
    print("3. Build release APK") 
    print("4. Clean build")
    print("5. Full setup and build")
    
    try:
        choice = input("\nEnter your choice (1-5): ").strip()
    except KeyboardInterrupt:
        print("\n❌ Build cancelled")
        sys.exit(1)
    
    if choice == '1':
        builder.install_dependencies()
        
    elif choice == '2':
        apk_path = builder.build_debug_apk()
        if apk_path and isinstance(apk_path, str):
            install = input("\nInstall APK to connected device? (y/n): ").strip().lower()
            if install == 'y':
                builder.install_apk(apk_path)
    
    elif choice == '3':
        apk_path = builder.build_release_apk()
        if apk_path and isinstance(apk_path, str):
            install = input("\nInstall APK to connected device? (y/n): ").strip().lower()
            if install == 'y':
                builder.install_apk(apk_path)
    
    elif choice == '4':
        builder.clean_build()
    
    elif choice == '5':
        print("\n🚀 Starting full setup and build process...")
        if (builder.install_dependencies() and 
            builder.setup_android_environment()):
            
            apk_path = builder.build_debug_apk()
            if apk_path and isinstance(apk_path, str):
                install = input("\nInstall APK to connected device? (y/n): ").strip().lower()
                if install == 'y':
                    builder.install_apk(apk_path)
    
    else:
        print("❌ Invalid choice")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("Build process completed!")
    print("Developer: SHAKIR HOSSAIN | Website: https://shakir.com.bd")
    print("=" * 60)

if __name__ == "__main__":
    main()