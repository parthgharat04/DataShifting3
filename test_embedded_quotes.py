import sys
from data_shifting import count_columns, clean_qualified_content

# Test the specific examples with embedded quotes
splash_pages_example = '"SU-1005692"|^|""|^|"United States of America"|^|"CO"|^|"Denver"|^|"80202"|^|""|^|""|^|"SUPPLIER_INVOICE_LINE-3-481715"|^|"2025-02-05-08:00"|^|"0"|^|""|^|"PO-100034982 - Line 1"|^|""|^|"WGU Corporation"|^|"WGUCORP"|^|"Managed"|^|"All Cost Centers"|^|"1220 Enterprise Systems (IT Operations)"|^|"American DataBank, LLC"|^|"PO-100034982"|^|"2025-01-30T09:08:31.573-08:00"|^|"Approved"|^|""|^|"2025-01-30T12:40:14.165-08:00"|^|"2025-01-10-08:00"|^|"SI-1134218"|^|"2501999"|^|"2025-01-10-08:00"|^|"ADB Complio SSL CERTS SPLASH PAGES"|^|"ADB will apply SSL Certificates for WGU Complio "Splash pages""|^|"Software"|^|"2400"|^|"0"|^|"0"|^|"0"|^|""|^|""|^|""|^|""|^|""|^|""|^|""|^|"2400"|^|"Paid"'

inches_example = '"SU-1014309"|^|""|^|"United States of America"|^|"TX"|^|"Austin"|^|"78745"|^|""|^|""|^|"SUPPLIER_INVOICE_LINE-3-482872"|^|"2025-02-06-08:00"|^|"2"|^|"Each"|^|"PO-100034988 - Line 6"|^|""|^|"Western Governors University"|^|"WGU"|^|"Managed"|^|"Student Support Services and Operations"|^|"1335 WGU Commencements"|^|"Commemorative Brands Inc"|^|"PO-100034988"|^|"2025-01-30T23:16:59.549-08:00"|^|"Approved"|^|""|^|"2025-02-03T13:08:45.677-08:00"|^|"2025-01-28-08:00"|^|"SI-1135627"|^|"374491"|^|"2025-01-28-08:00"|^|"CAP-GOWN PKG ULTRA NAVY 57""|^|""|^|"Commencement Goods"|^|"34"|^|"0"|^|"0"|^|"0"|^|""|^|""|^|""|^|""|^|""|^|""|^|""|^|"807"|^|"Paid"'

# Simplified test cases
splash_case = '"1"|^|"ADB will apply SSL Certificates for WGU Complio "Splash pages""|^|"Paid"'
inches_case = '"2"|^|"CAP-GOWN PKG ULTRA NAVY 57""|^|"Paid"'

# Test parameters
delimiter = '|^|'
qualifier = '"'

# Function to test and display results
def test_case(description, test_line, expected_columns):
    print(f"\nTesting: {description}")
    columns = count_columns(test_line, delimiter, qualifier)
    cleaned = clean_qualified_content(test_line, delimiter, qualifier)
    print(f"Column count: {columns} (Expected: {expected_columns})")
    print(f"Original: {test_line}")
    print(f"Cleaned: {cleaned}")
    
    if columns == expected_columns:
        print("PASSED: Column count is correct")
    else:
        print("FAILED: Column count is incorrect")
        
    # Test embedded quotes preservation
    if test_line.find('"Splash pages"') > 0 and cleaned.find('"Splash pages"') > 0:
        print("PASSED: Embedded 'Splash pages' quotes preserved")
    elif test_line.find('57"') > 0 and cleaned.find('57"') > 0:
        print("PASSED: Embedded '57\"' preserved")

# Run tests
print("=============== EMBEDDED QUOTES TESTING ===============")
test_case("Splash pages full example", splash_pages_example, 46)
test_case("Inches full example", inches_example, 46)
test_case("Simplified splash pages case", splash_case, 3)
test_case("Simplified inches case", inches_case, 3)
print("=====================================================") 