import re
import argparse
import sys
from pathlib import Path
import tempfile
import os

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Correct data shifting in text files.')
    parser.add_argument('input_file', type=str, help='Path to the input text file', nargs='?')
    parser.add_argument('output_file', type=str, help='Path to the output corrected file', nargs='?')
    parser.add_argument('--error_file', type=str, help='Path to the error log file (default: input_file_errors.log)')
    parser.add_argument('--error_transactions_file', type=str, help='Path to save error transactions (default: input_file_error_transactions.txt)')
    parser.add_argument('--delimiter', type=str, default='|^|', help='Column delimiter (default: |^|)')
    parser.add_argument('--qualifier', type=str, default='"', help='Text qualifier (default: ")')
    parser.add_argument('--test', action='store_true', help='Run built-in tests instead of processing files')
    return parser.parse_args()

def detect_delimiter_and_qualifier(first_line):
    """Try to automatically detect delimiter and text qualifier from the first line."""
    # Common delimiters to check
    delimiters = ['|^|', ',', '|', '\t', ';']
    qualifiers = ['"', "'"]
    
    detected_delimiter = None
    detected_qualifier = None
    
    # Try to detect delimiter
    for delimiter in delimiters:
        if delimiter in first_line:
            detected_delimiter = delimiter
            break
    
    # Try to detect qualifier
    for qualifier in qualifiers:
        if qualifier in first_line:
            detected_qualifier = qualifier
            break
            
    return detected_delimiter, detected_qualifier

def fix_embedded_quotes(line, delimiter, qualifier):
    """
    Enhanced fix for embedded quotes in specific problem patterns.
    
    1. For measurements with inch marks: 
       Example: "CAP-GOWN PKG ULTRA NAVY 60"" -> "CAP-GOWN PKG ULTRA NAVY 60 inches"
       When we see pattern like number+qualifier+qualifier+delimiter, replace with number+" inches"
    
    2. For other embedded quotes:
       Example: "ADB will apply SSL Certificates for WGU Complio "Splash pages"" 
       This requires different handling to keep the embedded quotes in context
    
    3. For complex patterns like "9-1/2" or "5" W x 9.5" H x 2.5" D"
    """
    result = line
    
    # Pattern 1: text qualifier + text qualifier + delimiter
    # Example: "CAP-GOWN PKG ULTRA NAVY 60""|^|
    double_quote_pattern = qualifier + qualifier + delimiter
    
    # Pattern 2: text qualifier + text qualifier at end of line (for multi-line cases)
    # Example: "Crosby Pentagon 9-1/2" (at end of line)
    double_quote_end_pattern = qualifier + qualifier + '$'
    
    # Pattern 3: Complex inch measurements like "9-1/2" or "5" W x 9.5" H x 2.5" D"
    # This regex looks for patterns like: number + optional fraction + " + optional space + letter/number
    inch_pattern = r'(\d+(?:-\d+/\d+)?)"(\s*[A-Za-z0-9]|\s*$)'
    
    # Apply inch pattern fixes first
    result = re.sub(inch_pattern, r'\1 inches\2', result)
    
    # Find all occurrences of double quote + delimiter pattern
    pos = 0
    while True:
        pos = result.find(double_quote_pattern, pos)
        if pos == -1:
            break
            
        # Now we need to check if there's content before this pattern
        # First, find the previous delimiter or start of string
        prev_delim_pos = result.rfind(delimiter, 0, pos)
        if prev_delim_pos == -1:
            prev_delim_pos = 0
        else:
            prev_delim_pos += len(delimiter)
            
        # Check if there's a qualifier after the previous delimiter
        if result[prev_delim_pos:prev_delim_pos+len(qualifier)] == qualifier:
            # There's a qualifier, so we have a proper field
            field_start = prev_delim_pos + len(qualifier)
            
            # If there's content between the start qualifier and the double quotes at pos
            if pos > field_start:
                # Check if the character before the double quotes is a digit
                # This would suggest it's a measurement in inches
                if pos > 0 and result[pos-1].isdigit():
                    # For measurements like "60""
                    result = result[:pos] + " inches" + result[pos+len(qualifier):]
                    # Adjust pos to account for the replacement
                    pos += len(" inches")
                else:
                    # For other embedded quotes like "Splash pages""
                    # We need a different approach - keep the quotes but ensure they're processed correctly
                    # Skip this double quote for now as it will be handled in the main processing functions
                    pos += len(qualifier)
            else:
                # Move past this occurrence
                pos += len(qualifier)
        else:
            # Move past this occurrence
            pos += len(double_quote_pattern)
    
    # Handle double quotes at end of line (multi-line cases)
    if result.endswith(qualifier + qualifier):
        # Find the last single quote before the double quotes
        last_single_quote = result.rfind(qualifier, 0, len(result) - len(qualifier))
        if last_single_quote != -1:
            # Check if there's content between the last single quote and the double quotes
            content_between = result[last_single_quote + len(qualifier):-len(qualifier)]
            if content_between.strip():
                # This is likely an incomplete field that continues on next line
                # Replace the double quotes with a single quote to maintain field integrity
                result = result[:-len(qualifier)]
    
    return result

def count_columns(line, delimiter, qualifier):
    """
    Enhanced column counting that better handles embedded quotes and multi-line scenarios.
    """
    # Apply special fix for embedded quotes like inches marks
    fixed_line = fix_embedded_quotes(line, delimiter, qualifier)
    
    # Enhanced column counting logic
    in_quoted_field = False
    current_pos = 0
    column_count = 1  # Start with 1 for the first column
    
    while current_pos < len(fixed_line):
        # Check for qualifier
        if fixed_line[current_pos:current_pos+len(qualifier)] == qualifier:
            if not in_quoted_field:
                # Start of quoted field
                in_quoted_field = True
                current_pos += len(qualifier)
            else:
                # Potential end of quoted field
                # Look ahead to see if this is actually a field boundary
                next_pos = current_pos + len(qualifier)
                
                # Skip any whitespace after the quote
                while next_pos < len(fixed_line) and fixed_line[next_pos].isspace():
                    next_pos += 1
                
                # Check if followed by delimiter or end of line
                if next_pos >= len(fixed_line) or fixed_line[next_pos:next_pos+len(delimiter)] == delimiter:
                    # This is indeed the end of the quoted field
                    in_quoted_field = False
                    current_pos = next_pos
                    
                    # If not at the end, then we've found a new column
                    if next_pos < len(fixed_line) and fixed_line[next_pos:next_pos+len(delimiter)] == delimiter:
                        column_count += 1
                        current_pos += len(delimiter)
                else:
                    # This is an embedded quote, not a closing quote
                    current_pos += len(qualifier)
        elif not in_quoted_field and fixed_line[current_pos:current_pos+len(delimiter)] == delimiter:
            # Found a delimiter outside quoted field - new column
            column_count += 1
            current_pos += len(delimiter)
        else:
            # Regular character, just move forward
            current_pos += 1
            
    return column_count

def is_line_complete(line, delimiter, qualifier):
    """
    Enhanced function to check if a line has complete quoted fields.
    Returns True if all quotes are balanced, False otherwise.
    """
    in_quote = False
    current_pos = 0
    
    while current_pos < len(line):
        if line[current_pos:current_pos+len(qualifier)] == qualifier:
            if not in_quote:
                # Start of quoted field
                in_quote = True
                current_pos += len(qualifier)
            else:
                # Potential end of quoted field
                next_pos = current_pos + len(qualifier)
                
                # Skip whitespace
                while next_pos < len(line) and line[next_pos].isspace():
                    next_pos += 1
                
                # If we're at end of line or next char is delimiter, this is a closing quote
                if next_pos >= len(line) or line[next_pos:next_pos+len(delimiter)] == delimiter:
                    in_quote = False
                # Otherwise it's just an embedded quote
                current_pos += len(qualifier)
        else:
            current_pos += 1
    
    return not in_quote

def should_combine_lines(current_line, next_line, delimiter, qualifier):
    """
    Enhanced logic to determine if two lines should be combined.
    This handles cases where the first line ends with an incomplete quoted field.
    """
    # Check if current line ends with an incomplete quoted field
    current_ends_with_quote = current_line.rstrip().endswith(qualifier)
    
    # Check if next line starts with content that could be part of a quoted field
    next_starts_with_content = next_line.strip() and not next_line.strip().startswith(qualifier)
    
    # Check if current line has fewer columns than expected (indicating incomplete transaction)
    current_columns = count_columns(current_line, delimiter, qualifier)
    
    # If current line ends with a quote and next line has content, likely should combine
    if current_ends_with_quote and next_starts_with_content:
        return True
    
    # If current line has very few columns, it's likely incomplete
    if current_columns < 10:  # Arbitrary threshold - adjust as needed
        return True
    
    return False

def fix_data_shifting(input_path, output_path, error_path=None, error_transactions_path=None, delimiter=None, qualifier=None):
    """
    Final enhanced fix_data_shifting function with robust multi-line detection and embedded quote handling.
    """
    # Initialize error log list and error transactions
    error_logs = []
    error_transactions = []
    
    try:
        with open(input_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except UnicodeDecodeError:
        # Try with a different encoding if utf-8 fails
        try:
            with open(input_path, 'r', encoding='latin-1') as file:
                lines = file.readlines()
        except Exception as e:
            error_msg = f"Error reading input file: {str(e)}"
            print(error_msg)
            error_logs.append(error_msg)
            if error_path:
                write_error_log(error_path, error_logs)
            return
    
    if not lines:
        error_msg = "Input file is empty."
        print(error_msg)
        error_logs.append(error_msg)
        if error_path:
            write_error_log(error_path, error_logs)
        return
    
    # Strip newlines from the header line
    header_line = lines[0].strip()
    
    # Add header to error transactions
    if error_transactions_path:
        error_transactions.append(header_line)
    
    # Auto-detect delimiter and qualifier if not provided
    if delimiter is None or qualifier is None:
        detected_delimiter, detected_qualifier = detect_delimiter_and_qualifier(header_line)
        delimiter = delimiter or detected_delimiter or '|^|'  # Default to |^| if not detected
        qualifier = qualifier or detected_qualifier or '"'    # Default to " if not detected
    
    print(f"Using delimiter: '{delimiter}' and qualifier: '{qualifier}'")
    
    # Count the number of headers
    header_count = count_columns(header_line, delimiter, qualifier)
    print(f"Detected {header_count} columns in header")
    
    # Process the data lines
    corrected_lines = [header_line]
    uncorrectable_lines = []
    i = 1
    
    while i < len(lines):
        current_line = lines[i].rstrip('\r\n')
        
        # Skip empty lines
        if not current_line.strip():
            i += 1
            continue
        
        # Count columns in the current line
        column_count = count_columns(current_line, delimiter, qualifier)
        
        # If the column count matches header count, add the line as is
        if column_count == header_count:
            corrected_lines.append(current_line)
            i += 1
        else:
            # Enhanced multi-line detection using multiple strategies
            line_complete = is_line_complete(current_line, delimiter, qualifier)
            should_combine = False
            
            # Check if we should combine with next line
            if i + 1 < len(lines):
                next_line = lines[i + 1].rstrip('\r\n')
                should_combine = should_combine_lines(current_line, next_line, delimiter, qualifier)
            
            if (not line_complete or should_combine) and i + 1 < len(lines):
                # Start building a combined line
                combined_line = current_line
                next_index = i + 1
                original_lines = [f"Line {i+1}: {current_line}"]
                error_transaction_lines = [current_line]
                
                # Continue adding lines until we have matching column count or no more lines
                max_combine_attempts = 10  # Prevent infinite loops
                combine_attempts = 0
                
                while (next_index < len(lines) and 
                       count_columns(combined_line, delimiter, qualifier) != header_count and
                       combine_attempts < max_combine_attempts):
                    
                    next_line = lines[next_index].rstrip('\r\n')
                    original_lines.append(f"Line {next_index+1}: {next_line}")
                    error_transaction_lines.append(next_line)
                    
                    # Replace newline with space for readability
                    combined_line += ' ' + next_line
                    
                    # Check if we now have all columns
                    if count_columns(combined_line, delimiter, qualifier) == header_count:
                        break
                    
                    next_index += 1
                    combine_attempts += 1
                
                # If we now have the correct count, consider it fixed
                if count_columns(combined_line, delimiter, qualifier) == header_count:
                    corrected_lines.append(combined_line)
                    error_logs.append(f"Fixed multi-line transaction at lines {i+1}-{next_index+1}:")
                    error_logs.extend(original_lines)
                    error_logs.append(f"Combined into: {combined_line}")
                    error_logs.append("-" * 50)
                else:
                    # Couldn't fix it
                    error_msg = f"Error: Could not fix multi-line transaction starting at line {i+1} (has {column_count} columns, expected {header_count})"
                    print(error_msg)
                    error_logs.append(error_msg)
                    error_logs.extend(original_lines)
                    error_logs.append("-" * 50)
                    uncorrectable_lines.append((i+1, current_line))
                    corrected_lines.append(current_line)  # Add as-is, since we can't fix it
                    
                    # Add to error transactions file
                    error_transactions.extend(error_transaction_lines)
                
                i = next_index + 1
            else:
                # Single line with incorrect columns that can't be fixed
                error_msg = f"Error: Line {i+1} has {column_count} columns (expected {header_count})"
                print(error_msg)
                error_logs.append(error_msg)
                error_logs.append(f"Line {i+1}: {current_line}")
                error_logs.append("-" * 50)
                uncorrectable_lines.append((i+1, current_line))
                corrected_lines.append(current_line)  # Add as-is
                
                # Add to error transactions file
                error_transactions.append(current_line)
                
                i += 1
    
    # Clean the content of each line (handle newlines within quoted text)
    final_lines = []
    for line in corrected_lines:
        # Process the line to fix any issues with newlines in quoted fields
        cleaned_line = clean_qualified_content(line, delimiter, qualifier)
        final_lines.append(cleaned_line)
    
    # Write the corrected data to the output file
    try:
        with open(output_path, 'w', encoding='utf-8') as out_file:
            for i, line in enumerate(final_lines):
                # Add newline character except for the last line
                if i < len(final_lines) - 1:
                    out_file.write(line + '\n')
                else:
                    out_file.write(line)
        
        print(f"Processed {len(lines)} input lines into {len(final_lines)} corrected lines")
        print(f"Corrected data written to {output_path}")
        
        if uncorrectable_lines:
            print(f"Found {len(uncorrectable_lines)} lines that could not be fully corrected")
        
        # Write error log if there are any errors and an error path is provided
        if error_logs and error_path:
            write_error_log(error_path, error_logs)
            print(f"Error log written to {error_path}")
            
        # Write error transactions if there are any and path is provided
        if len(error_transactions) > 1 and error_transactions_path:  # > 1 because header is always included
            write_error_transactions(error_transactions_path, error_transactions)
            print(f"Error transactions written to {error_transactions_path}")
            
    except Exception as e:
        error_msg = f"Error writing output file: {str(e)}"
        print(error_msg)
        error_logs.append(error_msg)
        if error_path:
            write_error_log(error_path, error_logs)

def clean_qualified_content(line, delimiter, qualifier):
    """
    Enhanced cleaning function that better handles embedded quotes and complex patterns.
    """
    # Apply special fix for embedded quotes like inches marks
    fixed_line = fix_embedded_quotes(line, delimiter, qualifier)
    
    cleaned_parts = []
    current_pos = 0
    in_quote = False
    current_field = ""
    field_content = ""
    
    while current_pos < len(fixed_line):
        if fixed_line[current_pos:current_pos+len(qualifier)] == qualifier:
            if not in_quote:
                # Starting a quoted field
                in_quote = True
                current_field += qualifier
                field_content = ""  # Reset field content for new field
                current_pos += len(qualifier)
            else:
                # Check if this is a real end quote or just an embedded quote
                next_pos = current_pos + len(qualifier)
                
                # Skip whitespace
                while next_pos < len(fixed_line) and fixed_line[next_pos].isspace():
                    next_pos += 1
                
                # If we're at end of line or next char is delimiter, this is a closing quote
                if next_pos >= len(fixed_line) or fixed_line[next_pos:next_pos+len(delimiter)] == delimiter:
                    # End of quoted field - now process the field content before adding it
                    
                    # Process the field content:
                    # 1. Replace tabs with spaces
                    processed_content = field_content.replace('\t', ' ')
                    
                    # 2. Replace newlines with spaces (already handled in the character-by-character processing)
                    
                    # 3. Trim multiple consecutive spaces to a single space
                    processed_content = re.sub(r' +', ' ', processed_content)
                    
                    # Add the processed content and closing qualifier
                    current_field += processed_content + qualifier
                    
                    # End of quoted field
                    in_quote = False
                    current_pos = next_pos
                    
                    # If there's a delimiter here, add it
                    if next_pos < len(fixed_line) and fixed_line[next_pos:next_pos+len(delimiter)] == delimiter:
                        cleaned_parts.append(current_field)
                        current_field = ""
                        cleaned_parts.append(delimiter)
                        current_pos += len(delimiter)
                    else:
                        # End of line after quote
                        cleaned_parts.append(current_field)
                        current_field = ""
                else:
                    # This is an embedded quote, not a closing quote
                    field_content += qualifier  # Add the embedded quote to field content
                    current_pos += len(qualifier)
        elif not in_quote and fixed_line[current_pos:current_pos+len(delimiter)] == delimiter:
            # Delimiter outside quotes
            if current_field:
                cleaned_parts.append(current_field)
                current_field = ""
            cleaned_parts.append(delimiter)
            current_pos += len(delimiter)
        else:
            # Regular character
            if in_quote:
                if fixed_line[current_pos] == '\n' or fixed_line[current_pos] == '\r':
                    # Replace newlines in quoted text with space
                    field_content += ' '
                elif fixed_line[current_pos] == '\t':
                    # Replace tabs in quoted text with space (will be further processed at end)
                    field_content += ' '
                else:
                    # Add regular character to field content
                    field_content += fixed_line[current_pos]
            else:
                # Outside quotes, add as is
                current_field += fixed_line[current_pos]
            current_pos += 1
    
    # Add any remaining field content
    if current_field:
        cleaned_parts.append(current_field)
    
    return ''.join(cleaned_parts)

def write_error_log(error_path, error_logs):
    """Write error logs to the specified file."""
    try:
        with open(error_path, 'w', encoding='utf-8') as error_file:
            for error in error_logs:
                error_file.write(error + '\n')
    except Exception as e:
        print(f"Error writing error log: {e}")

def write_error_transactions(error_transactions_path, error_transactions):
    """Write error transactions to the specified file."""
    try:
        with open(error_transactions_path, 'w', encoding='utf-8') as error_file:
            for transaction in error_transactions:
                error_file.write(transaction + '\n')
    except Exception as e:
        print(f"Error writing error transactions: {e}")

def run_tests():
    """Run built-in tests to verify the functionality."""
    print("Running built-in tests...")
    
    # Test 1: Basic embedded quotes
    test_line = '"Test "embedded" quotes"'
    result = fix_embedded_quotes(test_line, '|^|', '"')
    print(f"Test 1 - Basic embedded quotes: {result}")
    
    # Test 2: Inch measurements
    test_line = '"Product 9-1/2" x 5" x 2.5" D"'
    result = fix_embedded_quotes(test_line, '|^|', '"')
    print(f"Test 2 - Inch measurements: {result}")
    
    # Test 3: Complex pattern
    test_line = '"Crosby Pentagon 9-1/2" This is a description with 5" W x 9.5" H x 2.5" D"'
    result = fix_embedded_quotes(test_line, '|^|', '"')
    print(f"Test 3 - Complex pattern: {result}")
    
    # Test 4: Column counting
    test_line = '"Field1"|^|"Field2"|^|"Field3"'
    count = count_columns(test_line, '|^|', '"')
    print(f"Test 4 - Column counting: {count}")
    
    # Test 5: Line combination logic
    current_line = '"Field1"|^|"Field2"|^|"Incomplete'
    next_line = 'description continues here"|^|"Field3"'
    should_combine = should_combine_lines(current_line, next_line, '|^|', '"')
    print(f"Test 5 - Should combine lines: {should_combine}")
    
    print("Tests completed!")

if __name__ == '__main__':
    args = parse_args()
    
    if args.test:
        run_tests()
    elif args.input_file and args.output_file:
        fix_data_shifting(
            args.input_file, 
            args.output_file, 
            args.error_file, 
            args.error_transactions_file,
            args.delimiter, 
            args.qualifier
        )
    else:
        print("Usage: python data_shifting_final.py input_file output_file [options]")
        print("Or run tests: python data_shifting_final.py --test")
