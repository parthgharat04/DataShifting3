from data_shifting import count_columns, clean_qualified_content

# Test parameters
delimiter = '|^|'
qualifier = '"'

# Test cases
splash_case = '"1"|^|"ADB will apply SSL Certificates for WGU Complio "Splash pages""|^|"Paid"'
inches_case = '"2"|^|"CAP-GOWN PKG ULTRA NAVY 57""|^|"Paid"'

# Execute tests
print("Testing embedded quotes handling:")
print(f"1. Splash pages example: {splash_case}")
print(f"   Column count: {count_columns(splash_case, delimiter, qualifier)} (Expected: 3)")

print(f"2. Inches symbol example: {inches_case}")
print(f"   Column count: {count_columns(inches_case, delimiter, qualifier)} (Expected: 3)")

# Create and process a test file
import tempfile
import os
from pathlib import Path
from data_shifting import fix_data_shifting

try:
    # Create a temporary test file with our examples
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as test_file:
        # Write a simplified header and our example lines
        test_file.write('ID|^|Description|^|Status\n')
        test_file.write(splash_case + '\n')
        test_file.write(inches_case + '\n')
        test_file_path = test_file.name
        
    print("\nCreated test file with example data")
    
    # Create a temporary output file
    output_file_path = test_file_path + '_corrected.txt'
    
    # Process the file
    print("\nProcessing test file...")
    fix_data_shifting(
        Path(test_file_path), 
        Path(output_file_path), 
        delimiter=delimiter, 
        qualifier=qualifier
    )
    
    # Check if the output file was created and read its contents
    if os.path.exists(output_file_path):
        with open(output_file_path, 'r') as output_file:
            output_content = output_file.read()
        
        print("\nOutput file contents:")
        print(output_content)
        
        # Check if all lines are present in the output
        lines_count = output_content.count('\n') + 1
        print(f"\nOutput file has {lines_count} lines (Expected: 3)")
        
        # Clean up temporary files
        os.remove(test_file_path)
        os.remove(output_file_path)
    else:
        print("\nWarning: Output file was not created")

except Exception as e:
    print(f"\nError during test: {str(e)}") 