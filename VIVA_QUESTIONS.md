# Viva Questions and Answers

## 1. Architecture & Design

### Q1: Explain the overall architecture of your project.

**Answer:**
The project follows a three-tier architecture:

1. **Frontend Layer (HTML/CSS/JavaScript)**
   - User interface for login, signup, and file management
   - Handles user interactions and displays data
   - Communicates with backend via HTTP requests

2. **Backend Layer (Flask)**
   - Processes HTTP requests from frontend
   - Handles authentication and authorization
   - Manages file operations (upload, download, delete)
   - Communicates with Firebase services

3. **Cloud Layer (Firebase)**
   - **Authentication**: Manages user login/signup securely
   - **Storage**: Stores actual files in cloud
   - **Firestore**: Stores file metadata and user information

**Data Flow:**
```
User → Frontend → Flask Backend → Firebase Services → Cloud Storage
```

---

### Q2: Why did you choose Flask over Django?

**Answer:**
- **Lightweight**: Flask is minimal and easy to learn (perfect for beginners)
- **Flexibility**: Can add only what we need
- **Fast Development**: Less boilerplate code
- **Perfect for APIs**: Easy to create REST endpoints
- **Firebase Integration**: Works seamlessly with Firebase

Django is better for large projects with built-in features, but Flask is ideal for this project.

---

### Q3: What is the difference between Firestore and Firebase Storage?

**Answer:**

| Feature | Firestore | Firebase Storage |
|---------|-----------|-----------------|
| **Type** | NoSQL Database | File Storage |
| **Purpose** | Store structured data | Store files (images, videos, etc.) |
| **Data Format** | Documents & Collections | Binary files |
| **Use Case** | Metadata, user info | Actual files |
| **Query** | Can query data | Cannot query files |
| **Example** | File name, size, owner | Actual file content |

In our project:
- **Firestore**: Stores file metadata (name, size, owner, upload date)
- **Storage**: Stores actual file content

---

### Q4: Explain the authentication flow in your project.

**Answer:**
1. User enters email and password on signup page
2. Flask sends request to Firebase Authentication
3. Firebase creates user account and stores password securely (hashed)
4. User logs in with email and password
5. Flask verifies credentials using Firebase REST API
6. If valid, user ID is stored in session
7. Session ID is stored in browser cookie
8. For each request, Flask checks if user is logged in
9. If not logged in, user is redirected to login page

**Security:**
- Passwords are hashed by Firebase (not stored in plain text)
- Session cookies are HTTP-only (cannot be accessed by JavaScript)
- HTTPS should be used in production

---

## 2. Technical Implementation

### Q5: How do you handle file uploads?

**Answer:**
1. **Frontend**: User selects file via drag-drop or file input
2. **Validation**: Check file size (< 50MB) and type
3. **Upload**: Send file to Flask backend using FormData
4. **Backend Processing**:
   - Validate file again
   - Generate unique filename (to avoid conflicts)
   - Upload to Firebase Storage
   - Get download URL
5. **Metadata Storage**: Save file info to Firestore
6. **Response**: Return success message to frontend
7. **Reload**: Page refreshes to show new file

**Code Example:**
```python
@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    
    # Validate
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    # Upload to Firebase Storage
    bucket = storage.bucket()
    blob = bucket.blob(f"{user_id}/{uuid.uuid4()}_{file.filename}")
    blob.upload_from_string(file.read())
    
    # Save metadata to Firestore
    db.collection('files').add({
        'user_id': user_id,
        'filename': file.filename,
        'size': file.size,
        'uploaded_at': datetime.now()
    })
    
    return jsonify({'success': True})
```

---

### Q6: How do you ensure only the file owner can download their file?

**Answer:**
1. **Ownership Verification**: Check if `user_id` in session matches `user_id` in file metadata
2. **Authorization Check**: Before allowing download, verify ownership
3. **Error Handling**: Return 403 Forbidden if user doesn't own file

**Code Example:**
```python
@app.route('/download/<file_id>')
def download_file(file_id):
    user_id = session.get('user_id')
    
    # Get file metadata
    file_doc = db.collection('files').document(file_id).get()
    file_data = file_doc.to_dict()
    
    # Verify ownership
    if file_data['user_id'] != user_id:
        return render_template('error.html', error='Unauthorized'), 403
    
    # Allow download
    return redirect(file_data['download_url'])
```

---

### Q7: How do you generate shareable links?

**Answer:**
1. **Generate Token**: Create unique token for each file
2. **Store Token**: Save token in Firestore with file metadata
3. **Create Link**: Generate URL with share token
4. **Public Access**: Anyone with link can download (no login needed)
5. **Verification**: Check share token to find file

**Code Example:**
```python
@app.route('/share/<file_id>')
def share_file(file_id):
    file_doc = db.collection('files').document(file_id).get()
    file_data = file_doc.to_dict()
    
    # Generate shareable link
    share_link = url_for('download_shared', 
                        share_token=file_data['share_token'], 
                        _external=True)
    
    return jsonify({'share_link': share_link})

@app.route('/download-shared/<share_token>')
def download_shared(share_token):
    # Find file by share token (no login required)
    files = db.collection('files').where('share_token', '==', share_token).stream()
    
    for doc in files:
        file_data = doc.to_dict()
        return redirect(file_data['download_url'])
```

---

### Q8: How do you handle file deletion?

**Answer:**
1. **Verify Ownership**: Check if user owns the file
2. **Delete from Storage**: Remove file from Firebase Storage
3. **Delete Metadata**: Remove file record from Firestore
4. **Confirm**: Return success message

**Code Example:**
```python
@app.route('/delete/<file_id>', methods=['POST'])
def delete_file(file_id):
    user_id = session.get('user_id')
    
    # Get file metadata
    file_doc = db.collection('files').document(file_id).get()
    file_data = file_doc.to_dict()
    
    # Verify ownership
    if file_data['user_id'] != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Delete from Storage
    bucket = storage.bucket()
    blob = bucket.blob(file_data['storage_path'])
    blob.delete()
    
    # Delete metadata from Firestore
    db.collection('files').document(file_id).delete()
    
    return jsonify({'success': True})
```

---

## 3. Database & Storage

### Q9: What is Firestore and how is it different from SQL databases?

**Answer:**

| Feature | Firestore | SQL (MySQL, PostgreSQL) |
|---------|-----------|------------------------|
| **Type** | NoSQL | Relational |
| **Structure** | Collections & Documents | Tables & Rows |
| **Schema** | Flexible | Fixed |
| **Scaling** | Automatic | Manual |
| **Queries** | Simple queries | Complex joins |
| **Cost** | Pay per operation | Pay per server |

**Firestore Structure:**
```
Database
├── Collection: users
│   ├── Document: user1
│   │   ├── email: "user@example.com"
│   │   ├── created_at: 2024-01-01
│   │   └── storage_used: 1024
│   └── Document: user2
│       └── ...
└── Collection: files
    ├── Document: file1
    │   ├── user_id: "user1"
    │   ├── filename: "document.pdf"
    │   ├── size: 2048
    │   └── uploaded_at: 2024-01-15
    └── Document: file2
        └── ...
```

---

### Q10: How do you optimize Firestore queries?

**Answer:**
1. **Index Creation**: Create indexes for frequently queried fields
2. **Query Optimization**: Only fetch needed fields
3. **Pagination**: Load files in batches instead of all at once
4. **Caching**: Cache frequently accessed data

**Example - Optimized Query:**
```python
# Bad: Fetches all fields
files = db.collection('files').where('user_id', '==', user_id).stream()

# Good: Fetch only needed fields
files = db.collection('files')\
    .where('user_id', '==', user_id)\
    .select(['filename', 'size', 'uploaded_at'])\
    .stream()

# Better: Add pagination
files = db.collection('files')\
    .where('user_id', '==', user_id)\
    .order_by('uploaded_at', direction=firestore.Query.DESCENDING)\
    .limit(10)\
    .stream()
```

---

## 4. Security

### Q11: What security measures did you implement?

**Answer:**
1. **Authentication**: Firebase handles password hashing and storage
2. **Authorization**: Verify user ownership before allowing operations
3. **Session Management**: Store user ID in secure session
4. **Input Validation**: Validate file type and size
5. **HTTPS**: Use HTTPS in production (not HTTP)
6. **Credentials**: Never commit serviceAccountKey.json to Git
7. **Firestore Rules**: Restrict database access to authenticated users

**Firestore Security Rules:**
```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /files/{document=**} {
      allow read, write: if request.auth.uid == resource.data.user_id;
    }
  }
}
```

---

### Q12: How do you prevent unauthorized file access?

**Answer:**
1. **Ownership Check**: Verify user_id matches before download
2. **Share Token**: Use unique token for shared files
3. **Firestore Rules**: Database rules prevent direct access
4. **Storage Rules**: Storage rules prevent direct access

**Code Example:**
```python
# Before allowing download
if file_data['user_id'] != current_user_id:
    return error_response('Unauthorized')
```

---

## 5. Frontend & UX

### Q13: How do you handle drag-and-drop file upload?

**Answer:**
1. **Dragover Event**: Highlight upload area when file is dragged
2. **Drop Event**: Capture dropped files
3. **Validation**: Check file type and size
4. **Upload**: Send to backend

**Code Example:**
```javascript
uploadBox.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadBox.style.backgroundColor = '#e8f4f8';
});

uploadBox.addEventListener('drop', (e) => {
    e.preventDefault();
    const files = e.dataTransfer.files;
    for (let file of files) {
        uploadFile(file);
    }
});
```

---

### Q14: How do you show upload progress to user?

**Answer:**
1. **Show Progress Bar**: Display progress bar when upload starts
2. **Update Progress**: Update bar as file uploads
3. **Show Status**: Display current filename and status
4. **Complete**: Show success message when done

**Code Example:**
```javascript
function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    uploadProgress.style.display = 'block';
    uploadStatus.textContent = `Uploading: ${file.name}...`;
    
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            progressFill.style.width = '100%';
            uploadStatus.textContent = `✓ ${file.name} uploaded!`;
        }
    });
}
```

---

## 6. Deployment & Scalability

### Q15: How would you deploy this project to production?

**Answer:**
1. **Choose Platform**: Render, Heroku, or Firebase Hosting
2. **Prepare Code**: Remove debug mode, add error handling
3. **Environment Variables**: Store secrets in environment variables
4. **Database**: Use production Firestore rules
5. **HTTPS**: Enable HTTPS
6. **Monitoring**: Set up error tracking

**Steps:**
```bash
# 1. Create account on Render
# 2. Connect GitHub repository
# 3. Set environment variables
# 4. Deploy
```

---

### Q16: How would you scale this project for millions of users?

**Answer:**
1. **Database Optimization**: Add indexes, optimize queries
2. **Caching**: Use Redis for frequently accessed data
3. **CDN**: Use CDN for file delivery
4. **Load Balancing**: Distribute traffic across servers
5. **Microservices**: Split into smaller services
6. **Monitoring**: Track performance and errors

---

## 7. Troubleshooting

### Q17: What would you do if file upload fails?

**Answer:**
1. **Check Error Message**: Read error from backend
2. **Validate File**: Check file size and type
3. **Check Network**: Verify internet connection
4. **Check Storage**: Verify Firebase Storage has space
5. **Check Permissions**: Verify Firestore/Storage rules
6. **Retry**: Implement retry logic

---

### Q18: How would you debug a slow dashboard?

**Answer:**
1. **Check Network**: Use browser DevTools Network tab
2. **Check Queries**: Optimize Firestore queries
3. **Add Pagination**: Load files in batches
4. **Add Caching**: Cache frequently accessed data
5. **Monitor**: Use Firebase monitoring tools

---

## 8. Best Practices

### Q19: What best practices did you follow?

**Answer:**
1. **Code Organization**: Separate concerns (routes, templates, static files)
2. **Comments**: Add comments explaining code
3. **Error Handling**: Handle errors gracefully
4. **Validation**: Validate all inputs
5. **Security**: Never expose secrets
6. **Testing**: Test all features
7. **Documentation**: Document setup and usage

---

### Q20: What would you improve in this project?

**Answer:**
1. **Add Tests**: Unit tests and integration tests
2. **Add Logging**: Log all operations for debugging
3. **Add Notifications**: Email notifications for file sharing
4. **Add Versioning**: Keep file versions/history
5. **Add Compression**: Compress files before upload
6. **Add Encryption**: Encrypt files at rest
7. **Add Rate Limiting**: Prevent abuse
8. **Add Analytics**: Track usage statistics
9. **Add Search**: Search files by name
10. **Add Collaboration**: Share folders with other users

---

## Quick Reference

### Key Concepts
- **Flask**: Web framework for backend
- **Firebase**: Cloud platform for auth, storage, database
- **Firestore**: NoSQL database for metadata
- **Storage**: Cloud file storage
- **Authentication**: User login/signup
- **Authorization**: Permission checking
- **Session**: Store user info temporarily
- **REST API**: Communication between frontend and backend

### Important Files
- `app.py`: Main Flask application
- `templates/`: HTML files
- `static/`: CSS and JavaScript
- `requirements.txt`: Python dependencies
- `serviceAccountKey.json`: Firebase credentials

### Common Commands
```bash
# Activate virtual environment
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run Flask server
python app.py

# Deactivate virtual environment
deactivate
```

---

## Tips for Viva

1. **Understand the code**: Know what each function does
2. **Know the architecture**: Explain how components interact
3. **Be honest**: If you don't know, say so
4. **Ask for clarification**: If question is unclear, ask
5. **Give examples**: Use code examples to explain
6. **Think about security**: Always consider security implications
7. **Discuss trade-offs**: Explain why you made certain choices
8. **Show enthusiasm**: Demonstrate interest in the project
9. **Practice**: Rehearse answers before viva
10. **Stay calm**: Take time to think before answering
