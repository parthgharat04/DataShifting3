#!/usr/bin/env python3

try:
    # Import the fix_embedded_quotes function from data_shifting.py
    from data_shifting import fix_embedded_quotes
    print("Successfully imported fix_embedded_quotes")
except Exception as e:
    print(f"Error importing function: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

def main():
    try:
        # Test cases
        test_cases = [
            '"CAP-GOWN PKG ULTRA NAVY 60""|^|',
            '"NURSING GOWN PKG 54""|^|',
            '"MONITOR DELL 32""|^|',
            '|^|"CAP-GOWN PKG ULTRA NAVY 60""|^|',
            '"ADB will apply SSL Certificates for WGU Complio "Splash pages""|^|'
        ]
        
        delimiter = "|^|"
        qualifier = '"'
        
        print("Testing fix_embedded_quotes function for inches pattern")
        print("-" * 50)
        
        for i, test_case in enumerate(test_cases, 1):
            try:
                fixed = fix_embedded_quotes(test_case, delimiter, qualifier)
                print(f"Test {i}:")
                print(f"  Original: {test_case}")
                print(f"     Fixed: {fixed}")
                print(f"  Changed: {'Yes' if test_case != fixed else 'No'}")
                print()
            except Exception as e:
                print(f"Error in test {i}: {e}")
                import traceback
                traceback.print_exc()
        
        # Also test with a complete line
        complete_line = '"Value1"|^|"CAP-GOWN PKG ULTRA NAVY 60""|^|"Regular value"'
        try:
            fixed_line = fix_embedded_quotes(complete_line, delimiter, qualifier)
            print("Complete line test:")
            print(f"  Original: {complete_line}")
            print(f"     Fixed: {fixed_line}")
            print(f"  Changed: {'Yes' if complete_line != fixed_line else 'No'}")
        except Exception as e:
            print(f"Error in complete line test: {e}")
            import traceback
            traceback.print_exc()
    except Exception as e:
        print(f"Error in main: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 