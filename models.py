#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WiFi Security Testing Tool - Database Models
Developer: SHAKIR HOSSAIN
Website: https://shakir.com.bd

Database models for storing scan results, attack logs, and session data.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON

db = SQLAlchemy()

class Network(db.Model):
    """Model for discovered WiFi networks"""
    __tablename__ = 'networks'
    
    id = db.Column(db.Integer, primary_key=True)
    bssid = db.Column(db.String(17), unique=True, nullable=False)  # MAC address
    ssid = db.Column(db.String(255), nullable=True)  # Network name
    channel = db.Column(db.Integer, nullable=True)
    frequency = db.Column(db.String(10), nullable=True)
    encryption = db.Column(db.String(50), nullable=True)
    signal_strength = db.Column(db.Integer, nullable=True)  # dBm
    wps_enabled = db.Column(db.Boolean, default=False)
    wps_locked = db.Column(db.Boolean, default=False)
    manufacturer = db.Column(db.String(100), nullable=True)
    first_seen = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    scan_results = db.relationship('ScanResult', backref='network', lazy=True, cascade='all, delete-orphan')
    attack_logs = db.relationship('AttackLog', backref='network', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Network {self.bssid}: {self.ssid}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'bssid': self.bssid,
            'ssid': self.ssid,
            'channel': self.channel,
            'frequency': self.frequency,
            'encryption': self.encryption,
            'signal_strength': self.signal_strength,
            'wps_enabled': self.wps_enabled,
            'wps_locked': self.wps_locked,
            'manufacturer': self.manufacturer,
            'first_seen': self.first_seen.isoformat() if self.first_seen else None,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None
        }

class ScanResult(db.Model):
    """Model for individual scan results"""
    __tablename__ = 'scan_results'
    
    id = db.Column(db.Integer, primary_key=True)
    network_id = db.Column(db.Integer, db.ForeignKey('networks.id'), nullable=False)
    scan_time = db.Column(db.DateTime, default=datetime.utcnow)
    signal_strength = db.Column(db.Integer, nullable=True)
    wps_pins = db.Column(JSON, nullable=True)  # Store generated WPS pins
    scan_type = db.Column(db.String(50), nullable=True)  # 'passive', 'active'
    interface_used = db.Column(db.String(20), nullable=True)
    
    def __repr__(self):
        return f'<ScanResult {self.id} for Network {self.network_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'network_id': self.network_id,
            'scan_time': self.scan_time.isoformat() if self.scan_time else None,
            'signal_strength': self.signal_strength,
            'wps_pins': self.wps_pins,
            'scan_type': self.scan_type,
            'interface_used': self.interface_used
        }

class AttackLog(db.Model):
    """Model for attack attempt logs"""
    __tablename__ = 'attack_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    network_id = db.Column(db.Integer, db.ForeignKey('networks.id'), nullable=False)
    attack_type = db.Column(db.String(50), nullable=False)  # 'pixie_dust', 'brute_force', 'pin_attack'
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='started')  # 'started', 'running', 'completed', 'failed', 'stopped'
    pins_tested = db.Column(JSON, nullable=True)  # Array of tested pins
    successful_pin = db.Column(db.String(20), nullable=True)
    password_found = db.Column(db.String(255), nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    interface_used = db.Column(db.String(20), nullable=True)
    command_executed = db.Column(db.Text, nullable=True)
    output_log = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<AttackLog {self.id}: {self.attack_type} on Network {self.network_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'network_id': self.network_id,
            'attack_type': self.attack_type,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'status': self.status,
            'pins_tested': self.pins_tested,
            'successful_pin': self.successful_pin,
            'password_found': self.password_found,
            'error_message': self.error_message,
            'interface_used': self.interface_used,
            'command_executed': self.command_executed,
            'output_log': self.output_log
        }

class SystemStatus(db.Model):
    """Model for system status and configuration"""
    __tablename__ = 'system_status'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    root_access = db.Column(db.Boolean, nullable=False)
    monitor_mode_active = db.Column(db.Boolean, default=False)
    active_interface = db.Column(db.String(20), nullable=True)
    dependencies_installed = db.Column(JSON, nullable=True)  # Dict of dependency status
    current_operation = db.Column(db.String(100), nullable=True)
    system_info = db.Column(JSON, nullable=True)  # System information
    
    def __repr__(self):
        return f'<SystemStatus {self.id} at {self.timestamp}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'root_access': self.root_access,
            'monitor_mode_active': self.monitor_mode_active,
            'active_interface': self.active_interface,
            'dependencies_installed': self.dependencies_installed,
            'current_operation': self.current_operation,
            'system_info': self.system_info
        }

class Session(db.Model):
    """Model for user sessions and activities"""
    __tablename__ = 'sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(255), unique=True, nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)  # IPv6 compatible
    user_agent = db.Column(db.String(500), nullable=True)
    activities = db.Column(JSON, nullable=True)  # Array of user activities
    networks_scanned = db.Column(db.Integer, default=0)
    attacks_performed = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<Session {self.session_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'activities': self.activities,
            'networks_scanned': self.networks_scanned,
            'attacks_performed': self.attacks_performed
        }