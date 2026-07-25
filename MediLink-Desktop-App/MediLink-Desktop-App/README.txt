======================================================================
                  MEDILINK - PHARMACY DESKTOP APP (PRO)
                       SETUP & INSTALLATION GUIDE
======================================================================

Welcome to the MediLink Pharmacy Desktop Application! This guide will walk you through
setting up the application on a Windows computer.

----------------------------------------------------------------------
STEP 1: INSTALL PYTHON
----------------------------------------------------------------------
1. Download Python (version 3.10 or newer) from the official website:
   https://www.python.org/downloads/windows/
2. Run the Python installer.
3. IMPORTANT: Make sure to check the box that says:
   "Add python.exe to PATH" (at the bottom of the installer window).
4. Complete the installation.

----------------------------------------------------------------------
STEP 2: RUN THE ONE-CLICK INSTALLER
----------------------------------------------------------------------
1. Open this folder ("MediLink-Desktop-App").
2. Double-click the file named: "install.bat"
3. This script will automatically:
   - Install all required Python packages (Pillow, pymongo, etc.)
   - Create a beautiful "MediLink" shortcut on your Desktop with the branding icon!
4. Once completed, press any key to close the window.

----------------------------------------------------------------------
STEP 3: CONFIGURATION
----------------------------------------------------------------------
Before launching the app, configure your pharmacy details:
1. Open the file "pharmacy_config.json" in a text editor (e.g. Notepad).
2. Set the following fields inside the quotes:
   - "name": The name of your pharmacy.
   - "license": Your license code (used to encrypt/obscure your local database name).
   - "lat": Latitude coordinates (e.g. "33.6844").
   - "lng": Longitude coordinates (e.g. "73.0479").
   - "gemini_key": Your Gemini API Key (if you wish to use AI OCR for invoice extraction).
3. Save the file.

----------------------------------------------------------------------
STEP 4: RUNNING THE APPLICATION
----------------------------------------------------------------------
1. You can now launch the application directly using the "MediLink" shortcut
   on your Windows Desktop!
2. Alternatively, you can double-click "launch.bat" inside this folder.

----------------------------------------------------------------------
(OPTIONAL) STEP 5: TESSERACT OCR FOR IMAGE SCANNING
----------------------------------------------------------------------
If you want to use the local text extraction tool (OCR) for scanned invoices:
1. Download and install Tesseract OCR for Windows:
   https://github.com/UB-Mannheim/tesseract/wiki
2. The app will auto-detect the default installation path:
   C:\Program Files\Tesseract-OCR\tesseract.exe
----------------------------------------------------------------------
