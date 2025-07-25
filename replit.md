# WiFi Security Testing Tool

## Overview

This is a WiFi Security Testing Tool built with Flask for educational and security auditing purposes. The application provides a web interface for testing WPS (WiFi Protected Setup) vulnerabilities using various attack methods including Pixie Dust and brute force attacks. The tool is developed by SHAKIR HOSSAIN and integrates several wireless security testing utilities.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a dual-platform architecture supporting both web and mobile deployments:

### Web Platform
- **Backend**: Flask web framework with Python 3
- **Frontend**: HTML/CSS/JavaScript with Bootstrap for responsive UI
- **System Integration**: Direct integration with Linux wireless tools via subprocess calls
- **Real-time Communication**: RESTful API endpoints for status updates and control

### Mobile Platform (Android APK)
- **Framework**: Kivy cross-platform GUI framework
- **Build System**: Buildozer with Python-for-Android compilation
- **Interface**: Touch-optimized native Android UI with tabbed navigation
- **Device Support**: Rooted Android devices with WiFi adapter access
- **Deployment**: APK generation for sideloading on compatible devices

## Key Components

### Backend Components

1. **app.py** - Main Flask application server
   - Serves the web interface
   - Provides REST API endpoints for system control
   - Manages global application state
   - Handles real-time status updates

2. **wifi_manager.py** - WiFi operations manager
   - Manages wireless interface operations
   - Handles monitor mode activation/deactivation
   - Controls network scanning and attack operations
   - Integrates with aircrack-ng suite tools

3. **system_utils.py** - System utility functions
   - Checks system dependencies and requirements
   - Validates root privileges
   - Monitors wireless interface capabilities
   - Manages package installation status

4. **oneshot.py** - WPS attack implementation
   - Contains WPS PIN generation algorithms
   - Implements Pixie Dust attack methods
   - Handles network address manipulation
   - Provides core security testing functionality

5. **setup.py** - Installation and dependency management
   - Automates system setup process
   - Installs required Python packages
   - Configures system dependencies
   - Handles different Linux package managers

### Mobile Components

6. **mobile_app.py** - Kivy mobile application
   - Native Android interface with touch optimization
   - Three-tab navigation (Control, Networks, Results)
   - Real-time status monitoring and updates
   - Network scanning and attack management
   - Root access verification and system setup

7. **main.py** - APK entry point
   - Application launcher for Android deployment
   - Imports and initializes mobile app
   - Handles Kivy application lifecycle

8. **build_apk.py** - APK build automation
   - Interactive build script with multiple options
   - System dependency installation
   - Android SDK/NDK environment setup
   - Buildozer integration for APK generation
   - Device installation and testing support

9. **buildozer.spec** - APK configuration
   - Android permissions and requirements
   - Python-for-Android build settings
   - APK metadata and versioning
   - Cross-compilation parameters

10. **install_build_tools.sh** - Build environment setup
    - Automated system dependency installation
    - Android SDK tools configuration
    - Development environment preparation

### Frontend Components

1. **templates/index.html** - Main web interface
   - Bootstrap-based responsive design
   - Real-time status indicators
   - Network scanning results display
   - Attack configuration modals

2. **static/script.js** - Frontend JavaScript logic
   - Handles user interactions
   - Manages real-time status updates
   - Controls attack operations
   - Implements periodic network refreshing

3. **static/style.css** - Custom styling
   - Extends Bootstrap framework
   - Provides custom badge styling
   - Enhances table and card appearances

## Data Flow

1. **System Initialization**:
   - Check root privileges and system capabilities
   - Validate required dependencies
   - Initialize wireless interface management

2. **Network Discovery**:
   - Enable monitor mode on wireless interface
   - Scan for available networks
   - Parse and display WPS-enabled targets

3. **Attack Execution**:
   - Configure attack parameters
   - Execute security testing operations
   - Monitor progress and results
   - Generate reports and logs

4. **Status Management**:
   - Continuous system status monitoring
   - Real-time updates via API endpoints
   - Error handling and user notifications

## External Dependencies

### System Tools
- **aircrack-ng** - Wireless security auditing suite
- **reaver** - WPS attack tool
- **pixiewps** - WPS PIN recovery tool
- **iw** - Wireless configuration utility
- **wireless-tools** - Legacy wireless utilities

### Python Packages
- **Flask** - Web framework for the interface
- **wcwidth** - Unicode character width calculations
- **Kivy** - Cross-platform GUI framework for mobile app
- **Buildozer** - Android APK build system
- **Cython** - Python-to-C compiler for mobile optimization
- **Pexpect** - Process automation for system integration

### Frontend Libraries
- **Bootstrap 5.1.3** - CSS framework for responsive design
- **Font Awesome 6.0.0** - Icon library for UI elements

### Mobile Development Tools
- **Android SDK** - Android development platform
- **Android NDK** - Native development kit for cross-compilation
- **Python-for-Android (p4a)** - Python runtime for Android devices
- **Java 8 JDK** - Required for Android compilation
- **Build tools** - Essential compilation utilities

## Deployment Strategy

The application supports dual deployment modes for different use cases:

### Web Deployment (Traditional)
1. **Prerequisites**:
   - Linux operating system with wireless interface
   - Root privileges for wireless operations
   - Python 3 with pip package manager

2. **Installation Process**:
   - Run setup.py to install dependencies
   - Configure wireless interface permissions
   - Start Flask development server

3. **Access Method**:
   - Web browser interface at http://localhost:5000
   - REST API endpoints for programmatic control

### Mobile Deployment (Android APK)
1. **Development Prerequisites**:
   - Linux build environment with development tools
   - Android SDK and NDK (automatically downloaded)
   - Java 8 JDK for compilation
   - Buildozer and Kivy frameworks

2. **Build Process**:
   - Run install_build_tools.sh for system setup
   - Execute build_apk.py with option 5 for full build
   - Generated APK located in bin/ directory

3. **Target Device Requirements**:
   - Rooted Android device (API 21+)
   - WiFi adapter with monitor mode capability
   - USB debugging enabled for installation
   - Storage space for APK and system tools

4. **Installation Method**:
   - ADB sideloading: adb install -r wifisecurity-1.0-debug.apk
   - Direct installation from device file manager
   - Automated installation via build script

### Security Considerations
- **Root Access**: Both deployments require elevated privileges
- **Network Isolation**: Use in controlled testing environments only
- **Legal Compliance**: Ensure authorization before testing networks
- **Device Security**: Rooting Android devices creates security risks

The tool is specifically designed for educational purposes and authorized security testing, emphasizing the importance of responsible use and proper authorization before testing any wireless networks.

## Recent Changes (January 2025)

### Android APK Implementation
- ✅ Created complete Kivy-based mobile application (mobile_app.py)
- ✅ Implemented touch-optimized three-tab interface (Control, Networks, Results)
- ✅ Added real-time status monitoring with visual indicators
- ✅ Integrated network scanning and attack management for mobile
- ✅ Built comprehensive APK build system with automated scripts

### Build System Enhancement
- ✅ Developed automated build script (build_apk.py) with interactive options
- ✅ Created system setup script (install_build_tools.sh) for dependencies
- ✅ Configured buildozer.spec with Android permissions and requirements
- ✅ Added APK installation and device testing capabilities
- ✅ Implemented cross-platform compatibility for rooted devices

### Database Integration (January 2025)
- ✅ Integrated PostgreSQL database with SQLAlchemy ORM and Flask-Migrate
- ✅ Created comprehensive data models for Networks, ScanResults, AttackLogs, SystemStatus, and Sessions
- ✅ Enhanced scan and attack operations to automatically store results in database
- ✅ Built complete database API with endpoints for data retrieval, statistics, and management
- ✅ Created interactive Database Dashboard with tabbed interface showing:
  - Network discovery history with WPS status and signal strength
  - Scan result logs with timestamps and session tracking
  - Attack attempt logs with success/failure status and recovered credentials
  - User session management and system status monitoring
- ✅ Added database seeding functionality with sample data for demonstration
- ✅ Implemented data persistence across sessions for long-term analysis
- ✅ Enhanced main interface with navigation to database dashboard

### Documentation and Deployment
- ✅ Created comprehensive APK build guide (README_APK.md)
- ✅ Updated project architecture to support dual-platform deployment
- ✅ Added mobile-specific troubleshooting and usage instructions
- ✅ Documented security considerations for rooted device usage
- ✅ Enhanced system requirements for both web and mobile platforms
- ✅ Updated architecture documentation to reflect database integration

The project now supports traditional web deployment, mobile Android APK distribution, and persistent data storage with PostgreSQL, making it a comprehensive WiFi security testing platform with historical data analysis capabilities.