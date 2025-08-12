# Data Shifting Removal Application

A production-ready web-based application for fixing data shifting issues in delimited text files. The application provides a robust, user-friendly interface for uploading, processing, and downloading fixed data files with enhanced multi-line transaction handling.

## 🚀 Enhanced Features

- **Advanced Data Shifting Correction**: Fixes complex issues where newlines are embedded within text-qualified fields
- **Intelligent Multi-Line Detection**: Automatically detects and combines broken transactions spanning multiple lines
- **Enhanced Embedded Quotes Handling**: Properly handles embedded quotes within fields, including inch marks (e.g., "60"")
- **Robust Transaction Reconstruction**: Can handle transactions spanning up to 25 lines for complex descriptions
- **Multi-User Support**: Supports concurrent usage from different browsers or machines with session isolation
- **Advanced Space and Tab Handling**: Trims extra spaces to a single space and replaces tabs with spaces
- **Intelligent Folder Maintenance**: Automatically cleans up old files to prevent accumulation
- **Comprehensive Error Logging**: Provides detailed error logs and error transaction files for problematic records
- **Professional Web Interface**: User-friendly interface with file upload, processing options, and results display

## 🔧 Technical Overview

### Enhanced Data Processing Features

- **Advanced Multi-Line Detection**: Intelligently identifies incomplete transactions and combines related lines
- **Smart Line Combination**: Combines broken lines until proper column count is achieved (up to 25 lines)
- **Embedded Quotes Handling**: Correctly handles embedded quotes (e.g., `"CAP-GOWN PKG ULTRA NAVY 60""`)
- **Qualified Content Cleaning**: Replaces newlines with spaces, normalizes spaces, and replaces tabs
- **Enhanced Column Counting**: Accurately counts columns respecting text qualifiers with improved logic
- **Pattern Detection**: Detects common patterns like inch marks in measurements and complex descriptions
- **Intelligent Text Processing**: Distinguishes between embedded quotes in text and measurement units
- **Edge Case Handling**: Successfully processes very long descriptions (medical equipment, software details, etc.)

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

## 📖 Usage

### Web Interface
1. Start the application: `python app.py`
2. Access the web interface: `http://localhost:5000`
3. Upload your file (supports .txt, .csv, .dat, .tsv)
4. Set the appropriate delimiter (default: `|^|`) and qualifier (default: `"`)
5. Click "Process File"
6. Download the processed files and review any error logs

### Command Line Usage

The core functionality can also be used from the command line:

```bash
# Basic usage
python data_shifting.py input.txt output.txt

# With custom delimiter and qualifier
python data_shifting.py input.txt output.txt --delimiter "|^|" --qualifier "\""

# With error logging
python data_shifting.py input.txt output.txt --error_file errors.log --error_transactions_file error_transactions.txt

# Run built-in tests
python data_shifting.py --test
```

## 🧪 Testing

Run the comprehensive test suite to verify functionality:

```bash
python data_shifting.py --test
```

The test suite validates:
- Basic embedded quotes handling
- Inch measurement conversions
- Complex pattern recognition
- Column counting accuracy
- Line combination logic

## 📋 Requirements

- Python 3.6 or higher
- Flask
- Werkzeug

## 🚀 Installation

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install flask werkzeug
```

## 📁 File Structure

- `app.py`: Main Flask application with multi-user support and enhanced error handling
- `data_shifting.py`: Enhanced core data shifting correction logic with advanced multi-line detection
- `templates/`: HTML templates for the professional web interface
- `uploads/`: Root directory for user-specific upload folders
- `outputs/`: Root directory for user-specific output folders

## ⚠️ Error Handling

The tool generates three types of files:

1. **Corrected File**: Contains the fixed data with corrected line transactions
2. **Error Log File**: Detailed information about any issues encountered during processing
3. **Error Transactions File**: Only contains the problematic data rows for easy review

The application includes robust error handling:
- Files that don't exist are gracefully handled with appropriate user feedback
- Processing errors don't crash the application
- Missing error transaction files don't cause FileNotFoundError exceptions
- Comprehensive logging of all multi-line transaction fixes

## 💡 Examples

### Simple Data Shifting Fix

**Input (with data shifting):**
```
Name|^|Age|^|Description
"John Doe"|^|30|^|"Software
Engineer"
"Jane Smith"|^|28|^|"Data Analyst"
```

**Output (corrected):**
```
Name|^|Age|^|Description
"John Doe"|^|30|^|"Software Engineer"
"Jane Smith"|^|28|^|"Data Analyst"
```

### Complex Multi-Line Transaction Fix

**Input (complex medical equipment description):**
```
"SU-1000523"|^|"Net 30"|^|"United States"|^|"325-05050B
Nursing Anne Manikin Dark
1 Adult, Female, Full-Body Manikin, 1
Female Multi-Venous IV Training Arm-
Left, 1 Female Blood Pressure
Training Arm-Right, 1 Blood Pressure
Cuff, 1 Male Genitalia, 1 Female
Genitalia, 3 Urinary Connector Valves,
3 Anal Connector Valves, 4 Clamps, 1
100cc Slip Tip Syringe, 1 Can Manikin
Lubricant, 1 Hospital Gown and
Includes Gift Box"|^|"Lab Equipment"
```

**Output (fully reconstructed):**
```
"SU-1000523"|^|"Net 30"|^|"United States"|^|"325-05050B Nursing Anne Manikin Dark 1 Adult, Female, Full-Body Manikin, 1 Female Multi-Venous IV Training Arm- Left, 1 Female Blood Pressure Training Arm-Right, 1 Blood Pressure Cuff, 1 Male Genitalia, 1 Female Genitalia, 3 Urinary Connector Valves, 3 Anal Connector Valves, 4 Clamps, 1 100cc Slip Tip Syringe, 1 Can Manikin Lubricant, 1 Hospital Gown and Includes Gift Box"|^|"Lab Equipment"
```

## 🎯 Special Case Handling

The application correctly handles special cases such as:

1. **Embedded quotes**: `"ADB will apply SSL Certificates for WGU Complio "Splash pages""`
2. **Inch measurements**: `"CAP-GOWN PKG ULTRA NAVY 60""` → `"CAP-GOWN PKG ULTRA NAVY 60 inches"`
3. **Multiple spaces**: Converts `"Multiple   spaces"` to `"Multiple spaces"`
4. **Tabs in text**: Replaces tabs with spaces for cleaner output
5. **Complex multi-line descriptions**: Medical equipment, software specifications, detailed product descriptions
6. **Very long transactions**: Handles descriptions spanning up to 25 lines

## 🔒 Production Features

- **Session Management**: Secure user isolation and file handling
- **Error Recovery**: Graceful handling of processing failures
- **Resource Management**: Automatic cleanup and maintenance
- **Scalability**: Supports multiple concurrent users
- **Logging**: Comprehensive error tracking and debugging information

## 📞 Support

For issues or questions:
1. Check the error logs generated during processing
2. Review the error transactions file for problematic data
3. Ensure your input file format matches the expected structure
4. Verify delimiter and qualifier settings match your data format 