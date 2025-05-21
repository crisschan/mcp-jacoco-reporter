import argparse
import sys
from jacoco_reporter import JaCoCoReport # Assuming jacoco_reporter.py is in the same directory or PYTHONPATH

def main():
    parser = argparse.ArgumentParser(description="Generates a JSON report from a JaCoCo XML file.")
    parser.add_argument("jacoco_xmlreport_path", 
                        help="Path to the JaCoCo XML report file.")
    parser.add_argument("--covered-types", 
                        dest="covered_types_str",
                        type=str,
                        default="nocovered,partiallycovered,fullcovered",
                        help="Comma-separated string of coverage types to include. "
                             "Options: nocovered, partiallycovered, fullcovered. "
                             "Default: \"nocovered,partiallycovered,fullcovered\"")

    args = parser.parse_args()

    # Process covered_types
    if args.covered_types_str:
        covered_types = [ct.strip() for ct in args.covered_types_str.split(',') if ct.strip()]
        # Basic validation for allowed types
        allowed_types = {'nocovered', 'partiallycovered', 'fullcovered'}
        for ct in covered_types:
            if ct not in allowed_types:
                print(f"Error: Invalid covered type '{ct}'. Allowed types are {', '.join(allowed_types)}.", file=sys.stderr)
                sys.exit(1)
        if not covered_types: # If the string was all commas or empty
             covered_types = ['nocovered', 'partiallycovered', 'fullcovered']
    else: # Should not happen if default is set correctly, but as a fallback
        covered_types = ['nocovered', 'partiallycovered', 'fullcovered']


    try:
        reporter = JaCoCoReport(jacoco_xmlreport_path=args.jacoco_xmlreport_path, 
                                covered_types=covered_types)
        json_report = reporter.jacoco_to_json()
        print(json_report)
        sys.exit(0)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e: # Catches XML parsing errors or other value errors from JaCoCoReport
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
