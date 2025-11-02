# SignalCraft Project - Comprehensive File Organization Plan

After moving the .md files to the `docs` directory and the .ino files to the `ino` directory, here is a comprehensive plan for organizing the remaining files in the root directory.

## Current State of Root Directory

The root directory still contains 60+ files of various types that should be organized into logical folders for better maintainability and readability.

## Proposed Organization

### 1. /config - Configuration Files
- `.env` - Environment variables
- `.dockerignore` - Docker ignore patterns
- `.gitignore` - Git ignore patterns
- `api_keys_template.env` - API keys template
- `ecosystem.config.js` - PM2 process configuration
- `gunicorn.conf.py` - Gunicorn configuration file

### 2. /web - HTML and Web Files
- `audio_research.html` - Audio research page
- `audio_research_features.html` - Audio research features page
- `audio_research_fixed.html` - Fixed audio research page
- `backend.html` - Backend interface page
- `index.html` - Main index page
- `showcase.html` - Showcase page
- `진단리포트_다농마트_20250812_113007.html` - Diagnostic report file

### 3. /scripts - Shell and PowerShell Scripts
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

### 4. /system - System/Service Configuration Files
- `Dockerfile` - Docker configuration
- `docker-compose.yml` - Docker Compose configuration
- `signalcraft-nodejs.service` - Node.js systemd service
- `signalcraft-python.service` - Python systemd service
- `nginx_https_config.conf` - Nginx HTTPS config
- `nginx_proxy_config.conf` - Nginx proxy config
- `nginx_signalcraft_config.conf` - Nginx SignalCraft config
- `nginx_signalcraft_http.conf` - Nginx HTTP config
- `signalcraft_nginx.conf` - Main Nginx config

### 5. /assets - Images and Static Assets
- `dashboard.jpg` - Dashboard image

### 6. /src or /app - Application Entry Points
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
- `simple_labeling_server.js` - Simple labeling server
- `create_admin_sqlite.js` - Admin creation script

### 7. /routes - Route Files
- `aiRoutes.js` - AI routes module
- `esp32Routes.js` - ESP32 routes module
- `esp32Routes_fixed.js` - Fixed ESP32 routes
- `esp32FeaturesApi.js` - ESP32 features API
- `esp32FilesApi.js` - ESP32 files API

### 8. /services - Service Files
- `sqlite_database_service.js` - SQLite database service

### 9. /ai - AI/ML Application Files
- `data_collector.py` - Data collection script
- `labeling_tool.py` - Labeling tool script
- `preprocessor.py` - Preprocessing script
- `run_diagnosis.py` - Run diagnosis script
- `train_ai.py` - Train AI model script

### 10. /tests - Test Files
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

### 11. Keep in Root (Essential Project Files)
- `README.md` - Project documentation
- `package.json` - Node.js dependencies and scripts
- `package-lock.json` - Node.js lock file
- `requirements.txt` - Python dependencies
- `run_server.bat` - Windows server startup script
- `smartcompressor.db` - SQLite database file
- `end` - End script/file
- `mnt/` - Mount directory (already exists)
- `node_modules/` - Node.js modules (already exists)

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