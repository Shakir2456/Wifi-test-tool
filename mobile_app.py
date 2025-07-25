#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WiFi Security Testing Tool - Mobile Version
Developer: SHAKIR HOSSAIN
Website: https://shakir.com.bd
"""

try:
    import kivy
    kivy.require('2.0.0')
except ImportError:
    print("Kivy not available, running in compatibility mode")
    import sys
    sys.exit(1)

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.uix.spinner import Spinner
from kivy.uix.switch import Switch
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle

import subprocess
import threading
import time
import os
import sys
from oneshot import WPSpin
import json
import re

class StatusBar(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(40)
        self.spacing = dp(10)
        self.padding = [dp(10), dp(5)]
        
        with self.canvas.before:
            Color(0.2, 0.2, 0.2, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        
        self.bind(size=self._update_rect, pos=self._update_rect)
        
        # Root status
        self.root_label = Label(
            text='Root: Checking...', 
            size_hint_x=0.3,
            color=(1, 1, 1, 1)
        )
        self.add_widget(self.root_label)
        
        # Monitor status
        self.monitor_label = Label(
            text='Monitor: Disabled', 
            size_hint_x=0.3,
            color=(1, 1, 1, 1)
        )
        self.add_widget(self.monitor_label)
        
        # Operation status
        self.operation_label = Label(
            text='Ready', 
            size_hint_x=0.4,
            color=(1, 1, 1, 1)
        )
        self.add_widget(self.operation_label)
    
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    
    def update_status(self, root_access=False, monitor_active=False, operation=None):
        self.root_label.text = f'Root: {"Active" if root_access else "Required"}'
        self.root_label.color = (0, 1, 0, 1) if root_access else (1, 0, 0, 1)
        
        self.monitor_label.text = f'Monitor: {"Enabled" if monitor_active else "Disabled"}'
        self.monitor_label.color = (0, 1, 0, 1) if monitor_active else (0.5, 0.5, 0.5, 1)
        
        self.operation_label.text = operation or 'Ready'
        self.operation_label.color = (0, 0.8, 1, 1) if operation else (1, 1, 1, 1)

class NetworkItem(BoxLayout):
    def __init__(self, network_data, attack_callback, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(120)
        self.padding = [dp(10), dp(5)]
        self.spacing = dp(5)
        
        self.network_data = network_data
        
        # Background
        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        
        self.bind(size=self._update_rect, pos=self._update_rect)
        
        # Network info
        info_layout = BoxLayout(orientation='horizontal', size_hint_y=0.7)
        
        # Left column
        left_col = BoxLayout(orientation='vertical', size_hint_x=0.6)
        left_col.add_widget(Label(
            text=f"ESSID: {network_data.get('essid', 'Hidden')}", 
            text_size=(None, None),
            halign='left',
            color=(0, 0, 0, 1)
        ))
        left_col.add_widget(Label(
            text=f"BSSID: {network_data.get('bssid', 'Unknown')}", 
            text_size=(None, None),
            halign='left',
            color=(0, 0, 0, 1)
        ))
        left_col.add_widget(Label(
            text=f"Channel: {network_data.get('channel', 'N/A')}", 
            text_size=(None, None),
            halign='left',
            color=(0, 0, 0, 1)
        ))
        
        # Right column
        right_col = BoxLayout(orientation='vertical', size_hint_x=0.4)
        right_col.add_widget(Label(
            text=f"Power: {network_data.get('power', 'N/A')} dBm", 
            text_size=(None, None),
            halign='left',
            color=(0, 0, 0, 1)
        ))
        right_col.add_widget(Label(
            text=f"Encryption: {network_data.get('encryption', 'Unknown')}", 
            text_size=(None, None),
            halign='left',
            color=(0, 0, 0, 1)
        ))
        
        wps_pins = network_data.get('wps_pins', [])
        pin_count = len(wps_pins)
        right_col.add_widget(Label(
            text=f"WPS Pins: {pin_count}", 
            text_size=(None, None),
            halign='left',
            color=(0, 0, 0, 1)
        ))
        
        info_layout.add_widget(left_col)
        info_layout.add_widget(right_col)
        self.add_widget(info_layout)
        
        # Attack button
        attack_btn = Button(
            text='Attack Network',
            size_hint_y=0.3,
            background_color=(1, 0.2, 0.2, 1)
        )
        attack_btn.bind(on_press=lambda x: attack_callback(network_data))
        self.add_widget(attack_btn)
    
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class WiFiSecurityApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = 'WiFi Security Tool'
        self.wps_generator = WPSpin()
        self.networks = []
        self.monitor_active = False
        self.root_access = False
        self.current_operation = None
        self.scanning = False
        
    def build(self):
        # Main layout
        main_layout = BoxLayout(orientation='vertical')
        
        # Header
        header = BoxLayout(
            orientation='vertical', 
            size_hint_y=None, 
            height=dp(80),
            padding=[dp(10), dp(10)]
        )
        
        with header.canvas.before:
            Color(0.1, 0.1, 0.1, 1)
            header.rect = Rectangle(size=header.size, pos=header.pos)
        
        header.bind(size=self._update_header_rect, pos=self._update_header_rect)
        
        title_label = Label(
            text='WiFi Security Testing Tool',
            font_size='20sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=0.6
        )
        
        dev_label = Label(
            text='Developer: SHAKIR HOSSAIN | Website: https://shakir.com.bd',
            font_size='12sp',
            color=(0.8, 0.8, 0.8, 1),
            size_hint_y=0.4
        )
        
        header.add_widget(title_label)
        header.add_widget(dev_label)
        main_layout.add_widget(header)
        
        # Status bar
        self.status_bar = StatusBar()
        main_layout.add_widget(self.status_bar)
        
        # Tabbed interface
        tab_panel = TabbedPanel(do_default_tab=False)
        
        # Control tab
        control_tab = TabbedPanelItem(text='Control')
        control_layout = self.create_control_layout()
        control_tab.add_widget(control_layout)
        tab_panel.add_widget(control_tab)
        
        # Networks tab
        networks_tab = TabbedPanelItem(text='Networks')
        self.networks_layout = self.create_networks_layout()
        networks_tab.add_widget(self.networks_layout)
        tab_panel.add_widget(networks_tab)
        
        # Results tab
        results_tab = TabbedPanelItem(text='Results')
        self.results_layout = self.create_results_layout()
        results_tab.add_widget(self.results_layout)
        tab_panel.add_widget(results_tab)
        
        main_layout.add_widget(tab_panel)
        
        # Start status updates
        Clock.schedule_interval(self.update_status, 2)
        
        return main_layout
    
    def _update_header_rect(self, instance, value):
        instance.rect.pos = instance.pos
        instance.rect.size = instance.size
    
    def create_control_layout(self):
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # System setup section
        setup_section = BoxLayout(orientation='vertical', spacing=dp(5))
        setup_section.add_widget(Label(
            text='System Setup', 
            font_size='16sp', 
            bold=True,
            size_hint_y=None,
            height=dp(30),
            color=(0, 0, 0, 1)
        ))
        
        self.setup_btn = Button(
            text='Install Dependencies',
            size_hint_y=None,
            height=dp(50),
            background_color=(0.2, 0.6, 1, 1)
        )
        self.setup_btn.bind(on_press=self.setup_system)
        setup_section.add_widget(self.setup_btn)
        
        setup_section.add_widget(Label(
            text='Install required tools and modules',
            font_size='12sp',
            size_hint_y=None,
            height=dp(20),
            color=(0.5, 0.5, 0.5, 1)
        ))
        
        layout.add_widget(setup_section)
        
        # Monitor mode section
        monitor_section = BoxLayout(orientation='vertical', spacing=dp(5))
        monitor_section.add_widget(Label(
            text='Monitor Mode', 
            font_size='16sp', 
            bold=True,
            size_hint_y=None,
            height=dp(30),
            color=(0, 0, 0, 1)
        ))
        
        self.monitor_btn = Button(
            text='Enable Monitor Mode',
            size_hint_y=None,
            height=dp(50),
            background_color=(1, 0.6, 0, 1)
        )
        self.monitor_btn.bind(on_press=self.toggle_monitor_mode)
        monitor_section.add_widget(self.monitor_btn)
        
        monitor_section.add_widget(Label(
            text='Required for scanning and attacks',
            font_size='12sp',
            size_hint_y=None,
            height=dp(20),
            color=(0.5, 0.5, 0.5, 1)
        ))
        
        layout.add_widget(monitor_section)
        
        # Network operations section
        ops_section = BoxLayout(orientation='vertical', spacing=dp(5))
        ops_section.add_widget(Label(
            text='Network Operations', 
            font_size='16sp', 
            bold=True,
            size_hint_y=None,
            height=dp(30),
            color=(0, 0, 0, 1)
        ))
        
        self.scan_btn = Button(
            text='Scan Networks',
            size_hint_y=None,
            height=dp(50),
            background_color=(0, 0.8, 0.2, 1),
            disabled=True
        )
        self.scan_btn.bind(on_press=self.scan_networks)
        ops_section.add_widget(self.scan_btn)
        
        self.stop_btn = Button(
            text='Stop Operation',
            size_hint_y=None,
            height=dp(50),
            background_color=(0.8, 0.2, 0.2, 1),
            disabled=True
        )
        self.stop_btn.bind(on_press=self.stop_operation)
        ops_section.add_widget(self.stop_btn)
        
        layout.add_widget(ops_section)
        
        # Status section
        status_section = BoxLayout(orientation='vertical', spacing=dp(5))
        status_section.add_widget(Label(
            text='System Status', 
            font_size='16sp', 
            bold=True,
            size_hint_y=None,
            height=dp(30),
            color=(0, 0, 0, 1)
        ))
        
        self.status_text = Label(
            text='Click "Install Dependencies" to check system',
            font_size='12sp',
            text_size=(None, None),
            color=(0, 0, 0, 1)
        )
        status_section.add_widget(self.status_text)
        
        layout.add_widget(status_section)
        
        return layout
    
    def create_networks_layout(self):
        layout = BoxLayout(orientation='vertical', padding=dp(10))
        
        # Header
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        header.add_widget(Label(
            text='Discovered Networks', 
            font_size='16sp', 
            bold=True,
            color=(0, 0, 0, 1)
        ))
        self.network_count_label = Label(
            text='0 networks',
            font_size='12sp',
            color=(0.5, 0.5, 0.5, 1)
        )
        header.add_widget(self.network_count_label)
        layout.add_widget(header)
        
        # Networks scroll view
        self.networks_scroll = ScrollView()
        self.networks_container = BoxLayout(
            orientation='vertical',
            spacing=dp(5),
            size_hint_y=None
        )
        self.networks_container.bind(minimum_height=self.networks_container.setter('height'))
        
        # Initial message
        self.no_networks_label = Label(
            text='No networks scanned yet.\nEnable monitor mode and scan for networks.',
            font_size='14sp',
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height=dp(60)
        )
        self.networks_container.add_widget(self.no_networks_label)
        
        self.networks_scroll.add_widget(self.networks_container)
        layout.add_widget(self.networks_scroll)
        
        return layout
    
    def create_results_layout(self):
        layout = BoxLayout(orientation='vertical', padding=dp(10))
        
        layout.add_widget(Label(
            text='Attack Results', 
            font_size='16sp', 
            bold=True,
            size_hint_y=None,
            height=dp(40),
            color=(0, 0, 0, 1)
        ))
        
        self.results_scroll = ScrollView()
        self.results_text = Label(
            text='No attacks performed yet.',
            font_size='12sp',
            text_size=(None, None),
            color=(0, 0, 0, 1)
        )
        self.results_scroll.add_widget(self.results_text)
        layout.add_widget(self.results_scroll)
        
        return layout
    
    def update_status(self, dt):
        """Update system status"""
        try:
            # Check root access
            self.root_access = os.geteuid() == 0
            
            # Update UI
            self.status_bar.update_status(
                root_access=self.root_access,
                monitor_active=self.monitor_active,
                operation=self.current_operation
            )
            
            # Update button states  
            self.update_button_states()
            
        except Exception as e:
            print(f"Status update error: {e}")
    
    def update_button_states(self):
        """Update button enabled/disabled states"""
        has_operation = self.current_operation is not None
        
        self.setup_btn.disabled = has_operation
        self.monitor_btn.disabled = not self.root_access or has_operation
        self.scan_btn.disabled = not self.monitor_active or has_operation
        self.stop_btn.disabled = not has_operation
        
        # Update monitor button text
        if self.monitor_active:
            self.monitor_btn.text = 'Disable Monitor Mode'
            self.monitor_btn.background_color = (0.8, 0.2, 0.2, 1)
        else:
            self.monitor_btn.text = 'Enable Monitor Mode'
            self.monitor_btn.background_color = (1, 0.6, 0, 1)
    
    def setup_system(self, instance):
        """Setup system dependencies"""
        if not self.root_access:
            self.show_popup('Error', 'Root access required for system setup')
            return
        
        self.current_operation = 'Installing dependencies...'
        
        def run_setup():
            try:
                # Run setup script
                result = subprocess.run(['python3', 'setup.py'], 
                                      capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    self.current_operation = 'Setup completed successfully'
                    Clock.schedule_once(lambda dt: self.show_popup('Success', 'Dependencies installed successfully'), 0)
                else:
                    self.current_operation = 'Setup failed'
                    Clock.schedule_once(lambda dt: self.show_popup('Error', f'Setup failed: {result.stderr}'), 0)
                
                # Clear operation after delay
                time.sleep(3)
                self.current_operation = None
                
            except Exception as e:
                self.current_operation = f'Setup error: {str(e)}'
                Clock.schedule_once(lambda dt: self.show_popup('Error', f'Setup error: {str(e)}'), 0)
                time.sleep(3)
                self.current_operation = None
        
        thread = threading.Thread(target=run_setup)
        thread.daemon = True
        thread.start()
    
    def toggle_monitor_mode(self, instance):
        """Toggle monitor mode on/off"""
        if not self.root_access:
            self.show_popup('Error', 'Root access required for monitor mode')
            return
        
        self.current_operation = 'Toggling monitor mode...'
        
        def run_toggle():
            try:
                from wifi_manager import WiFiManager
                wifi_manager = WiFiManager()
                
                if self.monitor_active:
                    result = wifi_manager.disable_monitor_mode()
                    self.monitor_active = False
                    message = 'Monitor mode disabled'
                else:
                    result = wifi_manager.enable_monitor_mode()
                    self.monitor_active = result
                    message = 'Monitor mode enabled' if result else 'Failed to enable monitor mode'
                
                Clock.schedule_once(lambda dt: self.show_popup('Info', message), 0)
                self.current_operation = None
                
            except Exception as e:
                Clock.schedule_once(lambda dt: self.show_popup('Error', f'Monitor mode error: {str(e)}'), 0)
                self.current_operation = None
        
        thread = threading.Thread(target=run_toggle)
        thread.daemon = True
        thread.start()
    
    def scan_networks(self, instance):
        """Scan for WiFi networks"""
        if not self.monitor_active:
            self.show_popup('Error', 'Monitor mode must be enabled for scanning')
            return
        
        self.current_operation = 'Scanning for networks...'
        self.scanning = True
        
        def run_scan():
            try:
                from wifi_manager import WiFiManager
                wifi_manager = WiFiManager()
                
                networks = wifi_manager.scan_networks()
                self.networks = networks
                
                Clock.schedule_once(lambda dt: self.update_networks_display(), 0)
                
                self.current_operation = f'Found {len(networks)} networks'
                time.sleep(2)
                self.current_operation = None
                self.scanning = False
                
            except Exception as e:
                Clock.schedule_once(lambda dt: self.show_popup('Error', f'Scan error: {str(e)}'), 0)
                self.current_operation = None
                self.scanning = False
        
        thread = threading.Thread(target=run_scan)
        thread.daemon = True
        thread.start()
    
    def update_networks_display(self):
        """Update the networks display"""
        self.networks_container.clear_widgets()
        self.network_count_label.text = f'{len(self.networks)} networks'
        
        if not self.networks:
            self.no_networks_label = Label(
                text='No networks found. Try scanning again.',
                font_size='14sp',
                color=(0.5, 0.5, 0.5, 1),
                size_hint_y=None,
                height=dp(60)
            )
            self.networks_container.add_widget(self.no_networks_label)
        else:
            for network in self.networks:
                network_item = NetworkItem(network, self.attack_network)
                self.networks_container.add_widget(network_item)
    
    def attack_network(self, network_data):
        """Attack selected network"""
        bssid = network_data.get('bssid')
        essid = network_data.get('essid', 'Hidden')
        
        if not self.monitor_active:
            self.show_popup('Error', 'Monitor mode must be enabled for attacks')
            return
        
        # Show confirmation popup
        content = BoxLayout(orientation='vertical', spacing=dp(10))
        content.add_widget(Label(
            text=f'Attack network:\nESSID: {essid}\nBSSID: {bssid}',
            font_size='14sp'
        ))
        
        wps_pins = network_data.get('wps_pins', [])
        if wps_pins:
            pins_text = '\n'.join([f"{pin['name']}: {pin['pin']}" for pin in wps_pins[:3]])
            content.add_widget(Label(
                text=f'Available WPS Pins:\n{pins_text}',
                font_size='12sp'
            ))
        
        content.add_widget(Label(
            text='WARNING: This tool is for educational and authorized testing only.',
            font_size='12sp',
            color=(1, 0.5, 0, 1)
        ))
        
        button_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(50))
        
        cancel_btn = Button(text='Cancel')
        attack_btn = Button(text='Start Attack', background_color=(1, 0.2, 0.2, 1))
        
        button_layout.add_widget(cancel_btn)
        button_layout.add_widget(attack_btn)
        content.add_widget(button_layout)
        
        popup = Popup(
            title='Confirm Attack',
            content=content,
            size_hint=(0.9, 0.7)
        )
        
        cancel_btn.bind(on_press=popup.dismiss)
        attack_btn.bind(on_press=lambda x: self.start_attack(network_data, popup))
        
        popup.open()
    
    def start_attack(self, network_data, popup):
        """Start the actual attack"""
        popup.dismiss()
        
        bssid = network_data.get('bssid')
        essid = network_data.get('essid', 'Hidden')
        
        self.current_operation = f'Attacking {essid}...'
        
        def run_attack():
            try:
                from wifi_manager import WiFiManager
                wifi_manager = WiFiManager()
                
                result = wifi_manager.attack_network(bssid, essid)
                
                if result['success']:
                    message = f"Attack successful!\nPassword: {result.get('password', 'Not found')}"
                    Clock.schedule_once(lambda dt: self.show_popup('Success', message), 0)
                    Clock.schedule_once(lambda dt: self.update_results(f"Attack successful on {essid}: {result.get('password', 'Password found')}"), 0)
                else:
                    message = f"Attack failed: {result.get('error', 'Unknown error')}"
                    Clock.schedule_once(lambda dt: self.show_popup('Failed', message), 0)
                    Clock.schedule_once(lambda dt: self.update_results(f"Attack failed on {essid}: {result.get('error', 'Unknown error')}"), 0)
                
                self.current_operation = None
                
            except Exception as e:
                Clock.schedule_once(lambda dt: self.show_popup('Error', f'Attack error: {str(e)}'), 0)
                Clock.schedule_once(lambda dt: self.update_results(f"Attack error on {essid}: {str(e)}"), 0)
                self.current_operation = None
        
        thread = threading.Thread(target=run_attack)
        thread.daemon = True
        thread.start()
    
    def update_results(self, result_text):
        """Update attack results"""
        current_text = self.results_text.text
        if current_text == 'No attacks performed yet.':
            self.results_text.text = result_text
        else:
            self.results_text.text = f"{current_text}\n\n{result_text}"
    
    def stop_operation(self, instance):
        """Stop current operation"""
        try:
            # Kill processes
            subprocess.run(['pkill', '-f', 'airodump-ng'], capture_output=True)
            subprocess.run(['pkill', '-f', 'reaver'], capture_output=True)
            
            self.current_operation = None
            self.scanning = False
            self.show_popup('Info', 'Operation stopped')
            
        except Exception as e:
            self.show_popup('Error', f'Stop error: {str(e)}')
    
    def show_popup(self, title, message):
        """Show popup message"""
        content = BoxLayout(orientation='vertical', spacing=dp(10))
        content.add_widget(Label(text=message, font_size='14sp'))
        
        close_btn = Button(text='Close', size_hint_y=None, height=dp(40))
        content.add_widget(close_btn)
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.8, 0.6)
        )
        
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

if __name__ == '__main__':
    WiFiSecurityApp().run()