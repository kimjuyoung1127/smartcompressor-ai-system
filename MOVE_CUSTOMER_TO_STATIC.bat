@echo off
REM Move customer folder to static/customer
echo ========================================
echo Moving customer to static/customer
echo ========================================
echo.

cd C:\Users\gmdqn\signalcraft

echo Checking if customer folder exists...
if not exist "customer" (
    echo Error: customer folder not found!
    pause
    exit /b 1
)

echo Checking if static folder exists...
if not exist "static" (
    echo Error: static folder not found!
    pause
    exit /b 1
)

echo Moving customer folder...
move customer static\customer

if exist "static\customer" (
    echo.
    echo ========================================
    echo SUCCESS! Folder moved successfully
    echo ========================================
    echo.
    echo Location: C:\Users\gmdqn\signalcraft\static\customer
    echo.
    echo Next steps:
    echo 1. Update server/routes/customer/index.js
    echo 2. Update server/app.js
    echo 3. Restart server
    echo.
) else (
    echo.
    echo Error: Failed to move folder
    echo.
)

pause
