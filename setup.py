#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup script for WiFi Security Testing Tool
Developer: SHAKIR HOSSAIN
Website: https://shakir.com.bd
"""

import os
import sys
import subprocess
import platform

def check_root():
    """Check if running with root privileges"""
    return os.geteuid() == 0

def install_python_dependencies():
    """Install Python dependencies"""
    packages = ['flask', 'wcwidth']
    
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', package], check=True)
            print(f"✓ {package} installed successfully")
        except subprocess.CalledProcessError:
            print(f"✗ Failed to install {package}")
            return False
    return True

def install_system_dependencies():
    """Install system dependencies"""
    if not check_root():
        print("Root privileges required for system dependency installation")
        print("Please run: sudo python3 setup.py")
        return False
    
    # Detect package manager
    package_managers = {
        'apt-get': ['apt-get', 'update'],
        'yum': ['yum', 'update'],
        'pacman': ['pacman', '-Sy'],
        'zypper': ['zypper', 'refresh']
    }
    
    package_manager = None
    for pm in package_managers:
        if subprocess.run(['which', pm], capture_output=True).returncode == 0:
            package_manager = pm
            break
    
    if not package_manager:
        print("No supported package manager found")
        return False
    
    print(f"Using package manager: {package_manager}")
    
    # Update package lists
    try:
        print("Updating package lists...")
        subprocess.run(package_managers[package_manager], check=True)
    except subprocess.CalledProcessError:
        print("Failed to update package lists")
        return False
    
    # Define packages for different package managers
    packages = {
        'apt-get': ['aircrack-ng', 'reaver', 'pixiewps', 'iw', 'wireless-tools', 'python3-pip'],
        'yum': ['aircrack-ng', 'reaver', 'pixiewps', 'iw', 'wireless-tools', 'python3-pip'],
        'pacman': ['aircrack-ng', 'reaver', 'pixiewps', 'iw', 'wireless_tools', 'python-pip'],
        'zypper': ['aircrack-ng', 'reaver', 'pixiewps', 'iw', 'wireless-tools', 'python3-pip']
    }
    
    install_commands = {
        'apt-get': ['apt-get', 'install', '-y'],
        'yum': ['yum', 'install', '-y'],
        'pacman': ['pacman', '-S', '--noconfirm'],
        'zypper': ['zypper', 'install', '-y']
    }
    
    # Install packages
    for package in packages[package_manager]:
        try:
            print(f"Installing {package}...")
            cmd = install_commands[package_manager] + [package]
            subprocess.run(cmd, check=True)
            print(f"✓ {package} installed successfully")
        except subprocess.CalledProcessError:
            print(f"✗ Failed to install {package}")
            # Continue with other packages
    
    return True

def setup_permissions():
    """Setup proper permissions"""
    if not check_root():
        return True
    
    try:
        # Get the actual user (not root when using sudo)
        username = os.environ.get('SUDO_USER', os.environ.get('USER'))
        if username and username != 'root':
            print(f"Adding user {username} to netdev group...")
            subprocess.run(['usermod', '-a', '-G', 'netdev', username])
        
        # Set capabilities for wireless tools
        tools = [
            '/usr/bin/reaver',
            '/usr/bin/airodump-ng',
            '/usr/bin/aircrack-ng',
            '/usr/sbin/airmon-ng'
        ]
        
        for tool in tools:
            if os.path.exists(tool):
                print(f"Setting capabilities for {tool}...")
                subprocess.run(['setcap', 'cap_net_raw,cap_net_admin=eip', tool], 
                             capture_output=True)
        
        return True
    except Exception as e:
        print(f"Warning: Could not set all permissions: {e}")
        return True

def create_desktop_shortcut():
    """Create desktop shortcut"""
    try:
        desktop_path = os.path.expanduser("~/Desktop")
        if not os.path.exists(desktop_path):
            return
        
        shortcut_content = f"""[Desktop Entry]
Name=WiFi Security Tool
Comment=WiFi Security Testing Tool by SHAKIR HOSSAIN
Exec=python3 {os.path.abspath('app.py')}
Terminal=true
Type=Application
Icon=network-wireless
Categories=Network;Security;
"""
        
        shortcut_path = os.path.join(desktop_path, "wifi-security-tool.desktop")
        with open(shortcut_path, 'w') as f:
            f.write(shortcut_content)
        
        os.chmod(shortcut_path, 0o755)
        print(f"✓ Desktop shortcut created: {shortcut_path}")
        
    except Exception as e:
        print(f"Warning: Could not create desktop shortcut: {e}")

def main():
    print("=" * 60)
    print("WiFi Security Testing Tool - Setup")
    print("Developer: SHAKIR HOSSAIN")
    print("Website: https://shakir.com.bd")
    print("=" * 60)
    
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Root access: {'Yes' if check_root() else 'No'}")
    print()
    
    # Install Python dependencies
    print("Step 1: Installing Python dependencies...")
    if not install_python_dependencies():
        print("Failed to install Python dependencies")
        sys.exit(1)
    print()
    
    # Install system dependencies
    print("Step 2: Installing system dependencies...")
    if not install_system_dependencies():
        print("Failed to install system dependencies")
        print("You may need to install them manually:")
        print("- aircrack-ng")
        print("- reaver") 
        print("- pixiewps")
        print("- iw")
        print("- wireless-tools")
    print()
    
    # Setup permissions
    print("Step 3: Setting up permissions...")
    setup_permissions()
    print()
    
    # Create desktop shortcut
    print("Step 4: Creating desktop shortcut...")
    create_desktop_shortcut()
    print()
    
    print("=" * 60)
    print("Setup completed!")
    print()
    print("To run the application:")
    print("  sudo python3 app.py")
    print()
    print("Or use the desktop shortcut if created.")
    print("=" * 60)

if __name__ == "__main__":
    main()
