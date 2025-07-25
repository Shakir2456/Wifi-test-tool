#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
System utilities for dependency management and system checks
"""

import os
import subprocess
import sys
import logging

logger = logging.getLogger(__name__)

class SystemUtils:
    def __init__(self):
        self.required_packages = [
            'aircrack-ng',
            'reaver',
            'pixiewps',
            'iw',
            'wireless-tools'
        ]
        
        self.python_packages = [
            'flask',
            'wcwidth'
        ]
    
    def check_root(self):
        """Check if running with root privileges"""
        return os.geteuid() == 0
    
    def check_monitor_capability(self):
        """Check if system supports monitor mode"""
        try:
            result = subprocess.run(['iw', 'list'], capture_output=True, text=True)
            return 'monitor' in result.stdout.lower()
        except:
            return False
    
    def check_dependencies(self):
        """Check if all required dependencies are installed"""
        status = {}
        
        # Check system packages
        for package in self.required_packages:
            status[package] = self._check_package_installed(package)
        
        # Check Python packages
        for package in self.python_packages:
            status[f"python-{package}"] = self._check_python_package(package)
        
        return status
    
    def _check_package_installed(self, package):
        """Check if a system package is installed"""
        try:
            result = subprocess.run(['which', package], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def _check_python_package(self, package):
        """Check if a Python package is installed"""
        try:
            __import__(package)
            return True
        except ImportError:
            return False
    
    def install_dependencies(self):
        """Install all required dependencies"""
        if not self.check_root():
            raise Exception("Root access required for installation")
        
        try:
            # Update package lists
            logger.info("Updating package lists...")
            subprocess.run(['apt-get', 'update'], check=True)
            
            # Install system packages
            logger.info("Installing system packages...")
            for package in self.required_packages:
                if not self._check_package_installed(package):
                    logger.info(f"Installing {package}...")
                    subprocess.run(['apt-get', 'install', '-y', package], check=True)
            
            # Install Python packages
            logger.info("Installing Python packages...")
            for package in self.python_packages:
                if not self._check_python_package(package):
                    logger.info(f"Installing python-{package}...")
                    subprocess.run([sys.executable, '-m', 'pip', 'install', package], check=True)
            
            logger.info("All dependencies installed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to install dependencies: {e}")
            raise
    
    def setup_permissions(self):
        """Setup proper permissions for wireless operations"""
        try:
            # Add user to required groups
            username = os.environ.get('SUDO_USER', os.environ.get('USER'))
            if username:
                subprocess.run(['usermod', '-a', '-G', 'netdev', username])
            
            # Set capabilities for tools
            tools = ['/usr/bin/reaver', '/usr/bin/airodump-ng', '/usr/bin/aircrack-ng']
            for tool in tools:
                if os.path.exists(tool):
                    subprocess.run(['setcap', 'cap_net_raw,cap_net_admin=eip', tool])
            
        except Exception as e:
            logger.error(f"Failed to setup permissions: {e}")
    
    def get_system_info(self):
        """Get system information"""
        info = {}
        
        try:
            # OS information
            with open('/etc/os-release', 'r') as f:
                for line in f:
                    if line.startswith('PRETTY_NAME='):
                        info['os'] = line.split('=')[1].strip().strip('"')
                        break
        except:
            info['os'] = 'Unknown'
        
        # Kernel version
        try:
            result = subprocess.run(['uname', '-r'], capture_output=True, text=True)
            info['kernel'] = result.stdout.strip()
        except:
            info['kernel'] = 'Unknown'
        
        # Python version
        info['python'] = sys.version.split()[0]
        
        # Root status
        info['root'] = self.check_root()
        
        return info
