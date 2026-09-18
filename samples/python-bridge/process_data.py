"""
process_data.py - Python side of the IBM RPA Python bridge.

HOW IBM RPA CALLS PYTHON (official pattern from IBM Community):
  - IBM RPA uses runDOSCommand to invoke python.exe
  - runDOSCommand captures ALL stdout as a single String (not a List)
  - To return values back to WAL, use print()
  - WAL then uses getRegex to extract specific values from the printed output

RESTRICTION:
  - Only String output is returned - never a List
  - Parameters must be passed as text/numeric command-line arguments

SOLUTION (this script):
  - Accepts a comma-separated list of items as argv[1]
  - Accepts an operation name as argv[2]
  - Prints a single prefixed, comma-delimited result line:
      RESULT:ALICE,BOB,CHARLIE,DIANA
  - WAL uses getRegex with capture groups to parse each item by position

Usage (called from WAL via runDOSCommand):
    python process_data.py Alice,Bob,Charlie,Diana UPPER

Output (single stdout line):
    RESULT:ALICE,BOB,CHARLIE,DIANA
"""

import sys


def main():
    if len(sys.argv) < 3:
        print("ERROR: Expected 2 arguments: <comma_separated_items> <operation>")
        sys.exit(1)

    # argv[1]: comma-separated input items  e.g. "Alice,Bob,Charlie,Diana"
    items = sys.argv[1].split(",")
    operation = sys.argv[2].upper()

    if operation == "UPPER":
        result = [item.strip().upper() for item in items]
    elif operation == "LOWER":
        result = [item.strip().lower() for item in items]
    elif operation == "REVERSE":
        result = [item.strip() for item in reversed(items)]
    elif operation == "SORT":
        result = sorted(item.strip() for item in items)
    else:
        print(f"ERROR: Unknown operation '{operation}'")
        sys.exit(1)

    # Print a single prefixed comma-delimited line.
    # WAL's getRegex will extract each item by capture-group position.
    # The RESULT: prefix makes the line easy to identify in the raw output.
    print("RESULT:" + ",".join(result))


if __name__ == "__main__":
    main()
