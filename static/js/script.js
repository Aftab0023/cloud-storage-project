// ============================================================================
// Cloud Storage System - Frontend JavaScript
// ============================================================================
// This file contains all frontend logic for the application
// ============================================================================

// ============================================================================
// 1. UTILITY FUNCTIONS
// ============================================================================

/**
 * Show notification to user
 * @param {string} message - Message to display
 * @param {string} type - 'success', 'error', or 'info'
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.textContent = message;
    
    const container = document.querySelector('.container');
    container.insertBefore(notification, container.firstChild);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

/**
 * Format file size to human-readable format
 * @param {number} bytes - File size in bytes
 * @returns {string} Formatted size
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

/**
 * Format date to readable format
 * @param {Date} date - Date object
 * @returns {string} Formatted date
 */
function formatDate(date) {
    return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// ============================================================================
// 2. FORM VALIDATION
// ============================================================================

/**
 * Validate email format
 * @param {string} email - Email to validate
 * @returns {boolean} True if valid
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Validate password strength
 * @param {string} password - Password to validate
 * @returns {object} Validation result
 */
function validatePassword(password) {
    const result = {
        isValid: true,
        errors: []
    };
    
    if (password.length < 6) {
        result.isValid = false;
        result.errors.push('Password must be at least 6 characters');
    }
    
    if (!/[A-Z]/.test(password)) {
        result.errors.push('Password should contain uppercase letters');
    }
    
    if (!/[0-9]/.test(password)) {
        result.errors.push('Password should contain numbers');
    }
    
    return result;
}

// ============================================================================
// 3. FILE UPLOAD HANDLING
// ============================================================================

/**
 * Handle file upload with progress tracking
 * @param {File} file - File to upload
 */
function uploadFile(file) {
    // Validate file
    const maxSize = 50 * 1024 * 1024; // 50MB
    
    if (file.size > maxSize) {
        showNotification(`File too large. Maximum size is 50MB.`, 'error');
        return;
    }
    
    const allowedTypes = ['text/plain', 'application/pdf', 'image/png', 'image/jpeg', 'image/gif'];
    
    if (!allowedTypes.includes(file.type) && !file.name.match(/\.(doc|docx|xls|xlsx|zip)$/i)) {
        showNotification(`File type not allowed.`, 'error');
        return;
    }
    
    // Create FormData
    const formData = new FormData();
    formData.append('file', file);
    
    // Show progress
    const uploadProgress = document.getElementById('uploadProgress');
    const progressFill = document.getElementById('progressFill');
    const uploadStatus = document.getElementById('uploadStatus');
    
    if (uploadProgress) {
        uploadProgress.style.display = 'block';
        uploadStatus.textContent = `Uploading: ${file.name}...`;
        progressFill.style.width = '0%';
    }
    
    // Upload file
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (uploadStatus) {
                uploadStatus.textContent = `✓ ${file.name} uploaded successfully!`;
                progressFill.style.width = '100%';
            }
            
            showNotification(`${file.name} uploaded successfully!`, 'success');
            
            // Reload page after 1 second
            setTimeout(() => {
                location.reload();
            }, 1000);
        } else {
            showNotification(`Upload failed: ${data.error}`, 'error');
        }
    })
    .catch(error => {
        showNotification(`Upload error: ${error}`, 'error');
    });
}

// ============================================================================
// 4. FILE ACTIONS
// ============================================================================

/**
 * Download a file
 * @param {string} fileId - File ID to download
 */
function downloadFile(fileId) {
    window.location.href = `/download/${fileId}`;
}

/**
 * Delete a file
 * @param {string} fileId - File ID to delete
 */
function deleteFile(fileId) {
    if (!confirm('Are you sure you want to delete this file? This action cannot be undone.')) {
        return;
    }
    
    fetch(`/delete/${fileId}`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('File deleted successfully', 'success');
            
            // Remove file row from table
            const fileRow = document.querySelector(`[data-file-id="${fileId}"]`);
            if (fileRow) {
                fileRow.style.opacity = '0';
                setTimeout(() => {
                    fileRow.remove();
                }, 300);
            }
        } else {
            showNotification(`Delete failed: ${data.error}`, 'error');
        }
    })
    .catch(error => {
        showNotification(`Delete error: ${error}`, 'error');
    });
}

/**
 * Share a file
 * @param {string} fileId - File ID to share
 */
function shareFile(fileId) {
    fetch(`/share/${fileId}`)
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Show share modal
            const shareModal = document.getElementById('shareModal');
            const shareLink = document.getElementById('shareLink');
            
            if (shareModal && shareLink) {
                shareLink.value = data.share_link;
                shareModal.style.display = 'block';
            }
            
            showNotification('Share link generated', 'success');
        } else {
            showNotification(`Share failed: ${data.error}`, 'error');
        }
    })
    .catch(error => {
        showNotification(`Share error: ${error}`, 'error');
    });
}

/**
 * Copy share link to clipboard
 */
function copyShareLink() {
    const shareLink = document.getElementById('shareLink');
    
    if (shareLink) {
        shareLink.select();
        document.execCommand('copy');
        showNotification('Link copied to clipboard!', 'success');
    }
}

/**
 * Close share modal
 */
function closeShareModal() {
    const shareModal = document.getElementById('shareModal');
    if (shareModal) {
        shareModal.style.display = 'none';
    }
}

// ============================================================================
// 5. EVENT LISTENERS
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    // Upload box drag and drop
    const uploadBox = document.getElementById('uploadBox');
    const fileInput = document.getElementById('fileInput');
    
    if (uploadBox && fileInput) {
        // Click to upload
        uploadBox.addEventListener('click', () => {
            fileInput.click();
        });
        
        // Drag over
        uploadBox.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadBox.style.backgroundColor = '#e8f4f8';
            uploadBox.style.borderColor = '#764ba2';
        });
        
        // Drag leave
        uploadBox.addEventListener('dragleave', () => {
            uploadBox.style.backgroundColor = '';
            uploadBox.style.borderColor = '';
        });
        
        // Drop
        uploadBox.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadBox.style.backgroundColor = '';
            uploadBox.style.borderColor = '';
            
            const files = e.dataTransfer.files;
            for (let file of files) {
                uploadFile(file);
            }
        });
        
        // File input change
        fileInput.addEventListener('change', (e) => {
            const files = e.target.files;
            for (let file of files) {
                uploadFile(file);
            }
        });
    }
    
    // Modal close button
    const closeButtons = document.querySelectorAll('.close');
    closeButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            this.closest('.modal').style.display = 'none';
        });
    });
    
    // Close modal when clicking outside
    window.addEventListener('click', (e) => {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });
    });
});

// ============================================================================
// 6. KEYBOARD SHORTCUTS
// ============================================================================

document.addEventListener('keydown', function(e) {
    // Ctrl+U or Cmd+U to open upload
    if ((e.ctrlKey || e.metaKey) && e.key === 'u') {
        e.preventDefault();
        const fileInput = document.getElementById('fileInput');
        if (fileInput) {
            fileInput.click();
        }
    }
    
    // Escape to close modal
    if (e.key === 'Escape') {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.style.display = 'none';
        });
    }
});

// ============================================================================
// 7. EXPORT FUNCTIONS FOR GLOBAL USE
// ============================================================================

window.uploadFile = uploadFile;
window.downloadFile = downloadFile;
window.deleteFile = deleteFile;
window.shareFile = shareFile;
window.copyShareLink = copyShareLink;
window.closeShareModal = closeShareModal;
window.showNotification = showNotification;
window.formatFileSize = formatFileSize;
window.formatDate = formatDate;
