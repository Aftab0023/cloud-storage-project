# Cloud-Based File Storage System (Like Google Drive)

A complete beginner-friendly project using Flask and Firebase (free tier).

## Project Overview

This project teaches you how to build a cloud storage system where users can:
- Sign up and log in
- Upload files to cloud storage
- Download files
- Delete files
- Generate shareable links
- View file metadata

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (HTML/CSS/JS)               │
│              (Runs in user's browser)                   │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP Requests
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Backend (Flask Server)                      │
│         (Runs on your computer/server)                  │
│  - Handles login/signup                                 │
│  - Manages file uploads/downloads                       │
│  - Stores metadata                                      │
└────────────────────┬────────────────────────────────────┘
                     │ API Calls
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  Firebase (Cloud)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Auth Service │  │ Storage      │  │ Firestore DB │  │
│  │ (Login/Signup)  │ (File Storage)  │ (Metadata)   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Folder Structure

```
cloud-storage-project/
│
├── app.py                    # Main Flask application
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── serviceAccountKey.json    # Firebase credentials (DON'T SHARE!)
│
├── templates/                # HTML files
│   ├── base.html            # Base template
│   ├── login.html           # Login page
│   ├── signup.html          # Signup page
│   ├── dashboard.html       # Main file storage page
│   └── error.html           # Error page
│
├── static/                   # CSS and JavaScript
│   ├── css/
│   │   └── style.css        # Styling
│   └── js/
│       └── script.js        # Frontend logic
│
└── README.md                # This file
```

## Key Concepts Explained

### 1. Flask
- A lightweight Python web framework
- Handles HTTP requests from frontend
- Communicates with Firebase

### 2. Firebase Authentication
- Manages user login/signup securely
- Stores passwords encrypted
- Provides user ID for each user

### 3. Firebase Storage
- Cloud storage for files
- Like Google Drive's storage
- Free tier: 1GB storage

### 4. Firestore Database
- NoSQL database (stores data as documents)
- Stores file metadata (name, size, URL, owner)
- Free tier: 1GB storage

## Step-by-Step Setup

See individual files for complete setup instructions.

## Common Errors & Solutions

See ERRORS.md for troubleshooting.

## Viva Questions

See VIVA_QUESTIONS.md for interview preparation.

## Deployment

See DEPLOYMENT.md for free hosting options.
