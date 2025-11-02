# Root Directory Reorganization - Path Reference Guide

## Overview
This document details which files in the SignalCraft project reference specific root directory files and what changes would be needed to maintain functionality after reorganization.

## Files that Reference Root-Level Files

### 1. Configuration Files to Update

#### package.json
- Scripts may reference root-level JS files
- Current references: `server.js`, `production-server.js`, etc.

#### app.js and app.py
- May need path updates for imports/requires
- Check references to routes, services, and static files

### 2. Application Files with Path Dependencies

#### app.py
- Contains references to routes and services that may need path adjustments
- References to `static` and `templates` directories
- Database file references

#### app.js
- Contains middleware and route configurations
- References to static files and template locations
- Session and cookie configurations

### 3. Environment and Configuration Files

#### .env
- May contain paths to database, logs, or other files
- Verify if any paths reference root-level items

#### server configuration files
- Files like `gunicorn.conf.py`, nginx configs
- Deployment configuration files

### 4. Database Reference

#### smartcompressor.db
- The SQLite database file that may be referenced in code
- Ensure all database connection strings are updated

### 5. Static Asset References

- Multiple files may reference `static/`, `uploads/`, or root-level assets
- HTML templates may have hardcoded asset paths

### 6. Test Files with Root Dependencies

#### All test files
- Verify that test files still work after reorganization
- Update imports if necessary

## Critical Files to Examine Before Moving

1. `package.json` - Check all scripts and dependencies
2. `app.js` - Node.js application entry point
3. `app.py` - Python application entry point
4. `server.js` - Main server file
5. `requirements.txt` - Python dependencies
6. All route files in routes/ directory
7. All service files in services/ directory
8. Deployment configuration files
9. All HTML templates in templates/ directory

## Risk Assessment

### High Risk
- Moving database files (smartcompressor.db) - requires DB connection string updates
- Moving application entry points (app.js, app.py, server.js) - requires config updates
- Moving configuration files - affects environment setup

### Medium Risk
- Moving HTML files - may have relative path dependencies
- Moving static assets - may affect image paths, etc.

### Low Risk
- Moving documentation files (.md)
- Moving test files
- Moving hardware files (.ino)
- Moving shell scripts (.sh, .ps1)

## Recommended Approach

1. Start with low-risk files (docs, tests, hardware)
2. Update code references as you move files
3. Test functionality after each group of moves
4. Finally move high-risk files and configurations
5. Perform full system test

## Rollback Plan

To reverse changes if something breaks:
1. Git checkout to previous commit
2. Or run the reverse of the move commands
3. Restore original file locations