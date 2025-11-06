# SignalCraft - Industrial Compressor Audio Analysis System

## Overview

SignalCraft is an AI-powered system for monitoring and analyzing industrial compressor audio signals to detect anomalies, failures, and maintenance needs. The system integrates edge computing with IoT sensors (ESP32), machine learning models, and a comprehensive dashboard for monitoring and analysis.

## Project Structure

```
signalcraft/
├── .github/                    # GitHub configuration and workflows
│   └── workflows/              # CI/CD pipelines (auto-deploy.yml, deploy.yml, etc.)
├── admin/                      # Administrative interface and management
│   ├── routes/                 # Admin API routes
│   ├── services/               # Admin business logic
│   ├── static/                 # Admin static assets (CSS, JS)
│   └── templates/              # Admin HTML templates
├── ai/                         # AI and machine learning components
│   ├── ai_model_trainer.py     # Core model training script
│   ├── anomaly_detection_ai.py # Anomaly detection algorithms
│   ├── synthetic_data_generator.py # Synthetic data generation
│   ├── engineer_domain_knowledge_ai.py # Engineer knowledge integration
│   └── [60+ AI/ML files]       # Various AI models and utilities
├── assets/                     # Frontend static assets
│   ├── css/                    # Stylesheets
│   └── js/                     # Client-side JavaScript
├── backend_files/              # Compiled backend assets
│   ├── *.js                    # Built JavaScript files
│   └── *.css                   # Built CSS files
├── config/                     # Configuration files
│   ├── database.env            # Database connection config
│   └── database.env.template   # Database config template
├── data/                       # Data files and datasets
│   ├── augmented_audio/        # Augmented audio data
│   ├── features/               # Extracted audio features
│   ├── high_quality_sounds/    # High-quality reference audio
│   ├── models/                 # Trained model files
│   ├── real_audio_uploads/     # Real user-uploaded audio
│   ├── synthetic_data/         # Generated synthetic data
│   ├── training_data/          # Prepared training datasets
│   ├── analytics.db            # Analytics monitoring database
│   ├── smart_storage.db        # General data storage database
│   └── [10+ other data dirs]   # Various data storage areas
├── database/                   # Database files
│   └── smartcompressor.db      # Main SQLite database
├── docs/                       # Documentation files
│   ├── architecture_design.md  # System architecture docs
│   ├── false_positive_scenarios.md # False positive scenarios
│   ├── iot_sensor_system.md    # IoT sensor implementation
│   └── migration_guide.md      # Migration procedures
├── examples/                   # Example files and usage
│   ├── env_usage_example.py    # Environment variable usage
│   ├── kakao_login_example.py  # Kakao login integration
│   └── [2 more example files]  # Other usage examples
├── hardware/                   # Hardware-related files
│   ├── esp32_firmware/         # ESP32 firmware files
│   └── ESP32_audio_device_spec.md # ESP32 audio device specifications
├── ino/                        # Arduino/ESP32 firmware files
│   ├── alternative_pin_test.ino # Pin testing code
│   ├── board_diagnosis.ino     # Board diagnosis code
│   ├── mic_test_v2.ino         # Microphone testing
│   └── [10+ other .ino files]  # Various ESP32 implementations
├── models/                     # Data and ML models
│   ├── ai_models.py            # AI model definitions
│   ├── database.py             # Database models
│   ├── refrigerator_diagnosis_cnn.py # CNN model for refrigerator diagnosis
│   └── user.py                 # User data model
├── routes/                     # API route definitions
│   ├── ai_routes.py            # AI-related routes
│   ├── admin_routes.py         # Admin routes
│   ├── auth_routes.py          # Authentication routes
│   ├── dashboard_routes.py     # Dashboard routes
│   ├── esp32_routes.py         # ESP32 communication routes
│   └── [10+ other route files] # Other API routes
├── scripts/                    # Utility and deployment scripts
│   ├── deploy_ec2_complete.sh  # EC2 deployment script
│   ├── setup-github-token.sh   # GitHub token setup
│   ├── pm2-setup.sh            # PM2 configuration
│   └── [15+ other scripts]     # Various utility scripts
├── security/                   # Security-related components
│   ├── middleware/             # Security middleware
│   ├── policies/               # Security policies
│   └── services/               # Security services
├── server/                     # Server-side application
│   ├── app.js                  # Main server application
│   ├── config/                 # Server configuration
│   ├── routes/                 # Server routes
│   └── services/               # Server services
├── services/                   # Business logic services
│   ├── ai_service.py           # AI service
│   ├── analytics_service.py    # Analytics service
│   ├── auth_service.py         # Authentication service
│   ├── dashboard_service.py    # Dashboard data service
│   ├── esp32_optimizer.py      # ESP32 optimization service
│   ├── notification_service.py # Notification service
│   ├── sensor_data_service.py  # Sensor data service
│   └── [25+ other services]    # Other business logic services
├── static/                     # Static web assets
│   ├── admin/                  # Admin interface assets
│   ├── dashboard-components/   # Dashboard UI components
│   ├── css/                    # Stylesheets
│   ├── js/                     # JavaScript files
│   ├── images/                 # Image assets
│   └── [5+ other asset dirs]   # Other asset directories
├── templates/                  # Server-side HTML templates
│   ├── admin/                  # Admin page templates
│   └── customer/               # Customer page templates
└── uploads/                    # File upload storage
    └── audio/                  # Audio file uploads
```

## Core Components & Files

### Backend (Python/Flask)
- **`app.py`** - Main Flask application with route registration
- **`models/database.py`** - Database initialization and schema
- **`services/dashboard_service.py`** - Dashboard data service
- **`routes/dashboard_routes.py`** - Dashboard API endpoints
- **`services/ai_service.py`** - AI service with model integration

### Backend (Node.js)
- **`app.js`** - Main Express.js server
- **`services/sqlite_database_service.js`** - SQLite database service
- **`aiRoutes.js`** - AI-related API routes
- **`esp32Routes.js`** - ESP32 communication routes

### AI/Machine Learning
- **`ai/ai_model_trainer.py`** - Core model training
- **`ai/anomaly_detection_ai.py`** - Anomaly detection algorithms
- **`ai/synthetic_data_generator.py`** - Synthetic data generation
- **`ai/integrated_ai_system.py`** - Main AI system integration
- **`train_ai.py`** - AI training script
- **`run_diagnosis.py`** - Real-time diagnosis script

### IoT/ESP32 Firmware
- **`ino/board_diagnosis.ino`** - Board hardware diagnosis
- **`ino/alternative_pin_test.ino`** - Pin configuration testing
- **`ino/ice_cream_sensor_final.ino`** - Primary sensor implementation
- **`esp32Routes.js`** - ESP32 communication API

### Frontend Components
- **`static/dashboard-components/`** - Modular dashboard UI components
- **`templates/customer/dashboard.html`** - Main customer dashboard
- **`admin/templates/admin_dashboard.html`** - Admin dashboard template
- **`routes/dashboard_routes.py`** - Backend API for dashboard data

### Data Processing
- **`data_collector.py`** - Data collection simulator
- **`preprocessor.py`** - Audio preprocessing pipeline
- **`labeling_tool.py`** - Expert labeling interface
- **`services/sensor_data_service.py`** - Sensor data processing

## System Architecture Flow

```
[Real World] → [ESP32 Sensors] → [SignalCraft Server] → [AI Analysis] → [Dashboard]
     ↓              ↓                    ↓                  ↓            ↓
Physical     Audio signals        Data processing    Anomaly detection  Visual
Compressors  → over I2S → Network → & storage → ML models → results → interface
```

### Data Flow Process:
1. **Data Collection**: ESP32 sensors collect audio data from industrial compressors
2. **Data Transmission**: Audio data sent to SignalCraft server via HTTP API
3. **Data Storage**: Raw and processed data stored in database/filesystem
4. **AI Processing**: Anomaly detection models analyze audio patterns
5. **Result Generation**: Classification results with confidence scores
6. **Dashboard Display**: Visual representation of system health and anomalies
7. **Alerting**: Notifications sent based on detection results

### Technology Stack
- **Backend**: Python (Flask), Node.js (Express)
- **Database**: SQLite (primary), with PostgreSQL migration planned
- **AI/ML**: TensorFlow, scikit-learn, librosa for audio processing
- **Frontend**: HTML/CSS/JavaScript with Bootstrap
- **IoT**: ESP32 microcontrollers with I2S audio interface
- **Deployment**: Docker, PM2, Nginx, EC2

## Key Features

1. **Real-time Audio Monitoring**: Continuous analysis of compressor audio signals
2. **Anomaly Detection**: ML-powered identification of unusual patterns
3. **ESP32 Integration**: Edge computing with dedicated sensor hardware
4. **Dashboard Visualization**: Comprehensive monitoring interface
5. **Multi-channel Support**: Audio from multiple compressor units
6. **Expert Knowledge Integration**: Domain knowledge from engineers
7. **Scalable Architecture**: Designed for multiple sites and compressors