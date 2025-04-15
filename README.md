# Data Shifting Removal Application

A web-based application for fixing data shifting issues in delimited text files. The application provides a user-friendly interface for uploading, processing, and downloading fixed data files.

## Features

- **Data Shifting Correction**: Fixes issues where newlines are embedded within text-qualified fields
- **Special Cases Handling**: Properly handles embedded quotes within fields, including inch marks (e.g., "60"")
- **Multi-User Support**: Supports concurrent usage from different browsers or machines
- **Space and Tab Handling**: Trims extra spaces to a single space and replaces tabs with spaces
- **Folder Maintenance**: Automatically cleans up old files to prevent accumulation
- **Error Logging**: Provides detailed error logs for problematic records
- **Web Interface**: User-friendly interface with file upload, processing options, and results display

## Technical Overview

### Data Processing Features

- **Embedded Quotes Handling**: Correctly handles embedded quotes (e.g., `"CAP-GOWN PKG ULTRA NAVY 60""`)
- **Qualified Content Cleaning**: Replaces newlines with spaces, normalizes spaces, and replaces tabs
- **Column Counting**: Accurately counts columns respecting text qualifiers
- **Pattern Detection**: Detects common patterns like inch marks in measurements
- **Intelligent Text Processing**: Distinguishes between embedded quotes in text and measurement units

### Multi-User Support

The application uses session-based management to ensure different users can process files concurrently:

- Each user automatically receives a unique session ID using UUID
- User-specific folders are created for both uploads and outputs
- Files from different users are completely isolated from each other
- Session persistence allows users to return and access their previous files
- All file operations are contained within user-specific directories

### File Maintenance

- **Automatic Cleanup**: The system automatically manages disk space
- **Recent Files**: Only keeps the most recent files in each user's folders
- **Uploads Folder**: Keeps the last 10 uploaded files per user
- **Outputs Folder**: Maintains the last 20 output files per user
- **Inactive Users**: Folders for users inactive for 7+ days are automatically removed
- **Graceful Error Handling**: The system continues to function even if files are missing

## Usage

1. Start the application: `python app.py`
2. Access the web interface: `http://localhost:5000`
3. Upload your file
4. Set the appropriate delimiter (default: `|^|`) and qualifier (default: `"`)
5. Click "Process File"
6. Download the processed files

## Command Line Usage

The core functionality can also be used from the command line:

```
python data_shifting.py input.txt output.txt --delimiter "|^|" --qualifier "\""
```

## Testing

Run the test suite to verify functionality:

```
python data_shifting.py --test
```

## Requirements

- Python 3.6 or higher
- Flask
- Werkzeug

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```
pip install flask werkzeug
```

## File Structure

- `app.py`: Main Flask application with multi-user support
- `data_shifting.py`: Core data shifting correction logic
- `templates/`: HTML templates for the web interface
- `uploads/`: Root directory for user-specific upload folders
- `outputs/`: Root directory for user-specific output folders

## Error Handling

The tool generates three types of files:

1. **Corrected File**: Contains the fixed data with corrected line transactions
2. **Error Log File**: Detailed information about any issues encountered during processing
3. **Error Transactions File**: Only contains the problematic data rows for easy review

The application includes robust error handling:
- Files that don't exist are gracefully handled with appropriate user feedback
- Processing errors don't crash the application
- Missing error transaction files don't cause FileNotFoundError exceptions

## Example

For a file with data shifting issues like:

```
Name|^|Age|^|Description
"John Doe"|^|30|^|"Software
Engineer"
"Jane Smith"|^|28|^|"Data Analyst"
```

The corrected output would be:

```
Name|^|Age|^|Description
"John Doe"|^|30|^|"Software Engineer"
"Jane Smith"|^|28|^|"Data Analyst"
```

## Special Case Handling

The application correctly handles special cases such as:

1. **Embedded quotes**: `"ADB will apply SSL Certificates for WGU Complio "Splash pages""`
2. **Inch measurements**: `"CAP-GOWN PKG ULTRA NAVY 60""` → `"CAP-GOWN PKG ULTRA NAVY 60 inches"`
3. **Multiple spaces**: Converts `"Multiple   spaces"` to `"Multiple spaces"`
4. **Tabs in text**: Replaces tabs with spaces for cleaner output 