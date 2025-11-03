# SignalCraft Root Directory Reorganization Plan

## Current State
The root directory contains 100+ files of various types that should be organized into logical folders for better maintainability and readability.

## Proposed Organization

### 1. /config - Configuration Files
- `.env` - Environment variables
- `.dockerignore` - Docker ignore patterns
- `.gitignore` - Git ignore patterns
- `api_keys_template.env` - API keys template
- `database.env` and `database.env.template` (from config directory if applicable)

### 2. /docs - Documentation Files
- `API_KEYS_MANAGEMENT_GUIDE.md` - Guide for API key management
- `API_REFERENCE.md` - API reference documentation
- `EC2_DEPLOYMENT_GUIDE.md` - EC2 deployment guide
- `GITHUB_TOKEN_GUIDE.md` - GitHub token setup guide
- `HTTPS_SETUP_GUIDE.md` - HTTPS setup guide
- `INSTALLATION_GUIDE.md` - Installation guide
- `KAKAO_NOTIFICATION_SETUP.md` - Kakao notification setup
- `TROUBLESHOOTING_GUIDE.md` - Troubleshooting guide
- `anomalies.md` - Anomaly detection documentation
- `async_implementation_plan.md` - Async implementation plan
- `beoverview.md` - Backend overview
- `beprogress.md` - Backend progress tracking
- `cicd_improvement_plan.md` - CI/CD improvement plan
- `cicd_validation_report.md` - CI/CD validation report
- `dashboard-architecture.md` - Dashboard architecture
- `dashboard.md` - Dashboard documentation
- `field_data_collection_plan.md` - Field data collection plan
- `github_token_setup.md` - GitHub token setup guide
- `gunicorn_adoption_plan.md` - Gunicorn adoption plan
- `load_test_plan.md` - Load test plan
- `manual_deploy_guide.md` - Manual deployment guide
- `overview.md` - System overview
- `plan.md` - Project plan
- `progress.md` - Project progress
- `progress2.md` - Project progress (continued)
- `progress3.md` - Project progress (continued)
- `sentry_integration_plan.md` - Sentry integration plan
- `signalcraft_roadmap.md` - Project roadmap
- `suggestion.md` - Suggestions document

### 3. /src or /app - Application Entry Points
- `app.js` - Main Node.js application entry point
- `app.py` - Main Python/Flask application entry point
- `server.js` - Server implementation
- `server_app.js` - Server application module
- `server_app_fixed.js` - Fixed server application
- `production-server.js` - Production server setup
- `simple_server.js` - Simple server implementation
- `simple_server.py` - Simple Python server
- `integrated_server.js` - Integrated server
- `data_upload_server.js` - Data upload server
- `data_upload_server_fixed.js` - Fixed data upload server
- `https-server.js` - HTTPS server implementation
- `https-server-simple.js` - Simple HTTPS server
- `simple_dashboard_server.js` - Simple dashboard server
- `aiRoutes.js` - AI routes module
- `esp32Routes.js` - ESP32 routes module
- `esp32Routes_fixed.js` - Fixed ESP32 routes
- `esp32FeaturesApi.js` - ESP32 features API
- `esp32FilesApi.js` - ESP32 files API
- `create_admin_sqlite.js` - Admin creation script

### 4. /hardware - ESP32/Arduino Files
- `alternative_pin_test.ino` - ESP32 pin testing
- `board_diagnosis.ino` - Board diagnosis code
- `board_diagnosis_fixed.ino` - Fixed board diagnosis code
- `detailed_mic_test.ino` - Detailed microphone test
- `final_hardware_test.ino` - Final hardware test
- `ice_cream_sensor_final.ino` - Ice cream sensor implementation
- `ice_cream_sensor_final_fixed.ino` - Fixed ice cream sensor
- `ice_cream_sensor_final_install.ino` - Ice cream sensor installation
- `ice_cream_sensor_fixed.ino` - Fixed ice cream sensor code
- `ice_cream_sensor_no_json.ino` - Ice cream sensor without JSON
- `ice_cream_store_sensor.ino` - Ice cream store sensor
- `optimized_ice_cream_sensor.ino` - Optimized ice cream sensor
- `simple_mic_test.ino` - Simple microphone test
- `mic_test_v2.ino` - Microphone test v2

### 5. /tests - Test Files
- `test_admin_system.py` - Admin system tests
- `test_ai_model.py` - AI model tests
- `test_analytics_system.py` - Analytics system tests
- `test_auto_pipeline.py` - Auto pipeline tests
- `test_complete_system.js` - Complete system tests
- `test_dashboard_system.py` - Dashboard system tests
- `test_iot_system.py` - IoT system tests
- `test_lightweight_3tier_system.js` - Lightweight 3-tier tests
- `test_mobile_app.py` - Mobile app tests
- `test_mobile_app_system.py` - Mobile app system tests
- `test_notification_system.py` - Notification system tests
- `test_phase1_api.js` - Phase 1 API tests
- `test_safe_gpu_system.py` - Safe GPU system tests
- `test_sensor.js` - Sensor tests

### 6. /web - HTML and Web Files
- `audio_research.html` - Audio research page
- `audio_research_features.html` - Audio research features page
- `audio_research_fixed.html` - Fixed audio research page
- `backend.html` - Backend interface
- `index.html` - Main index page
- `showcase.html` - Showcase page
- `sw.md` - Service worker documentation

### 7. /scripts - Shell and PowerShell Scripts
- `check_deployment.sh` - Deployment check script
- `check_server_status.sh` - Server status check
- `deploy_ec2_complete.sh` - Complete EC2 deployment
- `generate_ssh_key.sh` - SSH key generation
- `setup_github_token.sh` - GitHub token setup
- `setup_https.sh` - HTTPS setup
- `setup_ssl.sh` - SSL setup
- `setup-auto-deploy.sh` - Auto deployment setup
- `deploy_to_ec2.ps1` - PowerShell EC2 deployment
- `push_to_github.ps1` - PowerShell GitHub push
- `setup_github_token.ps1` - PowerShell GitHub token setup
- `setup_kakao_login.ps1` - PowerShell Kakao login setup

### 8. /system - System/Service Configuration Files
- `Dockerfile` - Docker configuration
- `docker-compose.yml` - Docker Compose configuration
- `ecosystem.config.js` - PM2 ecosystem configuration
- `gunicorn.conf.py` - Gunicorn configuration
- `signalcraft-nodejs.service` - Node.js systemd service
- `signalcraft-python.service` - Python systemd service
- `nginx_https_config.conf` - Nginx HTTPS config
- `nginx_proxy_config.conf` - Nginx proxy config
- `nginx_signalcraft_config.conf` - Nginx SignalCraft config
- `nginx_signalcraft_http.conf` - Nginx HTTP config
- `signalcraft_nginx.conf` - Main Nginx config

### 9. /assets - Images and Static Assets
- `dashboard.jpg` - Dashboard image
- `error.png` - Error image
- `setting.png` - Setting image

## Migration Steps

### 1. Preparation
1. Create all target directories
2. Create this documentation file for reference
3. Test that all paths in the application correctly handle the new structure

### 2. Check for Dependencies
1. Update `package.json` if any scripts reference root files directly
2. Update `requirements.txt` references if needed
3. Update any import/require statements in code that reference root files
4. Update configuration files that reference root paths

### 3. Move Files
1. Move each file to its appropriate directory
2. Update import paths in source code to reflect new locations
3. Update build processes to look in new locations

### 4. Verification
1. Test that the application starts correctly
2. Test all functionality still works
3. Verify all automated tests pass
4. Verify deployment scripts still work

## Important Notes

⚠️ **CRITICAL**: Before making any changes, backup your project or work on a branch.

⚠️ **Dependencies**: Check the following files for hardcoded paths:
- `package.json` scripts section
- `app.js` and `app.py` require/import statements
- All `.js`, `.py` files that may reference files in the root
- Configuration files that specify file paths

⚠️ **Configuration**: Update environment variables or configuration that references root-level files, such as:
- Path to SQLite database file (`smartcompressor.db`)
- Path to static assets
- Path to logs or temporary files

⚠️ **Deployment**: Update deployment scripts to reflect the new directory structure.

## Safety Guidelines

1. **Always test** in a development environment before applying to production
2. **Use version control** - commit before making changes, so you can rollback
3. **Update import paths** in all modules after moving files
4. **Run tests** to ensure functionality is preserved
5. **Update documentation** to reflect new paths

This reorganization will make the project significantly more maintainable by grouping related files together and creating a logical structure that's easier to navigate.