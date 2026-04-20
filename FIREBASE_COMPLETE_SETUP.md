# Firebase Complete Setup Guide - Authentication & Firestore

## 🎯 Overview

This guide covers setting up Firebase for:
- ✅ **Authentication** (user login/signup)
- ✅ **Firestore Database** (store file metadata)
- ❌ **Cloud Storage** (we use Cloudinary instead)

---

## 📋 Prerequisites

Before starting, you need:
- Google account (free)
- Web browser
- Text editor
- Project folder ready

---

## 🚀 Step 1: Create Firebase Project

### 1.1 Go to Firebase Console
1. Visit https://console.firebase.google.com/
2. Click "Create a project"
3. Enter project name: `cloud-storage-app`
4. Click "Continue"

### 1.2 Configure Project Settings
1. Disable "Google Analytics" (for free tier)
2. Click "Create project"
3. Wait for project to be created (1-2 minutes)
4. Click "Continue" when done

### 1.3 You're In!
You should see the Firebase Console dashboard.

---

## 🔐 Step 2: Enable Firebase Authentication

### 2.1 Go to Authentication
1. In left menu, click "Authentication"
2. Click "Get started"
3. You'll see authentication methods

### 2.2 Enable Email/Password
1. Click "Email/Password" option
2. Toggle "Enable" to ON
3. Click "Save"

### 2.3 Verify It's Enabled
You should see "Email/Password" marked as "Enabled"

---

## 📊 Step 3: Create Firestore Database

### 3.1 Go to Firestore
1. In left menu, click "Firestore Database"
2. Click "Create database"

### 3.2 Configure Database
1. Select "Start in test mode"
   - This allows read/write for development
   - Perfect for learning
2. Click "Next"

### 3.3 Choose Location
1. Select location closest to you
   - Example: `us-central1` (USA)
   - Example: `europe-west1` (Europe)
   - Example: `asia-southeast1` (Asia)
2. Click "Enable"

### 3.4 Wait for Creation
Database will be created in 1-2 minutes.

---

## 🔑 Step 4: Get Firebase Credentials

### 4.1 Get Service Account Key
1. Go to "Project Settings" (gear icon, top right)
2. Click "Service Accounts" tab
3. Click "Generate New Private Key"
4. A JSON file will download
5. Save it as `serviceAccountKey.json` in your project root

**⚠️ IMPORTANT:** Never share this file!

### 4.2 Get Web API Key
The Web API Key location has changed in Firebase. Here are the correct steps:

**Method 1: From Firebase Console (Recommended)**
1. Go to "Project Settings" (gear icon, top right)
2. Click "General" tab
3. Scroll down to "Your apps" section
4. If no app is registered, click "Add app" → "Web"
5. Register your app (name it: `cloud-storage-app`)
6. Copy the `apiKey` from the config shown
7. This is your Web API Key

**Method 2: From Google Cloud Console**
1. Go to https://console.cloud.google.com/
2. Select your Firebase project
3. Go to "APIs & Services" → "Credentials"
4. Look for "API keys" section
5. Copy the key labeled "Browser key" or "API key"

**Method 3: Create New API Key**
1. Go to Google Cloud Console
2. Click "Create Credentials" → "API Key"
3. Copy the generated key
4. You'll need this for `.env` file

**Note:** If you don't see the Web API Key, you may need to:
- Register a web app in Firebase Console
- Or create an API key in Google Cloud Console
- Both methods work for this project

### 4.3 Get Project ID
1. In "Project Settings" → "General" tab
2. Look for "Project ID"
3. Copy it (looks like: `cloud-storage-app-12345`)
4. You'll need this for `.env` file

---

## 📝 Step 5: Create .env File

Create a file named `.env` in your project root:

```
# Firebase Configuration
FIREBASE_API_KEY=your_web_api_key_here
FIREBASE_PROJECT_ID=your_project_id_here

# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_cloudinary_api_key
CLOUDINARY_API_SECRET=your_cloudinary_api_secret

# Flask Configuration
SECRET_KEY=your_secret_key_here
```

**Replace with your actual values!**

### Where to Find Each Value:

**FIREBASE_API_KEY:**
- Go to Project Settings → General
- Look for "Web API Key"
- Copy the entire key

**FIREBASE_PROJECT_ID:**
- Go to Project Settings → General
- Look for "Project ID"
- Copy it

**CLOUDINARY_* values:**
- Go to Cloudinary Dashboard
- Look for "API Environment variable"
- Copy Cloud Name, API Key, API Secret

**SECRET_KEY:**
- Generate a random string
- Example: `your-secret-key-12345-abcde`

---

## 🔒 Step 6: Secure Your Credentials

### 6.1 Add to .gitignore
Create/update `.gitignore` file:

```
# Environment variables
.env
.env.local
.env.*.local

# Firebase credentials
serviceAccountKey.json

# Python
__pycache__/
*.pyc
*.pyo
*.egg-info/
dist/
build/

# Virtual environment
venv/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo
```

### 6.2 Never Commit Secrets
```bash
# Check what will be committed
git status

# Make sure .env and serviceAccountKey.json are NOT listed
```

---

## 📦 Step 7: Install Dependencies

### 7.1 Update requirements.txt
Make sure your `requirements.txt` has:

```
Flask==2.3.3
Flask-CORS==4.0.0
firebase-admin==6.2.0
cloudinary==1.33.0
requests==2.31.0
Werkzeug==2.3.7
python-dotenv==1.0.0
gunicorn==21.2.0
```

### 7.2 Install Packages
```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## ✅ Step 8: Verify Firebase Setup

### 8.1 Create Test Script
Create `test_firebase.py`:

```python
import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, auth, firestore

# Load environment variables
load_dotenv()

# Initialize Firebase
try:
    cred = credentials.Certificate('serviceAccountKey.json')
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("✓ Firebase initialized successfully!")
    
    # Test Firestore
    test_doc = {
        'test': 'data',
        'timestamp': firestore.SERVER_TIMESTAMP
    }
    db.collection('test').document('test_doc').set(test_doc)
    print("✓ Firestore is working!")
    
    # Clean up
    db.collection('test').document('test_doc').delete()
    print("✓ All tests passed!")
    
except Exception as e:
    print(f"✗ Error: {e}")
```

### 8.2 Run Test
```bash
python test_firebase.py
```

You should see:
```
✓ Firebase initialized successfully!
✓ Firestore is working!
✓ All tests passed!
```

---

## 🔐 Step 9: Configure Firestore Security Rules

### 9.1 Go to Firestore Rules
1. Go to Firestore Database
2. Click "Rules" tab
3. You'll see the current rules

### 9.2 Update Rules for Development
Replace with:

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Allow authenticated users to read/write their own data
    match /users/{uid} {
      allow read, write: if request.auth.uid == uid;
    }
    
    // Allow authenticated users to read/write their own files
    match /files/{document=**} {
      allow read, write: if request.auth.uid == resource.data.user_id;
      allow create: if request.auth.uid == request.resource.data.user_id;
    }
    
    // Test collection (for development only)
    match /test/{document=**} {
      allow read, write: if true;
    }
  }
}
```

### 9.3 Publish Rules
1. Click "Publish"
2. Confirm the changes

---

## 📊 Step 10: Verify Firestore Collections

### 10.1 Check Collections
1. Go to Firestore Database
2. Click "Data" tab
3. You should see:
   - `test` collection (from test script)
   - `users` collection (will be created when users sign up)
   - `files` collection (will be created when files are uploaded)

### 10.2 Delete Test Collection
1. Click on `test` collection
2. Click the three dots menu
3. Click "Delete collection"
4. Confirm deletion

---

## 🚀 Step 11: Run Your Project

### 11.1 Start Flask Server
```bash
# Make sure virtual environment is activated
python app.py
```

You should see:
```
✓ Firebase initialized successfully
✓ Cloudinary configured successfully
 * Running on http://localhost:5000
```

### 11.2 Test in Browser
1. Open http://localhost:5000
2. You should see login page

---

## 🧪 Step 12: Test All Features

### 12.1 Test Signup
1. Click "Sign up here"
2. Enter email: `test@example.com`
3. Enter password: `Test123456`
4. Click "Create Account"
5. You should see success message

### 12.2 Test Login
1. Go back to login page
2. Enter email: `test@example.com`
3. Enter password: `Test123456`
4. Click "Login"
5. You should see dashboard

### 12.3 Check Firestore
1. Go to Firebase Console
2. Go to Firestore Database
3. Click "Data" tab
4. You should see:
   - `users` collection with your test user
   - User document with email and created_at

### 12.4 Test File Upload
1. In dashboard, upload a file
2. File should appear in list
3. Go to Firestore
4. You should see `files` collection with your file metadata

### 12.5 Test Download
1. Click "Download" button
2. File should download

### 12.6 Test Delete
1. Click "Delete" button
2. Confirm deletion
3. File should disappear from list
4. Check Firestore - file metadata should be deleted

---

## 📊 Firestore Database Structure

### Users Collection
```
users/
├── user_id_1/
│   ├── email: "user@example.com"
│   ├── created_at: Timestamp
│   └── storage_used: 0
└── user_id_2/
    └── ...
```

### Files Collection
```
files/
├── file_id_1/
│   ├── user_id: "user_id_1"
│   ├── filename: "document.pdf"
│   ├── cloudinary_public_id: "user_id_1/uuid_document.pdf"
│   ├── size: 2048
│   ├── uploaded_at: Timestamp
│   ├── download_url: "https://res.cloudinary.com/..."
│   ├── share_token: "abc123xyz"
│   └── file_type: "raw"
└── file_id_2/
    └── ...
```

---

## 🔍 Monitoring Firestore

### Check Usage
1. Go to Firestore Database
2. Click "Usage" tab
3. See your current usage:
   - Reads
   - Writes
   - Deletes
   - Storage

### Example Usage
```
Reads:    234 / 50,000 (0.5%)
Writes:   123 / 20,000 (0.6%)
Deletes:  45 / 20,000 (0.2%)
Storage:  234 KB / 1 GB (0.02%)
```

---

## ❓ FAQ

**Q: Do I need Firebase Storage?**
A: No, we use Cloudinary instead (25GB free vs 1GB).

**Q: Can I use Firestore without Authentication?**
A: Yes, but not recommended. Authentication secures your data.

**Q: What's the free tier limit?**
A: 1GB storage, 50K reads/day, 20K writes/day.

**Q: Will I be charged?**
A: No, free tier has no automatic charges.

**Q: How do I upgrade?**
A: Go to Firestore → Upgrade to paid plan.

**Q: Can I delete my project?**
A: Yes, go to Project Settings → Delete Project.

**Q: How do I backup my data?**
A: Use Firestore export feature in Console.

---

## 🆘 Troubleshooting

### Issue: "Firebase initialization error"

**Solution:**
- Check if `serviceAccountKey.json` exists
- Verify file is in project root
- Make sure file is valid JSON
- Check file permissions

### Issue: "Invalid API Key"

**Solution:**
- Go to Project Settings → General
- Copy correct Web API Key
- Update `.env` file
- Restart Flask server

### Issue: "Permission denied" in Firestore

**Solution:**
- Check Firestore security rules
- Make sure rules allow authenticated access
- Use test mode rules for development
- Verify user is authenticated

### Issue: "Collection not found"

**Solution:**
- Collections are created automatically
- Just upload a file and collection will be created
- Or manually create collection in Console

### Issue: "User already exists"

**Solution:**
- Use different email
- Or delete user from Firebase Console
- Go to Authentication → Users → Delete user

---

## 📚 Complete Setup Checklist

### Firebase Setup
- [ ] Created Firebase project
- [ ] Enabled Authentication (Email/Password)
- [ ] Created Firestore Database (test mode)
- [ ] Downloaded serviceAccountKey.json
- [ ] Got Web API Key
- [ ] Got Project ID

### Local Setup
- [ ] Created .env file with all credentials
- [ ] Added .env to .gitignore
- [ ] Created virtual environment
- [ ] Installed dependencies
- [ ] Tested Firebase connection

### Security
- [ ] serviceAccountKey.json in .gitignore
- [ ] .env file in .gitignore
- [ ] Never committed secrets
- [ ] Set Firestore security rules

### Testing
- [ ] Tested signup
- [ ] Tested login
- [ ] Tested file upload
- [ ] Tested file download
- [ ] Tested file delete
- [ ] Checked Firestore data

---

## 🎯 Next Steps

### Immediate
1. Follow this guide step-by-step
2. Create Firebase project
3. Enable Authentication
4. Create Firestore Database
5. Get credentials

### Short Term
1. Create .env file
2. Install dependencies
3. Test Firebase connection
4. Run Flask server
5. Test all features

### Medium Term
1. Deploy to production
2. Monitor Firestore usage
3. Add more features
4. Prepare for interviews

---

## 📞 Support

### Firebase Documentation
- https://firebase.google.com/docs
- https://firebase.google.com/docs/auth
- https://firebase.google.com/docs/firestore

### Common Issues
- See ERRORS_AND_SOLUTIONS.md
- Check Firebase Console logs
- Check Flask server logs

---

## 🎉 You're Ready!

You now have:
- ✅ Firebase Authentication (unlimited users)
- ✅ Firestore Database (1GB free)
- ✅ Cloudinary Storage (25GB free)
- ✅ Complete setup
- ✅ All features working

**Start building!** 🚀

---

**Happy coding with Firebase + Cloudinary!** 💻✨
