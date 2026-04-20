# Deployment Guide - Deploy for Free

## Overview

This guide shows how to deploy your Cloud Storage project to production for free using Render.

---

## Option 1: Deploy on Render (Recommended)

Render is a modern cloud platform that offers free tier hosting.

### Step 1: Prepare Your Project

#### 1.1 Create `.gitignore` file

```bash
# Create .gitignore in project root
echo "venv/" > .gitignore
echo "serviceAccountKey.json" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo ".env" >> .gitignore
```

#### 1.2 Create `Procfile`

```bash
# Create Procfile (no extension)
echo "web: gunicorn app:app" > Procfile
```

#### 1.3 Update `requirements.txt`

```bash
# Add gunicorn for production
pip install gunicorn
pip freeze > requirements.txt
```

Your `requirements.txt` should include:
```
Flask==2.3.3
Flask-CORS==4.0.0
firebase-admin==6.2.0
requests==2.31.0
Werkzeug==2.3.7
python-dotenv==1.0.0
gunicorn==21.2.0
```

#### 1.4 Create `.env` file

```bash
# Create .env file (for environment variables)
echo "FLASK_ENV=production" > .env
echo "SECRET_KEY=your-secret-key-here" >> .env
```

**Important:** Add `.env` to `.gitignore` so it's not committed.

### Step 2: Push to GitHub

#### 2.1 Create GitHub Repository

1. Go to https://github.com/new
2. Create repository: `cloud-storage-app`
3. Don't initialize with README (we have one)

#### 2.2 Push Code to GitHub

```bash
# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Cloud Storage App"

# Add remote
git remote add origin https://github.com/YOUR_USERNAME/cloud-storage-app.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 3: Deploy on Render

#### 3.1 Create Render Account

1. Go to https://render.com
2. Click "Sign up"
3. Sign up with GitHub (easier)

#### 3.2 Create New Web Service

1. Click "New +" button
2. Select "Web Service"
3. Connect your GitHub repository
4. Select `cloud-storage-app` repository

#### 3.3 Configure Service

Fill in the following:

| Field | Value |
|-------|-------|
| Name | `cloud-storage-app` |
| Environment | `Python 3` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn app:app` |
| Plan | `Free` |

#### 3.4 Add Environment Variables

Click "Advanced" and add:

```
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
FIREBASE_API_KEY=your-api-key
```

#### 3.5 Deploy

1. Click "Create Web Service"
2. Wait for deployment (2-3 minutes)
3. You'll get a URL like: `https://cloud-storage-app.onrender.com`

### Step 4: Add Firebase Credentials

Since we can't upload `serviceAccountKey.json` to GitHub:

#### 4.1 Update `app.py`

```python
import os
import json

# Load Firebase credentials from environment variable
firebase_creds = os.environ.get('FIREBASE_CREDENTIALS')

if firebase_creds:
    # Production: Load from environment variable
    cred_dict = json.loads(firebase_creds)
    cred = credentials.Certificate(cred_dict)
else:
    # Development: Load from file
    cred = credentials.Certificate('serviceAccountKey.json')

firebase_admin.initialize_app(cred, {
    'storageBucket': os.environ.get('FIREBASE_STORAGE_BUCKET')
})
```

#### 4.2 Add to Render Environment Variables

1. Go to Render Dashboard
2. Select your service
3. Go to "Environment"
4. Add new variable:

**Name:** `FIREBASE_CREDENTIALS`

**Value:** Copy entire content of `serviceAccountKey.json` and paste as JSON string

Or use this Python script to convert:

```python
import json

with open('serviceAccountKey.json', 'r') as f:
    cred = json.load(f)

print(json.dumps(cred))
```

Copy the output and paste in Render.

#### 4.3 Add Storage Bucket

Add another environment variable:

**Name:** `FIREBASE_STORAGE_BUCKET`

**Value:** `your-project-id.appspot.com`

### Step 5: Test Deployment

1. Go to your Render URL
2. Try to sign up
3. Try to upload a file
4. Check if everything works

---

## Option 2: Deploy on Firebase Hosting

Firebase Hosting is free and integrates well with Firebase.

### Step 1: Install Firebase CLI

```bash
# Install Node.js first from https://nodejs.org/
# Then install Firebase CLI
npm install -g firebase-tools
```

### Step 2: Initialize Firebase

```bash
# Login to Firebase
firebase login

# Initialize Firebase in your project
firebase init hosting
```

### Step 3: Build for Production

```bash
# Create production build
mkdir public

# Copy static files
cp -r static/* public/
cp templates/* public/

# Copy app.py to functions
mkdir functions
cp app.py functions/
cp requirements.txt functions/
```

### Step 4: Deploy

```bash
firebase deploy
```

---

## Option 3: Deploy on Heroku (Free Tier Ending)

**Note:** Heroku free tier ended in November 2022. Use Render instead.

---

## Post-Deployment Checklist

- [ ] Application loads without errors
- [ ] Can create account
- [ ] Can login
- [ ] Can upload file
- [ ] Can download file
- [ ] Can delete file
- [ ] Can share file
- [ ] No console errors
- [ ] No server errors
- [ ] Database working
- [ ] Storage working

---

## Monitoring & Maintenance

### View Logs

**On Render:**
```bash
# View logs in Render Dashboard
# Go to Service > Logs
```

### Update Code

```bash
# Make changes locally
git add .
git commit -m "Fix: description"
git push origin main

# Render automatically redeploys
```

### Monitor Performance

1. Go to Render Dashboard
2. Check "Metrics" tab
3. Monitor CPU, Memory, Requests

---

## Troubleshooting Deployment

### Issue: "Build failed"

**Solution:**
1. Check build logs in Render
2. Make sure `requirements.txt` is correct
3. Make sure `Procfile` exists
4. Check for syntax errors in code

### Issue: "Application error"

**Solution:**
1. Check logs in Render
2. Make sure environment variables are set
3. Make sure Firebase credentials are correct
4. Check database connection

### Issue: "Firebase credentials not found"

**Solution:**
1. Make sure `FIREBASE_CREDENTIALS` environment variable is set
2. Make sure it's valid JSON
3. Make sure `FIREBASE_STORAGE_BUCKET` is set

### Issue: "Port already in use"

**Solution:**
```python
# In app.py, use environment variable for port
port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port)
```

---

## Security Checklist

- [ ] Never commit `serviceAccountKey.json`
- [ ] Use environment variables for secrets
- [ ] Enable HTTPS (automatic on Render)
- [ ] Update Firestore rules for production
- [ ] Update Storage rules for production
- [ ] Set strong `SECRET_KEY`
- [ ] Disable debug mode in production
- [ ] Monitor for suspicious activity

---

## Production Firestore Rules

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{uid} {
      allow read, write: if request.auth.uid == uid;
    }
    
    match /files/{document=**} {
      allow read, write: if request.auth.uid == resource.data.user_id;
      allow create: if request.auth.uid == request.resource.data.user_id;
    }
  }
}
```

---

## Production Storage Rules

```
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    match /{userId}/{allPaths=**} {
      allow read, write: if request.auth.uid == userId;
    }
  }
}
```

---

## Cost Estimation

### Render (Free Tier)
- **Compute**: Free (limited to 750 hours/month)
- **Bandwidth**: Free (limited)
- **Database**: Not included (use Firebase)

### Firebase (Free Tier)
- **Authentication**: Free (up to 50,000 users)
- **Firestore**: Free (1GB storage, 50,000 reads/day)
- **Storage**: Free (1GB storage)

**Total Cost**: $0/month for small projects

---

## Next Steps

1. Monitor your deployment
2. Collect user feedback
3. Add more features
4. Scale as needed
5. Consider paid plans if needed

---

## Useful Links

- Render Documentation: https://render.com/docs
- Firebase Hosting: https://firebase.google.com/docs/hosting
- Flask Deployment: https://flask.palletsprojects.com/deployment/
- Gunicorn: https://gunicorn.org/
