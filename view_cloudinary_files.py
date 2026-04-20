#!/usr/bin/env python3
# ============================================================================
# View Uploaded Files in Cloudinary
# ============================================================================
# This script lists all files uploaded to your Cloudinary account
# ============================================================================

import cloudinary
import cloudinary.api
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

print("=" * 80)
print("CLOUDINARY FILES VIEWER")
print("=" * 80)

try:
    # Get all resources (files) from Cloudinary
    print("\n📁 Fetching files from Cloudinary...\n")
    
    resources = cloudinary.api.resources(max_results=500)
    
    files = resources.get('resources', [])
    
    if not files:
        print("❌ No files found in Cloudinary")
        print("\nMake sure you:")
        print("1. Uploaded files using the web app")
        print("2. Have correct Cloudinary credentials in .env")
        exit(1)
    
    print(f"✓ Found {len(files)} file(s)\n")
    print("-" * 80)
    
    # Display each file
    for idx, file in enumerate(files, 1):
        public_id = file.get('public_id', 'N/A')
        file_type = file.get('type', 'N/A')
        resource_type = file.get('resource_type', 'N/A')
        size = file.get('bytes', 0)
        created = file.get('created_at', 'N/A')
        url = file.get('secure_url', 'N/A')
        
        # Convert size to MB
        size_mb = size / (1024 * 1024) if size else 0
        
        print(f"\n📄 File #{idx}")
        print(f"   Name: {public_id}")
        print(f"   Type: {resource_type}")
        print(f"   Size: {size_mb:.2f} MB ({size} bytes)")
        print(f"   Created: {created}")
        print(f"   URL: {url}")
        print("-" * 80)
    
    # Summary
    total_size = sum(f.get('bytes', 0) for f in files)
    total_size_mb = total_size / (1024 * 1024)
    
    print(f"\n📊 SUMMARY")
    print(f"   Total Files: {len(files)}")
    print(f"   Total Size: {total_size_mb:.2f} MB")
    print(f"   Cloud Name: {os.getenv('CLOUDINARY_CLOUD_NAME')}")
    print("=" * 80)

except Exception as e:
    print(f"❌ Error: {str(e)}")
    print("\nTroubleshooting:")
    print("1. Check .env file has correct Cloudinary credentials")
    print("2. Verify CLOUDINARY_CLOUD_NAME is correct")
    print("3. Verify CLOUDINARY_API_KEY is correct")
    print("4. Verify CLOUDINARY_API_SECRET is correct")
    print("5. Make sure you have uploaded files using the web app")
