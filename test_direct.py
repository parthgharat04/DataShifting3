from data_shifting import count_columns, clean_qualified_content

# Test our solution directly with detailed output

# Test parameters
delimiter = '|^|'
qualifier = '"'

# Test cases
splash_case = '"1"|^|"ADB will apply SSL Certificates for WGU Complio "Splash pages""|^|"Paid"'
inches_case = '"2"|^|"CAP-GOWN PKG ULTRA NAVY 57""|^|"Paid"'

def analyze_string(description, test_string):
    print(f"\n--- {description} ---")
    print(f"Input: {test_string}")
    
    # Count columns
    columns = count_columns(test_string, delimiter, qualifier)
    print(f"Column count: {columns}")
    
    # Clean content
    cleaned = clean_qualified_content(test_string, delimiter, qualifier)
    print(f"Cleaned: {cleaned}")
    
    # Verify column count in cleaned string
    cleaned_columns = count_columns(cleaned, delimiter, qualifier)
    print(f"Column count after cleaning: {cleaned_columns}")
    
    # Check if certain patterns exist
    if '"Splash pages"' in test_string:
        embedded_preserved = '"Splash pages"' in cleaned
        print(f"Embedded 'Splash pages' quotes preserved: {embedded_preserved}")
    
    if '57"' in test_string:
        inches_preserved = '57"' in cleaned 
        print(f"Embedded inches symbol preserved: {inches_preserved}")

# Analyze the test cases
analyze_string("Splash Pages Case", splash_case)
analyze_string("Inches Symbol Case", inches_case)

# For deeper debugging, trace through character by character
def trace_processing(description, test_string):
    print(f"\n--- Character-by-Character Tracing for {description} ---")
    in_quote = False
    position = 0
    
    while position < len(test_string):
        char = test_string[position]
        context = test_string[max(0, position-10):min(len(test_string), position+10)]
        context_with_marker = f"{context[:min(10, position)]}[{char}]{context[min(10, position)+1:]}"
        
        # Check for qualifier
        if test_string[position:position+len(qualifier)] == qualifier:
            if not in_quote:
                print(f"Position {position}: Found opening qualifier at: ...{context_with_marker}...")
                in_quote = True
                position += len(qualifier)
            else:
                # Check if this is an end quote
                next_pos = position + len(qualifier)
                while next_pos < len(test_string) and test_string[next_pos].isspace():
                    next_pos += 1
                
                if next_pos >= len(test_string) or test_string[next_pos:next_pos+len(delimiter)] == delimiter:
                    print(f"Position {position}: Found closing qualifier at: ...{context_with_marker}...")
                    in_quote = False
                    position = next_pos
                    
                    if next_pos < len(test_string) and test_string[next_pos:next_pos+len(delimiter)] == delimiter:
                        print(f"Position {next_pos}: Found delimiter after closing qualifier")
                        position += len(delimiter)
                else:
                    print(f"Position {position}: Found embedded qualifier at: ...{context_with_marker}...")
                    position += len(qualifier)
        elif not in_quote and test_string[position:position+len(delimiter)] == delimiter:
            print(f"Position {position}: Found delimiter outside quotes: ...{context_with_marker}...")
            position += len(delimiter)
        else:
            if in_quote:
                print(f"Position {position}: Regular character inside quotes: ...{context_with_marker}...")
            else:
                print(f"Position {position}: Regular character outside quotes: ...{context_with_marker}...")
            position += 1

# Do detailed tracing if needed
print("\nDetailed tracing of the problematic cases:")
trace_processing("Splash Pages Case", splash_case)
trace_processing("Inches Symbol Case", inches_case) 