# MediLink 🏥
**A Smart Pharmacy Desktop & Cloud Sync Solution**

MediLink is a modern, end-to-end pharmacy management platform designed to automate and streamline pharmacy operations. It combines an offline-first Windows Desktop Client for local pharmacy sales and management with a cloud-synchronized React Web Dashboard for analytics and cross-pharmacy insights.

---

## 🚀 Key Features

### 💻 Pharmacy Desktop Client (Pro)
*   **AI-Powered Invoice Extraction**: Integrated with Gemini AI & local Tesseract OCR to automatically scan and parse medicine invoices.
*   **Local Database Security**: Offline-first design using SQLite databases uniquely encrypted/named based on the pharmacy's license.
*   **Inventory & Sales Management**: Add medicines, update stock, log sales, and automatically generate PDF/text receipts.
*   **Auto-Sync Engine**: Runs in the background to sync local inventory and transaction logs to the cloud.

### 🌐 Cloud Web Dashboard
*   **Real-time Analytics**: Beautiful interactive dashboards showing daily sales, inventory levels, and system health.
*   **Pharmacy Map Directory**: Pinpoint locations of active pharmacies using latitude and longitude coordinates.
*   **Scalable Architecture**: Powered by MongoDB Atlas cloud databases and a FastAPI backend service.

---

## 📁 Repository Structure
```text
├── Backend/                     # FastAPI backend service API & cloud sync handlers
├── MediLink-Desktop-App/        # Windows desktop application (Tkinter, SQLite, OCR)
├── Medilink-project version 3/  # Web Dashboard client (React, Vite, Tailwind CSS)
└── videos/                      # Product demo videos embedded in the README
```

---

## 📽️ Application Demos
Below are the screen recordings demonstrating MediLink in action.

### 🎥 Demo 1: System Overview & Setup
*Demonstrating initial installation, configuration, and app initialization.*
<video src="videos/Vedio 1.webm" width="100%" controls></video>

### 🎥 Demo 2: Core Desktop Application Workflow
*Demonstrating inventory management, invoice OCR text extraction, and receipt generation.*
<video src="videos/Vedio 2.mp4" width="100%" controls></video>

### 🎥 Demo 3: Cloud Synchronization & Web Dashboard
*Demonstrating automated background synchronization to MongoDB Atlas and the React Web Dashboard visualization.*
<video src="videos/Vedio 3.webm" width="100%" controls></video>

*If the video players do not load directly in your browser, you can download them here:*
*   [📥 Download Demo Video 1 (WebM)](videos/Vedio%201.webm)
*   [📥 Download Demo Video 2 (MP4)](videos/Vedio%202.mp4)
*   [📥 Download Demo Video 3 (WebM)](videos/Vedio%203.webm)

---

## 🛠️ Installation & Setup

### Desktop Client Setup
1.  **Install Python**: Download Python 3.10+ and make sure to check **"Add python.exe to PATH"**.
2.  **Run Installer**: Double-click `install.bat` inside the `MediLink-Desktop-App/MediLink-Desktop-App` directory.
3.  **Configure**: Edit `pharmacy_config.json` with your details (name, license, lat/lng, Gemini key).
4.  **Run**: Launch the app using the shortcut created on your desktop or double-click `launch.bat`.

*(For detailed local OCR scanning, install [Tesseract OCR for Windows](https://github.com/UB-Mannheim/tesseract/wiki))*

---

Developed by **Rohail** & **Amish** 🤝