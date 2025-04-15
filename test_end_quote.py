from data_shifting import count_columns, clean_qualified_content

def test_end_quote_handling():
    # Test data with quote at the end of line
    header = 'Supplier ID|^|Payment Terms|^|Status'
    data_line = '"SU-1001832"|^|"Net 30"|^|"Paid"'
    
    # Test with embedded quotes in middle of data
    embedded_quote_line = '"SU-1001832"|^|"Net 30"|^|"12" monitor is Paid"'
    
    # Test with a problematic line from the user example
    problem_line = '"SU-1000115"|^|"Net 30"|^|"United States of America"|^|"UT"|^|"South Salt Lake CIty"|^|"84119"|^|""|^|""|^|"SUPPLIER_INVOICE_LINE-3-479261"|^|"2025-01-30-08:00"|^|"100"|^|"Each"|^|"PO-100033234 - Line 3"|^|""|^|"Western Governors University"|^|"WGU"|^|"Managed"|^|"Marketing"|^|"1307 Referral and Direct Mail Marketing"|^|"BrightPoint Creative LLC"|^|"PO-100033234"|^|"2024-10-28T14:57:20.880-07:00"|^|"Approved"|^|""|^|"2025-01-30T09:23:12.386-08:00"|^|"2025-01-01-08:00"|^|"SI-1135084"|^|"18964"|^|"2024-09-16-07:00"|^|"Foam fingers for referral marketing at Fort Worth commencement\n17" Love Foam Hand Mitt;16.875 " X 15.875 " \nNavy Blue 2965u"|^|""|^|"Brand Health"|^|"706"|^|"0"|^|"0"|^|"0"|^|""|^|""|^|""|^|""|^|""|^|""|^|""|^|"1815.34"|^|"Paid"'
    
    # Expected results after cleaning
    expected_cleaned = '"SU-1000115"|^|"Net 30"|^|"United States of America"|^|"UT"|^|"South Salt Lake CIty"|^|"84119"|^|""|^|""|^|"SUPPLIER_INVOICE_LINE-3-479261"|^|"2025-01-30-08:00"|^|"100"|^|"Each"|^|"PO-100033234 - Line 3"|^|""|^|"Western Governors University"|^|"WGU"|^|"Managed"|^|"Marketing"|^|"1307 Referral and Direct Mail Marketing"|^|"BrightPoint Creative LLC"|^|"PO-100033234"|^|"2024-10-28T14:57:20.880-07:00"|^|"Approved"|^|""|^|"2025-01-30T09:23:12.386-08:00"|^|"2025-01-01-08:00"|^|"SI-1135084"|^|"18964"|^|"2024-09-16-07:00"|^|"Foam fingers for referral marketing at Fort Worth commencement 17" Love Foam Hand Mitt;16.875 " X 15.875 "  Navy Blue 2965u"|^|""|^|"Brand Health"|^|"706"|^|"0"|^|"0"|^|"0"|^|""|^|""|^|""|^|""|^|""|^|""|^|""|^|""|^|"1815.34"|^|"Paid"'
    
    delimiter = '|^|'
    qualifier = '"'
    
    # Test column counting
    header_count = count_columns(header, delimiter, qualifier)
    data_count = count_columns(data_line, delimiter, qualifier)
    embedded_count = count_columns(embedded_quote_line, delimiter, qualifier)
    problem_count = count_columns(problem_line, delimiter, qualifier)
    
    print(f"Header columns: {header_count}")
    print(f"Data line columns: {data_count}")
    print(f"Embedded quote line columns: {embedded_count}")
    print(f"Problem line columns: {problem_count}")
    
    # Test content cleaning
    cleaned_line = clean_qualified_content(problem_line, delimiter, qualifier)
    print("\nCleaned problem line:")
    print(cleaned_line)
    
    # Check if cleaning worked correctly
    if cleaned_line == expected_cleaned:
        print("\nSuccess! The problem line was cleaned correctly.")
    else:
        print("\nFailed! The problem line was not cleaned correctly.")
        print("\nDifferences:")
        
        # Show where the differences are
        for i, (a, b) in enumerate(zip(cleaned_line, expected_cleaned)):
            if a != b:
                print(f"Position {i}: '{a}' vs '{b}'")
                
                # Print some context
                start = max(0, i - 20)
                end = min(len(cleaned_line), i + 20)
                print(f"Context in cleaned: '...{cleaned_line[start:end]}...'")
                print(f"Context in expected: '...{expected_cleaned[start:end]}...'")
                break

if __name__ == "__main__":
    test_end_quote_handling() 