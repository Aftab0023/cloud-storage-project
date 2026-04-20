# ============================================================================
# Cloud-Based File Storage System - Flask Backend with Cloudinary
# ============================================================================
# This is the main Flask application that handles all backend logic
# Uses Cloudinary for file storage and Firebase for auth + database
# ============================================================================

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, auth, firestore
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
import uuid
import cloudinary
import cloudinary.uploader
import cloudinary.api
import requests
from dotenv import load_dotenv

# ============================================================================
# 0. LOAD ENVIRONMENT VARIABLES
# ============================================================================

load_dotenv()

# ============================================================================
# 1. INITIALIZE FLASK APP
# ============================================================================

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')
CORS(app)

# Configuration
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'zip', 'mp4', 'mov', 'avi', 'mp3', 'wav'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# ============================================================================
# 2. INITIALIZE CLOUDINARY
# ============================================================================

cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

print("✓ Cloudinary configured successfully")

# ============================================================================
# 3. INITIALIZE FIREBASE
# ============================================================================

# Load Firebase credentials from serviceAccountKey.json
try:
    cred = credentials.Certificate('serviceAccountKey.json')
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("✓ Firebase initialized successfully")
except Exception as e:
    print(f"✗ Firebase initialization error: {e}")

# ============================================================================
# 4. HELPER FUNCTIONS
# ============================================================================

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_size_mb(size_bytes):
    """Convert bytes to MB"""
    return round(size_bytes / (1024 * 1024), 2)

def get_user_from_session():
    """Get current logged-in user from session"""
    if 'user_id' in session:
        return session['user_id']
    return None

# ============================================================================
# 5. AUTHENTICATION ROUTES
# ============================================================================

@app.route('/')
def index():
    """Home page - redirect to dashboard if logged in"""
    if get_user_from_session():
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    Handle user signup
    GET: Show signup form
    POST: Create new user account
    """
    if request.method == 'GET':
        return render_template('signup.html')
    
    try:
        # Get form data
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not email or not password:
            return render_template('signup.html', error='Email and password required'), 400
        
        if password != confirm_password:
            return render_template('signup.html', error='Passwords do not match'), 400
        
        if len(password) < 6:
            return render_template('signup.html', error='Password must be at least 6 characters'), 400
        
        # Create user in Firebase Authentication
        user = auth.create_user(email=email, password=password)
        
        # Store user info in Firestore
        db.collection('users').document(user.uid).set({
            'email': email,
            'created_at': datetime.now(),
            'storage_used': 0  # Track storage usage
        })
        
        return render_template('signup.html', success='Account created! Please login.'), 200
    
    except auth.EmailAlreadyExistsError:
        return render_template('signup.html', error='Email already exists'), 400
    except Exception as e:
        return render_template('signup.html', error=f'Error: {str(e)}'), 400

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login
    GET: Show login form
    POST: Authenticate user
    """
    if request.method == 'GET':
        return render_template('login.html')
    
    try:
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            return render_template('login.html', error='Email and password required'), 400
        
        # Verify user credentials using Firebase REST API
        api_key = os.getenv('FIREBASE_API_KEY')
        
        if not api_key:
            return render_template('login.html', error='Firebase API Key not configured'), 500
        
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            user_id = data['localId']
            
            # Store user ID in session
            session['user_id'] = user_id
            session['email'] = email
            
            return redirect(url_for('dashboard'))
        else:
            error_data = response.json()
            error_message = error_data.get('error', {}).get('message', 'Invalid email or password')
            return render_template('login.html', error=error_message), 401
    
    except Exception as e:
        return render_template('login.html', error=f'Error: {str(e)}'), 400

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('login'))

# ============================================================================
# 6. FILE MANAGEMENT ROUTES
# ============================================================================

@app.route('/dashboard')
def dashboard():
    """Show main dashboard with user's files"""
    user_id = get_user_from_session()
    
    if not user_id:
        return redirect(url_for('login'))
    
    try:
        # Get all files for this user from Firestore
        files_ref = db.collection('files').where('user_id', '==', user_id).stream()
        
        files = []
        total_size = 0
        
        for doc in files_ref:
            file_data = doc.to_dict()
            file_data['id'] = doc.id
            files.append(file_data)
            total_size += file_data.get('size', 0)
        
        # Sort by upload date (newest first)
        files.sort(key=lambda x: x.get('uploaded_at', ''), reverse=True)
        
        return render_template('dashboard.html', 
                             files=files, 
                             total_size=get_file_size_mb(total_size),
                             email=session.get('email'))
    
    except Exception as e:
        return render_template('error.html', error=f'Error loading dashboard: {str(e)}'), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Handle file upload to Cloudinary
    1. Receive file from frontend
    2. Upload to Cloudinary
    3. Save metadata to Firestore
    """
    user_id = get_user_from_session()
    
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({'error': 'File too large (max 50MB)'}), 400
        
        # Create unique filename
        original_filename = secure_filename(file.filename)
        unique_public_id = f"{user_id}/{uuid.uuid4()}_{original_filename}"
        
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            file,
            public_id=unique_public_id,
            resource_type="auto",  # Auto-detect file type
            overwrite=False
        )
        
        # Get secure URL
        download_url = result['secure_url']
        
        # Save metadata to Firestore
        file_doc = {
            'user_id': user_id,
            'filename': original_filename,
            'cloudinary_public_id': result['public_id'],
            'size': file_size,
            'uploaded_at': datetime.now(),
            'download_url': download_url,
            'share_token': str(uuid.uuid4()),  # For shareable links
            'file_type': result['resource_type']
        }
        
        db.collection('files').add(file_doc)
        
        return jsonify({
            'success': True,
            'message': 'File uploaded successfully',
            'filename': original_filename,
            'size': get_file_size_mb(file_size)
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/download/<file_id>')
def download_file(file_id):
    """
    Handle file download
    1. Get file metadata from Firestore
    2. Verify user owns the file
    3. Redirect to Cloudinary download URL
    """
    user_id = get_user_from_session()
    
    if not user_id:
        return redirect(url_for('login'))
    
    try:
        # Get file metadata
        file_doc = db.collection('files').document(file_id).get()
        
        if not file_doc.exists:
            return render_template('error.html', error='File not found'), 404
        
        file_data = file_doc.to_dict()
        
        # Verify user owns this file
        if file_data['user_id'] != user_id:
            return render_template('error.html', error='Unauthorized'), 403
        
        # Redirect to Cloudinary download URL
        return redirect(file_data['download_url'])
    
    except Exception as e:
        return render_template('error.html', error=f'Download error: {str(e)}'), 500

@app.route('/delete/<file_id>', methods=['POST'])
def delete_file(file_id):
    """
    Handle file deletion
    1. Verify user owns the file
    2. Delete from Cloudinary
    3. Delete metadata from Firestore
    """
    user_id = get_user_from_session()
    
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        # Get file metadata
        file_doc = db.collection('files').document(file_id).get()
        
        if not file_doc.exists:
            return jsonify({'error': 'File not found'}), 404
        
        file_data = file_doc.to_dict()
        
        # Verify user owns this file
        if file_data['user_id'] != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Delete from Cloudinary
        cloudinary.uploader.destroy(file_data['cloudinary_public_id'])
        
        # Delete metadata from Firestore
        db.collection('files').document(file_id).delete()
        
        return jsonify({'success': True, 'message': 'File deleted successfully'}), 200
    
    except Exception as e:
        return jsonify({'error': f'Delete failed: {str(e)}'}), 500

@app.route('/share/<file_id>')
def share_file(file_id):
    """
    Generate shareable link for a file
    Anyone with this link can download the file
    """
    try:
        # Get file metadata
        file_doc = db.collection('files').document(file_id).get()
        
        if not file_doc.exists:
            return render_template('error.html', error='File not found'), 404
        
        file_data = file_doc.to_dict()
        
        # Return shareable link
        share_link = url_for('download_shared', share_token=file_data['share_token'], _external=True)
        
        return jsonify({
            'success': True,
            'share_link': share_link,
            'filename': file_data['filename']
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Share failed: {str(e)}'}), 500

@app.route('/download-shared/<share_token>')
def download_shared(share_token):
    """
    Download file using share token (no login required)
    """
    try:
        # Find file by share token
        files = db.collection('files').where('share_token', '==', share_token).stream()
        
        file_doc = None
        for doc in files:
            file_doc = doc
            break
        
        if not file_doc:
            return render_template('error.html', error='File not found'), 404
        
        file_data = file_doc.to_dict()
        
        # Redirect to Cloudinary download URL
        return redirect(file_data['download_url'])
    
    except Exception as e:
        return render_template('error.html', error=f'Error: {str(e)}'), 500

# ============================================================================
# 7. ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('error.html', error='Page not found'), 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return render_template('error.html', error='Server error'), 500

# ============================================================================
# 8. RUN THE APP
# ============================================================================

if __name__ == '__main__':
    # Create templates and static folders if they don't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    # Run Flask development server
    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, host='localhost', port=port)
