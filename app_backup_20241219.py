from flask import Flask, render_template, request, send_file, flash, redirect, url_for, Response, session
import os
import uuid
from werkzeug.utils import secure_filename
import tempfile
from pathlib import Path
import glob
import time
import shutil
import random
from data_shifting import fix_data_shifting

app = Flask(__name__)
app.secret_key = 'data_shifting_secret_key'

# Configure base folders
BASE_UPLOAD_FOLDER = 'uploads'
BASE_OUTPUT_FOLDER = 'outputs'

# Create base directories if they don't exist
if not os.path.exists(BASE_UPLOAD_FOLDER):
    os.makedirs(BASE_UPLOAD_FOLDER)
if not os.path.exists(BASE_OUTPUT_FOLDER):
    os.makedirs(BASE_OUTPUT_FOLDER)

# Configure allowed file extensions
ALLOWED_EXTENSIONS = {'txt', 'csv', 'dat', 'tsv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_user_folders():
    """
    Get or create user-specific folders for uploads and outputs.
    This ensures different users can process files concurrently without interference.
    
    Returns:
        tuple: (upload_folder, output_folder) paths for the current user
    """
    # Check if user has a session ID, create one if not
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    
    user_id = session['user_id']
    
    # Create user-specific folders
    user_upload_folder = os.path.join(BASE_UPLOAD_FOLDER, user_id)
    user_output_folder = os.path.join(BASE_OUTPUT_FOLDER, user_id)
    
    # Ensure directories exist
    if not os.path.exists(user_upload_folder):
        os.makedirs(user_upload_folder)
    if not os.path.exists(user_output_folder):
        os.makedirs(user_output_folder)
    
    return user_upload_folder, user_output_folder

def cleanup_user_folders(user_folder, max_files=10):
    """
    Maintain and clean up user-specific folders, keeping only the most recent max_files.
    All other files are deleted to prevent accumulation of old files.
    
    Args:
        user_folder (str): Path to the user folder
        max_files (int): Maximum number of files to keep (default: 10)
    """
    try:
        # Get list of all files in the folder with their modification times
        files = []
        for file_path in glob.glob(os.path.join(user_folder, '*')):
            if os.path.isfile(file_path):
                files.append((file_path, os.path.getmtime(file_path)))
        
        # Sort files by modification time (newest first)
        files.sort(key=lambda x: x[1], reverse=True)
        
        # Keep only the most recent max_files
        files_to_delete = files[max_files:]
        
        # Delete older files
        for file_path, _ in files_to_delete:
            try:
                os.remove(file_path)
                print(f"Deleted old file: {file_path}")
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")
        
        return len(files_to_delete)
    except Exception as e:
        print(f"Error cleaning up folder {user_folder}: {e}")
        return 0

def cleanup_inactive_users(base_folder, max_age_days=7):
    """
    Clean up folders for inactive users (folders not accessed in the last max_age_days).
    
    Args:
        base_folder (str): Base folder containing user folders
        max_age_days (int): Maximum number of days since last access before removal
    """
    try:
        current_time = time.time()
        max_age_seconds = max_age_days * 24 * 60 * 60
        
        # Check each user folder
        for user_folder in glob.glob(os.path.join(base_folder, '*')):
            if os.path.isdir(user_folder):
                # Get the last access time of the folder
                last_access_time = os.path.getatime(user_folder)
                
                # If folder hasn't been accessed in max_age_days, remove it
                if current_time - last_access_time > max_age_seconds:
                    try:
                        shutil.rmtree(user_folder)
                        print(f"Removed inactive user folder: {user_folder}")
                    except Exception as e:
                        print(f"Error removing inactive user folder {user_folder}: {e}")
    except Exception as e:
        print(f"Error cleaning up inactive users: {e}")

@app.route('/custom.css')
def custom_css():
    css = """
    /* Navbar styles */
    .navbar {
        background: linear-gradient(135deg, #2563eb, #3b82f6);
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        padding: 0.8rem 1rem;
    }
    
    .navbar-brand {
        color: white !important;
        font-weight: 600;
        font-size: 1.4rem;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .navbar-brand i {
        font-size: 1.5rem;
    }
    
    .nav-link {
        color: rgba(255, 255, 255, 0.85) !important;
        font-weight: 500;
        transition: all 0.2s ease;
        padding: 0.5rem 1rem;
        border-radius: 8px;
    }
    
    .nav-link:hover, .nav-link.active {
        color: white !important;
        background-color: rgba(255, 255, 255, 0.15);
    }
    
    /* Container adjustments for navbar */
    .main-container {
        padding-top: 20px;
        padding-bottom: 40px;
    }
    
    /* Smaller file upload container */
    .file-upload-container {
        padding: 20px !important;
        max-width: 800px;
        margin: 0 auto;
        height: auto !important;
    }
    
    .file-upload-icon {
        font-size: 2.2rem !important;
        margin-bottom: 10px !important;
    }
    
    .file-upload-container .form-text {
        margin-top: 8px !important;
    }
    
    /* Make all form sections consistent height */
    .form-section {
        max-width: 900px;
        margin-left: auto;
        margin-right: auto;
        padding-top: 25px !important;
        padding-bottom: 25px !important;
    }
    
    /* Header adjustments */
    .header {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    
    /* Navbar dropdown */
    .navbar .dropdown-menu {
        background-color: white;
        border: none;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        margin-top: 10px;
    }
    
    .navbar .dropdown-item {
        color: var(--text-primary);
        font-weight: 500;
        padding: 8px 15px;
        transition: all 0.2s ease;
    }
    
    .navbar .dropdown-item:hover {
        background-color: var(--background-color);
        color: var(--primary-color);
    }
    
    .navbar .dropdown-item i {
        margin-right: 10px;
        color: var(--primary-color);
    }
    
    /* Adjust body spacing when navbar is present */
    body {
        padding-top: 0 !important;
    }
    
    /* Adjust header styling */
    .header::after {
        bottom: -10px;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .navbar-brand {
            font-size: 1.2rem;
        }
        
        .file-upload-container {
            padding: 15px !important;
        }
    }
    """
    return Response(css, mimetype='text/css')

@app.route('/navbar')
def navbar():
    return render_template('navbar.html')

@app.route('/custom_scripts')
def custom_scripts():
    js = """
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        // Initialize Bootstrap components
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl)
        });
        
        // Highlight active nav item
        var currentPath = window.location.pathname;
        var navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(function(link) {
            if (link.getAttribute('href') === currentPath) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    });
    </script>
    """
    return js

@app.route('/home')
def home_redirect():
    return redirect(url_for('home'))

@app.route('/', methods=['GET', 'POST'])
def home():
    # Get user-specific folders
    user_upload_folder, user_output_folder = get_user_folders()
    
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']
        
        # If user does not select file, browser also
        # submits an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            input_filepath = os.path.join(user_upload_folder, filename)
            file.save(input_filepath)
            
            # Get form data
            delimiter_option = request.form.get('delimiter_option', 'standard')
            standard_delimiter = request.form.get('standard_delimiter', '|^|')
            custom_delimiter = request.form.get('custom_delimiter', '')
            
            qualifier_option = request.form.get('qualifier_option', 'standard')
            standard_qualifier = request.form.get('standard_qualifier', '"')
            custom_qualifier = request.form.get('custom_qualifier', '')
            
            # Determine which delimiter and qualifier to use
            delimiter = custom_delimiter if delimiter_option == 'custom' else standard_delimiter
            qualifier = custom_qualifier if qualifier_option == 'custom' else standard_qualifier
            
            # Define output paths
            base_filename = os.path.splitext(filename)[0]
            output_filepath = os.path.join(user_output_folder, f"{base_filename}_corrected.txt")
            error_filepath = os.path.join(user_output_folder, f"{base_filename}_errors.log")
            error_transactions_filepath = os.path.join(user_output_folder, f"{base_filename}_error_transactions.txt")
            
            # Process the file
            try:
                fix_data_shifting(
                    Path(input_filepath), 
                    Path(output_filepath), 
                    Path(error_filepath),
                    Path(error_transactions_filepath),
                    delimiter, 
                    qualifier
                )
            except FileNotFoundError as e:
                # Catch any FileNotFoundError that might be raised if files don't exist
                print(f"FileNotFoundError during processing: {e}")
                # Continue execution - we'll check which files were created next
            except Exception as e:
                # Log other errors but allow the process to continue
                print(f"Error during processing: {e}")
            
            # Clean up user folders after processing
            deleted_upload_count = cleanup_user_folders(user_upload_folder)
            deleted_output_count = cleanup_user_folders(user_output_folder, max_files=20)  # Keep more output files
            
            # Periodically clean up inactive user folders (run this occasionally)
            if random.random() < 0.1:  # 10% chance to run on any request
                cleanup_inactive_users(BASE_UPLOAD_FOLDER)
                cleanup_inactive_users(BASE_OUTPUT_FOLDER)
            
            # Check which files were actually created
            output_file = f"{base_filename}_corrected.txt"
            
            # Check if error files exist (they may not be created if there were no errors)
            error_file = f"{base_filename}_errors.log" if os.path.exists(os.path.join(user_output_folder, f"{base_filename}_errors.log")) else None
            error_transactions_file = f"{base_filename}_error_transactions.txt" if os.path.exists(os.path.join(user_output_folder, f"{base_filename}_error_transactions.txt")) else None
            
            return render_template(
                'results.html',
                input_file=filename,
                output_file=output_file,
                error_file=error_file,
                error_transactions_file=error_transactions_file,
                has_errors=(error_file is not None or error_transactions_file is not None),
                navbar=navbar(),
                custom_css=url_for('custom_css'),
                custom_scripts=custom_scripts()
            )
        else:
            flash(f'File type not allowed. Please upload one of the following types: {", ".join(ALLOWED_EXTENSIONS)}')
            return redirect(request.url)
    
    # GET request
    return render_template('index.html', 
                           navbar=navbar(), 
                           custom_css=url_for('custom_css'),
                           custom_scripts=custom_scripts())

@app.route('/download/<filename>')
def download_file(filename):
    # Get user-specific output folder
    _, user_output_folder = get_user_folders()
    
    file_path = os.path.join(user_output_folder, filename)
    
    # Check if file exists
    if not os.path.exists(file_path):
        flash(f"File {filename} does not exist")
        return redirect(url_for('home'))
        
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
