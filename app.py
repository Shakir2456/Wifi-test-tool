#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WiFi Security Testing Tool
Developer: SHAKIR HOSSAIN
Website: https://shakir.com.bd
"""

from flask import Flask, render_template, jsonify, request, session as flask_session
from flask_migrate import Migrate
import os
import sys
import subprocess
import json
import threading
import time
from datetime import datetime
import uuid
from wifi_manager import WiFiManager
from system_utils import SystemUtils
from models import db, Network, ScanResult, AttackLog, SystemStatus, Session
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "wifi-security-tool-key"

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)

# Global instances
wifi_manager = WiFiManager()
system_utils = SystemUtils()

# Global state
scan_results = []
monitor_mode_active = False
current_operation = None

# Initialize database
with app.app_context():
    db.create_all()
    logger.info("Database initialized")

def get_or_create_session():
    """Get or create a session for the current user"""
    if 'session_id' not in flask_session:
        flask_session['session_id'] = str(uuid.uuid4())
        
        # Create database session record
        session_record = Session(
            session_id=flask_session['session_id'],
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')[:500]
        )
        db.session.add(session_record)
        db.session.commit()
    
    return flask_session['session_id']

def log_system_status():
    """Log current system status to database"""
    try:
        interfaces = wifi_manager.get_wireless_interfaces()
        active_interface = interfaces[0] if interfaces else None
        
        status = SystemStatus(
            root_access=system_utils.check_root(),
            monitor_mode_active=monitor_mode_active,
            active_interface=active_interface,
            dependencies_installed=system_utils.check_dependencies(),
            current_operation=current_operation,
            system_info={
                'os': sys.platform,
                'python_version': sys.version.split()[0]
            }
        )
        db.session.add(status)
        db.session.commit()
    except Exception as e:
        logger.error(f"Failed to log system status: {e}")

@app.route('/')
def index():
    """Main interface page"""
    return render_template('index.html')

@app.route('/database')
def database_dashboard():
    """Database dashboard page"""
    return render_template('database.html')

@app.route('/api/status')
def get_status():
    """Get system and application status"""
    try:
        session_id = get_or_create_session()
        root_access = system_utils.check_root()
        monitor_capable = system_utils.check_monitor_capability()
        dependencies = system_utils.check_dependencies()
        
        # Log system status periodically
        log_system_status()
        
        # Get network count from database
        network_count = Network.query.count()
        recent_scans = ScanResult.query.filter(
            ScanResult.scan_time >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        ).count()
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'root_access': root_access,
            'monitor_capable': monitor_capable,
            'dependencies': dependencies,
            'monitor_mode_active': monitor_mode_active,
            'current_operation': current_operation,
            'networks_found': len(scan_results),
            'networks_in_db': network_count,
            'scans_today': recent_scans
        })
    except Exception as e:
        logger.error(f"Status check error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/setup', methods=['POST'])
def setup_system():
    """Setup system dependencies"""
    try:
        if not system_utils.check_root():
            return jsonify({
                'success': False, 
                'error': 'Root access required for system setup'
            })
        
        # Run setup in background thread
        def run_setup():
            global current_operation
            current_operation = 'Installing dependencies...'
            try:
                system_utils.install_dependencies()
                current_operation = 'Setup completed successfully'
                time.sleep(3)
                current_operation = None
            except Exception as e:
                current_operation = f'Setup failed: {str(e)}'
                time.sleep(5)
                current_operation = None
        
        thread = threading.Thread(target=run_setup)
        thread.daemon = True
        thread.start()
        
        return jsonify({'success': True, 'message': 'Setup started in background'})
        
    except Exception as e:
        logger.error(f"Setup error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/monitor/toggle', methods=['POST'])
def toggle_monitor_mode():
    """Toggle monitor mode on/off"""
    global monitor_mode_active, current_operation
    
    try:
        if not system_utils.check_root():
            return jsonify({
                'success': False, 
                'error': 'Root access required for monitor mode'
            })
        
        current_operation = 'Toggling monitor mode...'
        
        if monitor_mode_active:
            # Disable monitor mode
            result = wifi_manager.disable_monitor_mode()
            monitor_mode_active = False
            message = 'Monitor mode disabled'
        else:
            # Enable monitor mode
            result = wifi_manager.enable_monitor_mode()
            monitor_mode_active = result
            message = 'Monitor mode enabled' if result else 'Failed to enable monitor mode'
        
        current_operation = None
        
        return jsonify({
            'success': result or not monitor_mode_active,
            'monitor_active': monitor_mode_active,
            'message': message
        })
        
    except Exception as e:
        current_operation = None
        logger.error(f"Monitor mode toggle error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/scan', methods=['POST'])
def scan_networks():
    """Scan for WiFi networks"""
    global scan_results, current_operation
    
    try:
        if not monitor_mode_active:
            return jsonify({
                'success': False, 
                'error': 'Monitor mode must be enabled for scanning'
            })
        
        current_operation = 'Scanning for networks...'
        
        # Run scan in background thread
        def run_scan():
            global scan_results, current_operation
            try:
                scan_results = wifi_manager.scan_networks()
                
                # Store scan results in database
                session_id = get_or_create_session()
                for network_data in scan_results:
                    # Find or create network record
                    network = Network.query.filter_by(bssid=network_data.get('bssid')).first()
                    if not network:
                        network = Network(
                            bssid=network_data.get('bssid'),
                            ssid=network_data.get('essid', ''),
                            channel=network_data.get('channel'),
                            encryption=network_data.get('privacy', ''),
                            signal_strength=network_data.get('power'),
                            wps_enabled=network_data.get('wps', False),
                            wps_locked=network_data.get('locked', False)
                        )
                        db.session.add(network)
                        db.session.flush()  # Get the ID
                    
                    # Create scan result record
                    scan_result = ScanResult(
                        network_id=network.id,
                        session_id=session_id,
                        signal_strength=network_data.get('power'),
                        scan_data=network_data
                    )
                    db.session.add(scan_result)
                
                db.session.commit()
                current_operation = f'Found {len(scan_results)} networks (saved to database)'
                time.sleep(2)
                current_operation = None
            except Exception as e:
                db.session.rollback()
                current_operation = f'Scan failed: {str(e)}'
                time.sleep(3)
                current_operation = None
        
        thread = threading.Thread(target=run_scan)
        thread.daemon = True
        thread.start()
        
        return jsonify({'success': True, 'message': 'Scan started'})
        
    except Exception as e:
        current_operation = None
        logger.error(f"Scan error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/networks')
def get_networks():
    """Get scanned networks"""
    return jsonify({
        'success': True,
        'networks': scan_results
    })

@app.route('/api/attack', methods=['POST'])
def attack_network():
    """Attack selected network"""
    global current_operation
    
    try:
        data = request.get_json()
        bssid = data.get('bssid')
        essid = data.get('essid')
        
        if not bssid:
            return jsonify({'success': False, 'error': 'BSSID required'})
        
        if not monitor_mode_active:
            return jsonify({
                'success': False, 
                'error': 'Monitor mode must be enabled for attacks'
            })
        
        # Run attack in background thread
        def run_attack():
            global current_operation
            current_operation = f'Attacking {essid or bssid}...'
            session_id = get_or_create_session()
            attack_log = None
            
            try:
                # Find or create network record
                network = Network.query.filter_by(bssid=bssid).first()
                if not network:
                    network = Network(
                        bssid=bssid,
                        ssid=essid or '',
                        wps_enabled=True  # Assume WPS if we're attacking
                    )
                    db.session.add(network)
                    db.session.flush()
                
                # Create attack log entry
                attack_log = AttackLog(
                    network_id=network.id,
                    attack_type='pixie_dust'
                )
                db.session.add(attack_log)
                db.session.flush()
                
                # Perform the attack
                result = wifi_manager.attack_network(bssid, essid)
                
                # Update attack log with results
                attack_log.end_time = datetime.utcnow()
                attack_log.status = 'completed' if result['success'] else 'failed'
                attack_log.error_message = result.get('error', '')
                
                if result['success']:
                    attack_log.successful_pin = result.get('pin', '')
                    attack_log.password_found = result.get('password', '')
                    current_operation = f'Attack completed: {result.get("message", "")}'
                else:
                    current_operation = f'Attack failed: {result.get("error", "")}'
                
                db.session.commit()
                time.sleep(5)
                current_operation = None
                
            except Exception as e:
                if attack_log:
                    attack_log.end_time = datetime.utcnow()
                    attack_log.status = 'error'
                    attack_log.error_message = str(e)
                    db.session.commit()
                else:
                    db.session.rollback()
                    
                current_operation = f'Attack error: {str(e)}'
                time.sleep(5)
                current_operation = None
        
        thread = threading.Thread(target=run_attack)
        thread.daemon = True
        thread.start()
        
        return jsonify({'success': True, 'message': 'Attack started'})
        
    except Exception as e:
        current_operation = None
        logger.error(f"Attack error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/stop', methods=['POST'])
def stop_operation():
    """Stop current operation"""
    global current_operation
    
    try:
        wifi_manager.stop_current_operation()
        current_operation = None
        return jsonify({'success': True, 'message': 'Operation stopped'})
    except Exception as e:
        logger.error(f"Stop operation error: {e}")
        return jsonify({'success': False, 'error': str(e)})

# Database API Endpoints

@app.route('/api/db/networks')
def get_db_networks():
    """Get all networks from database"""
    try:
        networks = Network.query.all()
        return jsonify({
            'success': True,
            'networks': [network.to_dict() for network in networks]
        })
    except Exception as e:
        logger.error(f"Database networks error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/db/networks/<int:network_id>')
def get_network_details(network_id):
    """Get detailed information about a specific network"""
    try:
        network = Network.query.get_or_404(network_id)
        scan_results = ScanResult.query.filter_by(network_id=network_id).all()
        attack_logs = AttackLog.query.filter_by(network_id=network_id).all()
        
        return jsonify({
            'success': True,
            'network': network.to_dict(),
            'scan_results': [scan.to_dict() for scan in scan_results],
            'attack_logs': [log.to_dict() for log in attack_logs]
        })
    except Exception as e:
        logger.error(f"Network details error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/db/attacks')
def get_attack_logs():
    """Get all attack logs from database"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        attacks = AttackLog.query.order_by(AttackLog.start_time.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'attacks': [attack.to_dict() for attack in attacks.items],
            'total': attacks.total,
            'pages': attacks.pages,
            'current_page': page
        })
    except Exception as e:
        logger.error(f"Attack logs error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/db/scans')
def get_scan_results():
    """Get scan results from database"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        scans = ScanResult.query.order_by(ScanResult.scan_time.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'scans': [scan.to_dict() for scan in scans.items],
            'total': scans.total,
            'pages': scans.pages,
            'current_page': page
        })
    except Exception as e:
        logger.error(f"Scan results error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/db/sessions')
def get_sessions():
    """Get user sessions from database"""
    try:
        sessions = Session.query.order_by(Session.start_time.desc()).limit(20).all()
        return jsonify({
            'success': True,
            'sessions': [session.to_dict() for session in sessions]
        })
    except Exception as e:
        logger.error(f"Sessions error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/db/stats')
def get_database_stats():
    """Get database statistics"""
    try:
        stats = {
            'total_networks': Network.query.count(),
            'total_scans': ScanResult.query.count(),
            'total_attacks': AttackLog.query.count(),
            'total_sessions': Session.query.count(),
            'successful_attacks': AttackLog.query.filter(
                AttackLog.successful_pin.isnot(None)
            ).count(),
            'networks_with_wps': Network.query.filter_by(wps_enabled=True).count(),
            'recent_activity': {
                'scans_today': ScanResult.query.filter(
                    ScanResult.scan_time >= datetime.utcnow().replace(
                        hour=0, minute=0, second=0, microsecond=0
                    )
                ).count(),
                'attacks_today': AttackLog.query.filter(
                    AttackLog.start_time >= datetime.utcnow().replace(
                        hour=0, minute=0, second=0, microsecond=0
                    )
                ).count()
            }
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        logger.error(f"Database stats error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/db/clear', methods=['POST'])
def clear_database():
    """Clear database records (admin function)"""
    try:
        data = request.get_json()
        table = data.get('table', 'all')
        
        if table == 'all':
            AttackLog.query.delete()
            ScanResult.query.delete()
            Network.query.delete()
            SystemStatus.query.delete()
            # Keep sessions for tracking
        elif table == 'networks':
            Network.query.delete()
        elif table == 'scans':
            ScanResult.query.delete()
        elif table == 'attacks':
            AttackLog.query.delete()
        elif table == 'status':
            SystemStatus.query.delete()
        else:
            return jsonify({'success': False, 'error': 'Invalid table specified'})
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Cleared {table} records from database'
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Database clear error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/db/seed', methods=['POST'])
def seed_database():
    """Seed database with sample data for demonstration"""
    try:
        # Create sample networks directly
        network1 = Network(
            bssid='00:11:22:33:44:55',
            ssid='TestNetwork_WPS',
            channel=6,
            encryption='WPA2',
            signal_strength=-45,
            wps_enabled=True
        )
        
        network2 = Network(
            bssid='AA:BB:CC:DD:EE:FF',
            ssid='SecureWiFi',
            channel=11,
            encryption='WPA3',
            signal_strength=-52,
            wps_enabled=False
        )
        
        network3 = Network(
            bssid='11:22:33:44:55:66',
            ssid='OpenNetwork',
            channel=1,
            encryption='Open',
            signal_strength=-38,
            wps_enabled=True,
            wps_locked=False
        )
        
        # Check if they already exist
        existing1 = Network.query.filter_by(bssid='00:11:22:33:44:55').first()
        existing2 = Network.query.filter_by(bssid='AA:BB:CC:DD:EE:FF').first()
        existing3 = Network.query.filter_by(bssid='11:22:33:44:55:66').first()
        
        networks_added = 0
        
        if not existing1:
            db.session.add(network1)
            db.session.flush()
            
            # Add sample scan result
            scan1 = ScanResult(network_id=network1.id, signal_strength=-45)
            db.session.add(scan1)
            
            # Add successful attack log
            attack1 = AttackLog(
                network_id=network1.id,
                attack_type='pixie_dust',
                end_time=datetime.utcnow(),
                status='completed',
                successful_pin='12345670',
                password_found='testpass123'
            )
            db.session.add(attack1)
            networks_added += 1
        
        if not existing2:
            db.session.add(network2)
            db.session.flush()
            
            scan2 = ScanResult(network_id=network2.id, signal_strength=-52)
            db.session.add(scan2)
            networks_added += 1
        
        if not existing3:
            db.session.add(network3)
            db.session.flush()
            
            scan3 = ScanResult(network_id=network3.id, signal_strength=-38)
            db.session.add(scan3)
            
            # Add failed attack log
            attack3 = AttackLog(
                network_id=network3.id,
                attack_type='pixie_dust',
                end_time=datetime.utcnow(),
                status='failed',
                error_message='WPS locked after too many attempts'
            )
            db.session.add(attack3)
            networks_added += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Database seeded with {networks_added} new sample networks'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Database seed error: {e}")
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    print("=" * 60)
    print("WiFi Security Testing Tool")
    print("Developer: SHAKIR HOSSAIN")
    print("Website: https://shakir.com.bd")
    print("=" * 60)
    
    # Check if running as root
    if os.geteuid() != 0:
        print("WARNING: Not running as root. Some features may not work.")
        print("For full functionality, run with: sudo python3 app.py")
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
