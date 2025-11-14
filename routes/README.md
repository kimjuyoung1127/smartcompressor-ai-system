# Routes Directory

This directory contains all the route definitions for the SignalCraft web application.

## Overview
The routes directory contains modules that define the API endpoints and URL routes for different parts of the SignalCraft application. Each route file corresponds to a specific feature or section of the application.

## Files
- `__init__.py` - Package initialization file
- `__pycache__/` - Python bytecode cache directory
- `admin_routes.py` - Routes for administrative functionality
- `ai_routes.py` - Routes for AI-related functionality
- `analytics_routes.py` - Routes for analytics functionality
- `audio_routes.py` - Routes for audio processing functionality
- `auth_routes.py` - Routes for authentication
- `customer_routes.py` - Routes for customer-related functionality
- `dashboard_routes.py` - Routes for dashboard functionality
- `enhanced_auth_routes.py` - Enhanced authentication routes
- `esp32_routes.py` - Routes for ESP32 IoT device communication
- `iot_sensor_routes.py` - Routes for IoT sensor functionality
- `kakao_auth_routes.py` - Routes for Kakao authentication
- `kakao_notification_routes.py` - Routes for Kakao notifications
- `main_routes.py` - Main application routes
- `mobile_app_routes.py` - Routes for mobile application
- `model_management_routes.py` - Routes for model management
- `monitoring_routes.py` - Routes for system monitoring
- `notification_routes.py` - Routes for notification functionality
- `payment_routes.py` - Routes for payment processing

## API Architecture Flow
```
HTTP Request → Router → Authentication/Authorization → Business Logic → Data Access → Response Generation → HTTP Response
```

## Purpose
This directory organizes the application's URL routing system by feature area, making it easier to maintain and extend. Each route file handles specific types of requests and connects them to the appropriate controller functions.

## Route Organization
- Authentication routes for user login/logout
- AI routes for machine learning functionality
- Audio routes for audio processing and analysis
- IoT routes for ESP32 communication
- Admin routes for management interfaces
- Analytics routes for data analysis features
- Notification routes for messaging functionality

## Request Flow
```
Client Request → Route Handler → Service Layer → Data Layer → Response → Client
```

## API Category Flows

### Authentication Flow
```
Login Request → Auth Routes → Auth Service → Token Generation → Session Management → Response
```

### AI Model Flow
```
Analysis Request → AI Routes → AI Service → Model Inference → Results → Response
```

### IoT Device Flow
```
Sensor Data → ESP32 Routes → Data Processing → Storage → Analytics → Response
```

### Admin Flow
```
Admin Request → Admin Routes → Permission Check → Admin Service → Data Management → Response
```